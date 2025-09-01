import datetime
import logging
import numbers
import os
from itertools import zip_longest
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Union

import h5py

logger = logging.getLogger(__name__)


def mca_data_to_spec_string(
    mca: Sequence[float],
    title: Optional[str] = None,
    filename: Optional[str] = None,
    date: Optional[Union[str, datetime.datetime, datetime.date]] = None,
    calibration: Optional[Sequence[float]] = None,
    detector_name: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> str:
    """Official file format specs: https://certif.com/downloads/css_docs/spec_man.pdf

    :param mca: MCA spectrum
    :param title: scan title
    :param filename: name by which the file will be created
    :param date: start date of the scan
    :param calibration: MCA calibration as the sequence [zero, gain, quad],
                        all of them optional so that
                        energy = zero + gain*channels + quad*channels^2
    :param detector_name: name of the MCA detector
    :param metadata: saved as comments
    :returns: SPEC serialized string
    """
    nchan_per_line = 16
    nchan_tot = len(mca)

    if title is None:
        title = "ct"
    if filename is None:
        filename = "unspecified"
    if detector_name is None:
        detector_name = "MCA0"
    date = spectimeformat(date)
    calib = [0, 1, 0]  # zero, gain, quad
    if calibration:
        if len(calibration) > 3:
            raise ValueError("MCA calibration requires 3 only coefficients")
        calib = [
            p if p is not None else pdefault
            for p, pdefault in zip_longest(calibration, calib)
        ]

    header = [f"#F {filename}", f"#D {date}", "", f"#S {title}", f"#D {date}"]
    if metadata:
        for k, v in metadata.items():
            header.append(f"#C {k} = {v}")
    header.append("#N 1")
    header.append(f"#@MCA {nchan_per_line}C")
    header.append(f"#@CHANN {nchan_tot} 0 {nchan_tot-1} 1")
    header.append(f"#@CALIB {' '.join(map(str, calib))}")
    header.append("#@MCA_NB 1")
    header.append(f"#L {detector_name}")

    mcastring = "\n".join(header)

    mcastring += "\n@A"
    if isinstance(mca[0], numbers.Integral):
        fmt = " %d"
    else:
        # fmt = " %.4f"
        fmt = " %.8g"
    for idx in range(0, nchan_tot, nchan_per_line):
        if idx + nchan_per_line - 1 < nchan_tot:
            for i in range(0, nchan_per_line):
                mcastring += fmt % mca[idx + i]
            if idx + nchan_per_line != nchan_tot:
                mcastring += "\\"
        else:
            for i in range(idx, nchan_tot):
                mcastring += fmt % mca[i]
        mcastring += "\n"
    return mcastring


def save_as_spec(filename: str, mca: Sequence[float], **kwargs) -> None:
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    content = mca_data_to_spec_string(mca, filename=filename, **kwargs)
    with open(filename, "w") as f:
        f.write(content)


class SpecScanData(NamedTuple):
    scan_name: str
    scan_title: str
    start_time: str
    scan_data: Dict[str, list]
    n_points: int

    @property
    def scan_number(self) -> int:
        return int(float(self.scan_name))

    @property
    def spec_title(self) -> str:
        return f"#S {self.scan_number} {self.scan_title}"


def extract_scan_data(
    h5file: h5py.File,
    scan_name: str,
    counter_names: List[str],
    acq_time: Optional[float],
) -> SpecScanData:
    """
    Extract counters and start_time for a single scan.
    Trim all counters to the same minimum length.
    Handle missing counters and timer/acq_time injection.
    """
    scan = h5file[scan_name]
    _ = scan["end_time"]
    measurement = scan["measurement"]
    force_counters = bool(counter_names)
    if not force_counters:
        counter_names = list(measurement)

    scan_data: Dict[str, list] = {}

    # Extract and format start_time
    dset = scan.get("start_time")
    if dset is not None:
        start_time = spectimeformat(dset[()])
    else:
        start_time = spectimeformat(None)
        logger.warning(f"Missing start_time for scan {scan_name}, using dummy time.")

    # Extract scan title
    dset = scan.get("title")
    if dset is not None:
        scan_title = asstr(dset[()])
    else:
        scan_title = "NISscan"

    # Extract counters
    for name in counter_names:
        if name in measurement:
            dset = measurement[name]
            if dset.ndim != 1:
                if force_counters:
                    logger.warning(
                        f"Counter '{name}' is not 1D in scan {scan_name}, skipping."
                    )
            else:
                scan_data[name] = dset[()]
        else:
            logger.warning(f"Counter '{name}' missing in scan {scan_name}, skipping.")

    # Determine minimum length and trim
    if scan_data:
        min_len = min(len(v) for v in scan_data.values())
        for k in scan_data.keys():
            scan_data[k] = scan_data[k][:min_len]
    else:
        logger.warning(f"No counters found for scan {scan_name}. Skipping this scan.")
        return SpecScanData(
            scan_name=scan_name,
            scan_title=scan_title,
            start_time=start_time,
            scan_data={},
            n_points=0,
        )

    # Handle acquisition time
    if "timer" in scan_data:
        scan_data["Seconds"] = scan_data.pop("timer")
    elif acq_time is not None:
        scan_data["Seconds"] = [acq_time] * min_len
    else:
        dset = h5file.get(f"/{scan_name}/scan_parameters/count_time")
        if dset is not None:
            acq_time = dset[()]
        else:
            acq_time = 0
            logger.warning(
                f"No 'acq_time' parameter or 'timer' counter found for scan {scan_name}, inserting zeros."
            )
        scan_data["Seconds"] = [acq_time] * min_len

    return SpecScanData(
        scan_name=scan_name,
        scan_title=scan_title,
        start_time=start_time,
        scan_data=scan_data,
        n_points=min_len,
    )


def scan_data_to_spec_string(scan: SpecScanData) -> str:
    lines = []
    lines.append(scan.spec_title)
    lines.append(f"#D {scan.start_time}")
    lines.append(f"#T {scan.scan_data['Seconds'][0]}  (Seconds)")

    keys = list(scan.scan_data)
    lines.append("#L " + "  ".join(keys))

    for k in range(scan.n_points):
        row = [str(scan.scan_data[name][k]) for name in keys]
        lines.append(" ".join(row) + "")

    lines.append("#C")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def save_as_spec2(filename: str, scans: List[SpecScanData]) -> str:
    """
    Write the extracted scan data into an ASCII file in SPEC format.
    """
    filename = os.path.abspath(filename)
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    existing_content = ""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            existing_content = f.read()
    else:
        with open(filename, "a") as f:
            date = spectimeformat(None)
            f.write(f"#F {filename}\n")
            f.write(f"#D {date}\n")
            f.write("\n")

    with open(filename, "a") as f:
        for scan in scans:
            if scan.n_points == 0:
                continue
            if scan.spec_title in existing_content:
                # Scan was already saved
                continue
            content = scan_data_to_spec_string(scan)
            f.write(content)
    return filename


def spectimeformat(date: Union[datetime.datetime, str, bytes, None]) -> str:
    if date is None:
        date = datetime.datetime.now()
    if not isinstance(date, datetime.datetime):
        date = datetime.datetime.fromisoformat(asstr(date))
    return date.strftime("%a %b %d %H:%M:%S %Y")


def asstr(data: Union[str, bytes]) -> Any:
    if isinstance(data, bytes):
        return data.decode()
    return data

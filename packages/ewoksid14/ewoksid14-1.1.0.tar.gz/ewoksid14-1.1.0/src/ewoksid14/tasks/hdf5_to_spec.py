import logging
import os
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Union

from blissdata.h5api import dynamic_hdf5
from ewokscore.task import Task

from .io import save_as_spec
from .io import spectimeformat

logger = logging.getLogger(__name__)


class Hdf5ToSpec(
    Task,
    input_names=["filename", "output_filename"],
    optional_input_names=[
        "scan_numbers",
        "retry_timeout",
        "retry_period",
        "mca_counter",
        "mca_calibration",
    ],
    output_names=["output_filenames"],
):
    """Convert Bliss HDF5 scans to SPEC files, one file per scan and only MCA data."""

    def run(self):
        filename: str = self.inputs.filename
        scan_numbers: Optional[Sequence[int]] = self.get_input_value(
            "scan_numbers", None
        )
        mca_counter: str = self.get_input_value("mca_counter", "Counts")
        retry_timeout: Optional[float] = self.get_input_value("retry_timeout", None)
        retry_period: Optional[float] = self.get_input_value("retry_period", 1)
        mca_calibration: Optional[float] = self.get_input_value("mca_calibration", None)

        output_filename: str = self.inputs.output_filename
        dirname = os.path.dirname(output_filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        output_filename, ext = os.path.splitext(output_filename)

        output_filenames = list()
        failed_scans = list()
        with dynamic_hdf5.File(
            filename, retry_timeout=retry_timeout, retry_period=retry_period
        ) as nxroot:
            if scan_numbers:
                scan_names = [f"{scannr}.1" for scannr in scan_numbers]
            else:
                scan_names = nxroot

            for scan_name in scan_names:
                scan_number = int(float(scan_name))

                try:
                    title = _asstr(nxroot[f"/{scan_name}/title"][()])
                    start_time = _asstr(nxroot[f"/{scan_name}/start_time"][()])
                    end_time = _asstr(nxroot[f"/{scan_name}/end_time"][()])
                    mca = nxroot[f"/{scan_name}/measurement/{mca_counter}"][-1]
                except Exception as e:
                    failed_scans.append(scan_number)
                    logger.error(
                        "Processing scan %s::/%s failed (%s)", filename, scan_name, e
                    )
                    continue

                scan_output_filename = f"{output_filename}_{scan_number:02d}{ext}"
                metadata = {"Finished": spectimeformat(end_time)}

                save_as_spec(
                    scan_output_filename,
                    mca,
                    title=f"{scan_number} {title}",
                    date=start_time,
                    detector_name=mca_counter,
                    metadata=metadata,
                    calibration=mca_calibration,
                )
                output_filenames.append(scan_output_filename)

        if failed_scans:
            raise RuntimeError(f"Failed scans (see logs why): {failed_scans}")

        self.outputs.output_filenames = output_filenames


def _asstr(data: Union[str, bytes]) -> Any:
    if isinstance(data, bytes):
        return data.decode()
    return data

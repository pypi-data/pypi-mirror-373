from typing import List

import h5py
import numpy

from ...tasks.hdf5_to_spec2 import Hdf5ToSpec2


def test_hdf5_to_spec2(tmp_path):
    raw_filename = tmp_path / "RAW_DATA" / "bliss_dataset.h5"
    raw_filename.parent.mkdir()
    raw_output_filename = tmp_path / "PROCESSED_DATA" / "bliss_dataset.mca"
    filename = str(raw_filename)
    output_filename = str(raw_output_filename)

    time_iso = "2025-08-27T13:53:01.817551"
    time_spec = "Wed Aug 27 13:53:01 2025"

    nscans = 3
    nchannels = 10
    with h5py.File(filename, "w") as nxroot:
        for scan in range(1, nscans + 1):
            nxroot[f"/{scan}.1/start_time"] = time_iso
            nxroot[f"/{scan}.1/title"] = "NISscan"
            nxroot[f"/{scan}.1/measurement/diode1"] = numpy.full((nchannels,), scan)
            nxroot[f"/{scan}.1/end_time"] = time_iso

    def check_scan_content(scans: List[int], scan_acq_times: List[float]) -> List[str]:
        with open(task.outputs["output_filename"], "r") as f:
            lines = [s.rstrip() for s in f.readlines()]

        expected = [f"#F {output_filename}", lines[1], ""]
        if not scan_acq_times:
            scan_acq_times = [0] * len(scans)
        for scan, acq_time in zip(scans, scan_acq_times):
            expected.append(f"#S {scan} NISscan")
            expected.append(f"#D {time_spec}")
            expected.append(f"#T {acq_time}  (Seconds)")
            expected.append("#L diode1  Seconds")
            for _ in range(nchannels):
                expected.append(f"{scan} {acq_time}")
            expected.append("#C")
            expected.append("")

        assert lines == expected

    all_scans_numbers = list(range(1, nscans + 1))

    # Test fresh file
    inputs = {
        "filename": filename,
        "output_filename": output_filename,
        "scan_numbers": all_scans_numbers[:-1],
    }
    task = Hdf5ToSpec2(inputs=inputs)
    task.run()
    check_scan_content(all_scans_numbers[:-1], [])

    # Test no-duplicates and append
    inputs = {"filename": filename, "output_filename": output_filename}
    task = Hdf5ToSpec2(inputs=inputs)
    task.run()
    check_scan_content(all_scans_numbers, [])

    # Test scan_acq_times
    raw_output_filename.unlink()
    inputs = {
        "filename": filename,
        "output_filename": output_filename,
        "scan_acq_times": all_scans_numbers,
    }
    task = Hdf5ToSpec2(inputs=inputs)
    task.run()
    check_scan_content(all_scans_numbers, all_scans_numbers)

    # Test scan_acq_times ignored
    scan_acq_times = []
    with h5py.File(filename, "a") as nxroot:
        for scan in range(1, nscans + 1):
            acq_time = scan / 10
            scan_acq_times.append(acq_time)
            nxroot[f"/{scan}.1/measurement/timer"] = numpy.full((nchannels,), acq_time)

    raw_output_filename.unlink()
    inputs = {
        "filename": filename,
        "output_filename": output_filename,
        "scan_acq_times": all_scans_numbers,
    }
    task = Hdf5ToSpec2(inputs=inputs)
    task.run()
    check_scan_content(all_scans_numbers, scan_acq_times)

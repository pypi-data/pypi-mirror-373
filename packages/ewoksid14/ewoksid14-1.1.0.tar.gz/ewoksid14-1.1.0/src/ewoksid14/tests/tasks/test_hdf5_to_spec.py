import h5py
import numpy
import pytest

from ...tasks.hdf5_to_spec import Hdf5ToSpec


def test_hdf5_to_spec(tmp_path):
    filename = tmp_path / "RAW_DATA" / "bliss_dataset.h5"
    filename.parent.mkdir()
    filename = str(filename)
    output_filename = str(tmp_path / "PROCESSED_DATA" / "bliss_dataset.mca")

    time_iso = "2025-08-27T13:53:01.817551"
    time_spec = "Wed Aug 27 13:53:01 2025"

    nscans = 3
    nchannels = 10
    with h5py.File(filename, "w") as nxroot:
        for scan in range(1, nscans + 1):
            nxroot[f"/{scan}.1/start_time"] = time_iso
            nxroot[f"/{scan}.1/title"] = "timescan 0.1"
            nxroot[f"/{scan}.1/measurement/Counts"] = numpy.full((1, nchannels), scan)
            nxroot[f"/{scan}.1/end_time"] = time_iso

    inputs = {
        "filename": filename,
        "scan_numbers": list(range(1, nscans + 1)),
        "output_filename": output_filename,
        "mca_calibration": [0.1, 0.2],
    }
    task = Hdf5ToSpec(inputs=inputs)
    task.run()

    output_filenames = [
        str(tmp_path / "PROCESSED_DATA" / f"bliss_dataset_{i:02d}.mca")
        for i in range(1, nscans + 1)
    ]
    assert task.get_output_values() == {"output_filenames": output_filenames}

    for i, filename in enumerate(output_filenames, 1):
        with open(filename, "r") as f:
            lines = [s.rstrip() for s in f.readlines()]

            expected = [
                f"#F {filename}",
                f"#D {time_spec}",
                "",
                f"#S {i} timescan 0.1",
                f"#D {time_spec}",
                f"#C Finished = {time_spec}",
                "#N 1",
                "#@MCA 16C",
                f"#@CHANN {nchannels} 0 {nchannels-1} 1",
                "#@CALIB 0.1 0.2 0",
                "#@MCA_NB 1",
                "#L Counts",
                "@A " + " ".join(map(str, [i] * 10)),
            ]
            assert lines == expected


def test_hdf5_to_spec_failed(tmp_path):
    filename = tmp_path / "RAW_DATA" / "bliss_dataset.h5"
    filename.parent.mkdir()
    filename = str(filename)
    output_filename = str(tmp_path / "PROCESSED_DATA" / "bliss_dataset.mca")

    time_iso = "2025-08-27T13:53:01.817551"

    nscans = 1
    nchannels = 10
    with h5py.File(filename, "w") as nxroot:
        for scan in range(1, nscans + 1):
            nxroot[f"/{scan}.1/start_time"] = time_iso
            nxroot[f"/{scan}.1/title"] = "timescan 0.1"
            nxroot[f"/{scan}.1/measurement/Counts"] = numpy.full((1, nchannels), scan)
            nxroot[f"/{scan}.1/end_time"] = time_iso

    inputs = {
        "filename": filename,
        "scan_numbers": list(range(1, nscans + 3)),
        "output_filename": output_filename,
        "retry_timeout": 0.1,
    }
    task = Hdf5ToSpec(inputs=inputs)
    with pytest.raises(
        RuntimeError, match=r"^Failed scans \(see logs why\): \[2, 3\]$"
    ):
        task.run()

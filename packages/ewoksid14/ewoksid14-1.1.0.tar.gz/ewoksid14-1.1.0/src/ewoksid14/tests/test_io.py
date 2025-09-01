import numpy

from ..tasks import io


def test_io_spec():
    time_iso = "2025-08-27T13:53:01.817551"
    time_spec = "Wed Aug 27 13:53:01 2025"

    mca = numpy.arange(6)
    mca_string = io.mca_data_to_spec_string(mca, date=time_iso)
    expected = [
        "#F unspecified",
        f"#D {time_spec}",
        "",
        "#S ct",
        f"#D {time_spec}",
        "#N 1",
        "#@MCA 16C",
        "#@CHANN 6 0 5 1",
        "#@CALIB 0 1 0",
        "#@MCA_NB 1",
        "#L MCA0",
        "@A 0 1 2 3 4 5",
        "",
    ]
    assert mca_string.split("\n") == expected

    mca = numpy.arange(16)
    mca_string = io.mca_data_to_spec_string(mca, date=time_iso)
    expected = [
        "#F unspecified",
        f"#D {time_spec}",
        "",
        "#S ct",
        f"#D {time_spec}",
        "#N 1",
        "#@MCA 16C",
        "#@CHANN 16 0 15 1",
        "#@CALIB 0 1 0",
        "#@MCA_NB 1",
        "#L MCA0",
        "@A 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15",
        "",
    ]
    assert mca_string.split("\n") == expected

    mca = numpy.arange(32)
    mca_string = io.mca_data_to_spec_string(mca, date=time_iso)
    expected = [
        "#F unspecified",
        f"#D {time_spec}",
        "",
        "#S ct",
        f"#D {time_spec}",
        "#N 1",
        "#@MCA 16C",
        "#@CHANN 32 0 31 1",
        "#@CALIB 0 1 0",
        "#@MCA_NB 1",
        "#L MCA0",
        "@A 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\\",
        " 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31",
        "",
    ]
    assert mca_string.split("\n") == expected

    mca = numpy.arange(33)
    mca_string = io.mca_data_to_spec_string(mca, date=time_iso)
    expected = [
        "#F unspecified",
        f"#D {time_spec}",
        "",
        "#S ct",
        f"#D {time_spec}",
        "#N 1",
        "#@MCA 16C",
        "#@CHANN 33 0 32 1",
        "#@CALIB 0 1 0",
        "#@MCA_NB 1",
        "#L MCA0",
        "@A 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\\",
        " 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31\\",
        " 32",
        "",
    ]
    assert mca_string.split("\n") == expected

    mca = numpy.arange(33)
    mca_string = io.mca_data_to_spec_string(
        mca, date=time_iso, metadata={"a": 1, "b": 2}
    )
    expected = [
        "#F unspecified",
        f"#D {time_spec}",
        "",
        "#S ct",
        f"#D {time_spec}",
        "#C a = 1",
        "#C b = 2",
        "#N 1",
        "#@MCA 16C",
        "#@CHANN 33 0 32 1",
        "#@CALIB 0 1 0",
        "#@MCA_NB 1",
        "#L MCA0",
        "@A 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\\",
        " 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31\\",
        " 32",
        "",
    ]
    assert mca_string.split("\n") == expected


def test_io_spec2():
    scan = io.SpecScanData(
        "1.1",
        "NISscan",
        "Wed Aug 27 13:53:01 2025",
        scan_data={"diode1": [1, 2], "diode2": [3, 4], "Seconds": [0.5, 0.5]},
        n_points=2,
    )
    spec_string = io.scan_data_to_spec_string(scan)
    expected = """#S 1 NISscan
#D Wed Aug 27 13:53:01 2025
#T 0.5  (Seconds)
#L diode1  diode2  Seconds
1 3 0.5
2 4 0.5
#C

"""
    assert spec_string == expected

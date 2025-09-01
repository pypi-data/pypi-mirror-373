from typing import List
from typing import Optional

from blissdata.h5api import dynamic_hdf5
from ewokscore.model import BaseInputModel
from ewokscore.task import Task
from pydantic import Field

from .io import SpecScanData
from .io import extract_scan_data
from .io import save_as_spec2


class Inputs(BaseInputModel):
    filename: str = Field(
        ...,
        description="Path to the HDF5 file. Can be absolute or relative.",
        examples=[
            "/data/visitor/hc6232/id14/20250716/PROCESSED_DATA/MK103_235K_IV/session_HRM2_22Jul25.h5",
            "session_HRM2_01Apr25.h5",
        ],
    )

    output_filename: str = Field(
        ...,
        description="Output filename for the extracted ASCII data. Can be absolute or relative.",
        examples=["jul16.asc", "/home/user/myname/output.asc"],
    )

    scan_numbers: Optional[List[int]] = Field(
        None,
        description="List of scans to extract.",
        examples=[[29, 30, 39, 40, 49, 50]],
    )

    counter_names: Optional[List[str]] = Field(
        None,
        description="List of counters/motors to extract.",
        examples=[["bin2", "bout2", "eib1", "pico2", "df", "di", "epoch", "timer"]],
    )

    scan_acq_times: Optional[List[float]] = Field(
        None,
        description=(
            "Acquisition time per point. Either a single-element list (applied to all scans), "
            "or a list matching the length of scan_numbers. When not provided try using the 'timer' counter."
        ),
        examples=[[8], [8, 8, 10]],
    )

    retry_timeout: Optional[float] = Field(
        None, description="Timeout for trying to read from the HDF5 file in seconds."
    )

    retry_period: Optional[float] = Field(
        None,
        description="Retry period for trying to read from the HDF5 file in seconds.",
    )


class Hdf5ToSpec2(Task, input_model=Inputs, output_names=["output_filename"]):
    """Convert Bliss HDF5 scans to SPEC files, multiple scans per file and only 1D counters."""

    def run(self):
        filename = self.inputs.filename
        scan_numbers = self.get_input_value("scan_numbers", [])
        counter_names = self.get_input_value("counter_names", [])
        scan_acq_times = self.get_input_value("scan_acq_times", [])
        retry_timeout = self.get_input_value("retry_timeout", 0)
        retry_period = self.get_input_value("retry_period", 1)

        scans: List[SpecScanData] = []
        with dynamic_hdf5.File(
            filename, retry_timeout=retry_timeout, retry_period=retry_period
        ) as nxroot:
            if scan_numbers:
                scan_names = [f"{scannr}.1" for scannr in scan_numbers]
            else:
                scan_names = list(nxroot)

            if scan_acq_times:
                if len(scan_acq_times) == 1:
                    scan_acq_times = scan_acq_times * len(scan_names)
                elif len(scan_acq_times) != len(scan_names):
                    raise ValueError(
                        "Length of 'scan_acq_times' and 'scan_numbers' must be the same"
                    )
            else:
                scan_acq_times = [None] * len(scan_names)

            for scan_name, acq_time in zip(scan_names, scan_acq_times):
                scan = extract_scan_data(nxroot, scan_name, counter_names, acq_time)
                scans.append(scan)

        self.outputs.output_filename = save_as_spec2(self.inputs.output_filename, scans)

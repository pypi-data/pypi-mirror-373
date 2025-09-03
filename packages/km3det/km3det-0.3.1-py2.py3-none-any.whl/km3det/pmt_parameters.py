import numpy as np
from pathlib import Path


class PMT_parameters:
    def __init__(self, filename):
        self.filename = Path(filename)
        self._data = None

        if self.filename.suffix == ".txt":
            with open(self.filename, "r") as fin:
                self._data = read_txt_pmt_parameters(fin)

    @property
    def pmts(self):
        return self._data["pmts"]


def read_txt_pmt_parameters(io):
    lines = io.readlines()

    lines = [line.strip() for line in lines if line.strip() and line.startswith("PMT=")]

    pmts_dtype = np.dtype(
        [
            ("module_id", np.int32),
            ("channel_id", np.int32),
            ("QE", np.float64),
            ("gain", np.float64),
            ("gain_spread", np.float64),
            ("rise_time", np.float64),
            ("tts", np.float64),
            ("threshold", np.float64),
        ]
    )
    pmts_data = []

    for line in lines:
        elements = line.split()
        pmts_data.append(tuple(elements[1:]))

    return {"pmts": np.array(pmts_data, dtype=pmts_dtype)}

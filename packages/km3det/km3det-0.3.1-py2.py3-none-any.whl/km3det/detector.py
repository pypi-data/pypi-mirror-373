import numpy as np
import struct
from pathlib import Path
from datetime import datetime, timedelta

MAX_POSIX_TIME = datetime(2038, 12, 31)


class Detector:
    def __init__(self, filename):
        self.filename = Path(filename)
        self._data = None
        self._com = None

        if self.filename.suffix == ".detx":
            with open(self.filename, "r") as fin:
                self._data = read_detx(fin)
        elif self.filename.suffix == ".datx":
            with open(self.filename, "rb") as fin:
                self._data = read_datx(fin)
        else:
            raise Exception(f"Unsupported file extension: {self.filename}")

    @property
    def detid(self):
        return self._data["detid"]

    @property
    def modules(self):
        return self._data["modules"]

    @property
    def pmts(self):
        return self._data["pmts"]

    @property
    def version(self):
        return self._data["version"]

    @property
    def utm(self):
        return (self._data["utm_position"], self._data["utm_ref_grid"])

    @property
    def n_modules(self):
        return self._data["n_modules"]

    @property
    def validity(self):
        return self._data["validity"]

    @property
    def absolute(self):
        data = self._data["modules"].copy()
        data["pos_x"] += self.utm[0][0]
        data["pos_y"] += self.utm[0][1]
        data["pos_z"] += self.utm[0][2]
        return data

    @property
    def com(self):
        """Center of mass"""
        if self._com is None:
            self._com = np.array(
                [
                    np.mean(self.pmts["pos_x"]),
                    np.mean(self.pmts["pos_y"]),
                    np.mean(self.pmts["pos_z"]),
                ]
            )
        return self._com


def unix2datetime(timestamp):
    if timestamp > MAX_POSIX_TIME.timestamp():
        timestamp = MAX_POSIX_TIME.timestamp()
    return datetime(1970, 1, 1) + timedelta(seconds=timestamp)


def _readstring(io):
    length = np.frombuffer(io.read(4), dtype=np.int32)[0]
    return io.read(length).decode("utf-8")


def read_detx(io):
    lines = io.readlines()

    header_last = max(
        [0]
        + [i for i, line in enumerate(lines) if line.strip() and line.startswith("#")]
    )

    lines = [
        line.strip()
        for line in lines[header_last:]
        if line.strip() and not line.startswith("#")
    ]

    first_line = lines[0].lower()

    if "v" in first_line:
        det_id, version = map(int, first_line.split("v"))
        validity = tuple([unix2datetime(float(t)) for t in lines[1].split()])
        utm_parts = lines[2].split()
        utm_position = np.array(utm_parts[3:6], dtype=np.float64)
        utm_ref_grid = " ".join(utm_parts[1:3])
        n_modules = int(lines[3])
        idx = 4
    else:
        det_id, n_modules = map(int, first_line.split())
        version = 1
        utm_position = None
        utm_ref_grid = None
        validity = None
        idx = 1

    module_dtype = np.dtype(
        [
            ("module_id", np.int32),
            ("du", np.int32),
            ("floor", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
            ("qa", np.float64),
            ("qb", np.float64),
            ("qc", np.float64),
            ("qd", np.float64),
            ("t0", np.float64),
            ("status", np.int32),
            ("n_pmts", np.int32),
        ]
    )

    pmts_dtype = np.dtype(
        [
            ("module_id", np.int32),
            ("pmt_id", np.int32),
            ("channel_id", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
            ("dir_x", np.float64),
            ("dir_y", np.float64),
            ("dir_z", np.float64),
            ("t0", np.float64),
            ("status", np.int32),
        ]
    )

    modules_data = []
    pmts_data = []

    floor_counter = 1
    last_string = -1

    for _ in range(n_modules):
        elements = lines[idx].split()
        module_id, string, floor = map(int, elements[:3])

        if floor == -1:
            if last_string == -1:
                last_string = string
            elif last_string != string:
                floor_counter = 1
                last_string = string
            floor = floor_counter
            floor_counter += 1

        if version >= 4:
            module_pos = np.array(elements[3:6], dtype=np.float64)
            q = np.array(elements[6:10], dtype=np.float64)
            t0 = float(elements[10])
        else:
            module_pos = np.zeros(3, dtype=np.float64)
            q = np.zeros(4, dtype=np.float64)
            t0 = 0.0

        status = float(elements[11]) if version >= 5 else 0.0
        n_pmts = int(elements[-1])

        pmts = np.zeros(n_pmts, dtype=pmts_dtype)

        for i in range(n_pmts):
            pmt_data = lines[idx + i + 1].split()
            pmts_data.append(
                (
                    int(module_id),
                    int(pmt_data[0]),
                    i,
                    *np.array(pmt_data[1:4], dtype=np.float64),
                    *np.array(pmt_data[4:7], dtype=np.float64),
                    float(pmt_data[7]),
                    int(pmt_data[8]) if version >= 3 else 0,
                )
            )

        modules_data.append(
            (module_id, string, floor, *module_pos, *q, t0, status, n_pmts)
        )

        idx += n_pmts + 1

    return {
        "version": version,
        "detid": det_id,
        "validity": validity,
        "utm_position": utm_position,
        "utm_ref_grid": utm_ref_grid,
        "n_modules": n_modules,
        "modules": np.array(modules_data, dtype=module_dtype),
        "pmts": np.array(pmts_data, dtype=pmts_dtype),
    }


def read_datx(io):
    comment_marker = b"####"
    supported_versions = {5}

    comments = []
    while io.read(4) == comment_marker:
        comments.append(_readstring(io))
    io.seek(max(0, io.tell() - len(comment_marker)))

    det_id = struct.unpack("i", io.read(4))[0]
    version = int(_readstring(io)[1:])
    if version not in supported_versions:
        raise ValueError(
            f"DATX version {version} is not supported. Supported versions: {supported_versions}"
        )

    validity = (
        unix2datetime(struct.unpack("d", io.read(8))[0]),
        unix2datetime(struct.unpack("d", io.read(8))[0]),
    )
    _readstring(io)  # Ignoring "UTM"
    wgs = _readstring(io)
    zone = _readstring(io)
    utm_ref_grid = f"{wgs} {zone}"
    utm_position = np.array(struct.unpack("ddd", io.read(24)), dtype=np.float64)
    n_modules = struct.unpack("i", io.read(4))[0]

    module_dtype = np.dtype(
        [
            ("module_id", np.int32),
            ("du", np.int32),
            ("floor", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
            ("qa", np.float64),
            ("qb", np.float64),
            ("qc", np.float64),
            ("qd", np.float64),
            ("t0", np.float64),
            ("status", np.int32),
            ("n_pmts", np.int32),
        ]
    )

    pmts_dtype = np.dtype(
        [
            ("module_id", np.int32),
            ("pmt_id", np.int32),
            ("channel_id", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
            ("dir_x", np.float64),
            ("dir_y", np.float64),
            ("dir_z", np.float64),
            ("t0", np.float64),
            ("status", np.int32),
        ]
    )

    modules_data = []
    pmts_data = []

    for _ in range(n_modules):
        module_id = struct.unpack("i", io.read(4))[0]
        du, floor = struct.unpack("ii", io.read(8))
        module_pos = struct.unpack("ddd", io.read(24))
        q = struct.unpack("dddd", io.read(32))
        module_t0 = struct.unpack("d", io.read(8))[0]
        module_status = struct.unpack("i", io.read(4))[0]
        n_pmts = struct.unpack("i", io.read(4))[0]

        for channel in range(n_pmts):
            pmt_id = struct.unpack("i", io.read(4))[0]
            pmt_pos = struct.unpack("ddd", io.read(24))
            pmt_dir = struct.unpack("ddd", io.read(24))
            pmt_t0 = struct.unpack("d", io.read(8))[0]
            pmt_status = struct.unpack("i", io.read(4))[0]
            pmts_data.append(
                (module_id, pmt_id, channel, *pmt_pos, *pmt_dir, pmt_t0, pmt_status)
            )

        modules_data.append(
            (module_id, du, floor, *module_pos, *q, module_t0, module_status, n_pmts)
        )

    return {
        "version": version,
        "detid": det_id,
        "validity": validity,
        "utm_position": utm_position,
        "utm_ref_grid": utm_ref_grid,
        "n_modules": n_modules,
        "modules": np.array(modules_data, dtype=module_dtype),
        "pmts": np.array(pmts_data, dtype=pmts_dtype),
    }

import numpy as np
from pathlib import Path
from .detector import Detector


class AuxilliaryObject:

    def __init__(self, filename, detector=None):
        self.filename = Path(filename)
        self._data = dict()
        self._detector = None

        if self.filename.suffix == ".txt":
            with open(self.filename, "r") as fin:
                self._data["raw"] = read_txt_file(fin, self.DTYPE)

        if detector is not None:
            self._set_detector(detector)

    def _set_detector(self, detector):
        """
        Utility class to attach a detector geometry to the Tripods object.
        """
        if isinstance(detector, Detector):
            self._detector = detector

        if isinstance(detector, str):
            detector = Path(detector)

        if isinstance(detector, Path):
            self._detector = Detector(detector)

        self._utm, self._grid = self._detector.utm

        return

    @property
    def detector(self):
        """
        Detector attached to geometry.
        """
        return self._detector

    @property
    def relative(self):
        """
        Tripods coordinates relative to Detector object.
        """
        if self._detector is None:
            raise AttributeError(
                "Detector model not declared, impossible to provide relative coordinates. use set_detector() to associate a detector geometry to the tripods."
            )

        return self._data["relative"]

    @property
    def absolute(self):
        """
        Absolute tripods coordinates.
        """
        return self._data["absolute"]

    @property
    def raw(self):
        """
        Raw (as written in the input file) coordinates.
        """
        return self._data["raw"]


class Tripods(AuxilliaryObject):
    """
    IO class for tripod.txt files, that contains the absolute
    coordinates of acoustic emitters (outside of Base Module emitters,
    that are handled in the Transmitter class.

    A detector can be optionally provided in order to shift the tripod
    in the reference frame of the Detector object.

    Parameters
    ----------
    filename : str or Path
    detector : str or Path or Detector, optional
    """

    DTYPE = np.dtype(
        [
            ("jpp_id", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
        ]
    )

    def __init__(self, filename, detector=None):
        super().__init__(filename, detector)
        self._data["absolute"] = self._data["raw"]
        if detector:
            self._data["relative"] = coordinates_relative_to_reference(
                self._data["absolute"], self._utm
            )


class Transmitters(AuxilliaryObject):
    """
    IO class for transmitter.txt files, that contains the relative
    coordinates of acoustic emitters attached to Base Module. The
    coordinates are expressed w.r.t. to the coordinate a module in the
    detector file, which is refered too by the du:floor pair key, with
    the floor typically being 0.
    A detector can be optionally provided in order to shift the transmitter
    in the reference frame of the Detector object.

    Parameters
    ----------
    filename : str or Path
    detector : str or Path or Detector, optional
    """

    DTYPE = np.dtype(
        [
            ("jpp_id", np.int32),
            ("du", np.int32),
            ("floor", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
        ]
    )

    def __init__(self, filename, detector=None):
        super().__init__(filename, detector)

        if detector:
            self._data["relative"] = generate_coordinates_from_modules_relation(
                self._data["raw"], self._detector.modules
            )
            self._data["absolute"] = coordinates_relative_to_reference(
                self._data["relative"], -1.0 * np.array(self._utm)
            )


class Hydrophones(AuxilliaryObject):
    """
    IO class for hydrophone.txt files, that contains the relative
    coordinates of hydrophones  attached to Base Module. The
    coordinates are expressed w.r.t. to the coordinate a module in the
    detector file, which is refered too by the du:floor pair key, with
    the floor typically being 0.

    A detector can be optionally provided in order to shift the transmitter
    in the reference frame of the Detector object.

    Parameters
    ----------
    filename : str or Path
    detector : str or Path or Detector, optional
    """

    DTYPE = np.dtype(
        [
            ("du", np.int32),
            ("floor", np.int32),
            ("pos_x", np.float64),
            ("pos_y", np.float64),
            ("pos_z", np.float64),
        ]
    )

    def __init__(self, filename, detector=None):
        super().__init__(filename, detector)
        self._data["raw"] = self._data["raw"][self._data["raw"]["floor"] != -1]

        if detector:
            self._data["relative"] = generate_coordinates_from_modules_relation(
                self._data["raw"], self._detector.modules
            )
            self._data["absolute"] = coordinates_relative_to_reference(
                self._data["relative"], -1.0 * np.array(self._utm)
            )


def read_txt_file(io, dtype):
    """
    IO class to read the txt file and return a Nammed Numpy array.
    """
    lines = io.readlines()

    lines = [
        line.strip() for line in lines if line.strip() and not line.startswith("#")
    ]

    data = []

    for line in lines:
        elements = line.split()
        data.append(tuple(elements))

    return np.array(data, dtype=dtype)


def coordinates_relative_to_reference(data, reference):
    """
    Compute the coordinate in the relative to reference.
    """
    relative = data.copy()

    relative["pos_x"] -= reference[0]
    relative["pos_y"] -= reference[1]
    relative["pos_z"] -= reference[2]

    return relative


def generate_coordinates_from_modules_relation(data, modules):
    """
    Compute the coordinate shifted with respect to the (du,floor) key indicated.
    """

    relative = data.copy()

    shifts = []

    for row in data:
        du, floor = row["du"], row["floor"]

        mod = modules[(modules["du"] == du) & (modules["floor"] == floor)]
        if len(mod) == 0:
            raise ValueError(
                f"Transmitter is linked to DU{du:03d}F{floor:02d}, but this module doesn't exist in the attached detector"
            )

        mod = mod[0]

        shifts.append([mod["pos_x"], mod["pos_y"], mod["pos_z"]])
    shifts = np.stack(shifts)

    relative["pos_x"] += shifts[:, 0]
    relative["pos_y"] += shifts[:, 1]
    relative["pos_z"] += shifts[:, 2]

    return relative

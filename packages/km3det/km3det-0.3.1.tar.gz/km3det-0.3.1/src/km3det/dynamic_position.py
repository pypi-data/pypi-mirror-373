import numpy as np
from pathlib import Path


class DynamicPosition:
    """
    Handler for dynamic positioning files.

    These files contains the results of the mechanical model fits, for each DU in the detector.
    It contains 2 trees:

    - head: This scalar tree contains the generic information about the fit
    - fits: contains the fitted parameters for each DU

    """

    FITS_DTYPE = [
        ("id", np.int32),
        ("tx", np.float64),
        ("ty", np.float64),
        ("tx2", np.float64),
        ("ty2", np.float64),
        ("vs", np.float64),
    ]

    def __init__(self, filename):
        self.filename = Path(filename)
        self._head = None
        self._fits = None
        if self.filename.suffix == ".root":
            self.read_file_root()
        else:
            raise NotImplemented(
                "Error, only dynamic positioning file in root format are supported"
            )

    def read_file_root(self):
        """
        Implement the reading of the root tree so populate self._head and self._fits.
        """
        import uproot

        with uproot.open(self.filename) as fin:
            self._head = fin["ACOUSTICS_FIT/JACOUSTICS::JHead/"].arrays()
            aliases = {
                key.replace("vector<JACOUSTICS::JFit>.", ""): key
                for key in fin["ACOUSTICS_FIT/vector<JACOUSTICS::JFit>/"].keys()
            }
            del aliases["fUniqueID"]
            del aliases["fBits"]
            self._fits = fin["ACOUSTICS_FIT/vector<JACOUSTICS::JFit>/"].arrays(
                aliases.keys(), aliases=aliases
            )

    @property
    def head(self):
        """Return the content of ACOUSTICS_FIT/JACOUSTICS::JHead/"""
        return self._head.to_numpy()

    @property
    def fits(self):
        """Return the content of 'ACOUSTICS_FIT/vector<JACOUSTICS::JFit>/"""
        return self._fits

    def fit(self, DU, fill_value=0):
        """Return the fit for a given DU. Same shape as head, missing fit values are replaced by fill_value"""
        import awkward as ak

        m_fits = self._fits.id == DU
        fits = ak.fill_none(ak.firsts(self._fits[m_fits]), fill_value).to_numpy()
        return fits

    @property
    def DUs(self):
        """Return the list of DUs for which fits are available"""
        import awkward as ak

        return np.unique(ak.flatten(self._fits.id))

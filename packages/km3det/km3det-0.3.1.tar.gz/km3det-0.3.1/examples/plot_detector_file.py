"""
How to read detector file
=========================

The following example shows how to read detector file using the ``Detector`` class
"""

from km3det import Detector
from km3net_testdata import data_path

datx_file_path = data_path("datx/KM3NeT_00000133_20221025.datx")

#####################################################
# Initialising a Detector
# -----------------------
# Detector take a file path as input:


det = Detector(datx_file_path)

#####################################################
# Look at module level information
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The (optical) modules level information can be accessed this way
# (just printing the first 10 rows here):

print(det.modules[:10])

#####################################################
# The name of each fields can be obtained like so:

print(det.modules.dtype.names)


#####################################################
# Look at PMTs level information
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The PMTs level information can be accessed this way
# (just printing the first 10 rows here):

print(det.pmts[:10])

#####################################################
# The name of each fields can be obtained like so:

print(det.pmts.dtype.names)

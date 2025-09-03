"""
How to read PMT parameters file
===============================

The following example shows how to read detector file using the ``Detector`` class
"""

from km3det import PMT_parameters
from km3net_testdata import data_path

pmt_file_path = data_path("pmt/calibration_00000117_H_1.0.0_00013757_00013826_1.txt")

#####################################################
# Initialising a Detector
# -----------------------
# Detector take a file path as input:


pars = PMT_parameters(pmt_file_path)


#####################################################
# Look at PMTs level information
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The PMTs level information can be accessed this way
# (just printing the first 10 rows here):

print(pars.pmts[:10])

#####################################################
# The name of each fields can be obtained like so:

print(pars.pmts.dtype.names)

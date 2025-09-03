#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from km3net_testdata import data_path
from km3det import PMT_parameters


class TestPMTparameters(unittest.TestCase):
    def setUp(self):
        self.pars_path = data_path(
            "pmt/calibration_00000117_H_1.0.0_00013757_00013826_1.txt"
        )

    def test_reader(self):
        self.pars = PMT_parameters(self.pars_path)
        assert len(self.pars.pmts) == 7254

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from km3net_testdata import data_path
from km3det import Detector


class TestDetectorV5(unittest.TestCase):
    def setUp(self):
        self.datx_path = data_path("datx/KM3NeT_00000133_20221025.datx")
        self.detx_path = data_path("detx/KM3NeT_00000133_20221025.detx")

    def test_datx_reader(self):
        self.datx = Detector(self.datx_path)
        assert self.datx.n_modules == 399
        assert self.datx.n_modules == len(self.datx.modules)
        assert len(self.datx.pmts) == 11718
        assert self.datx.version == 5

    def test_detx_reader(self):
        self.detx = Detector(self.detx_path)
        assert self.detx.n_modules == 399
        assert self.detx.n_modules == len(self.detx.modules)
        assert len(self.detx.pmts) == 11718
        assert self.detx.version == 5

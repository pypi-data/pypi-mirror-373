#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from km3net_testdata import data_path
from km3det import Detector, Tripods, Hydrophones, Transmitters


class TestDetectorV5(unittest.TestCase):
    def setUp(self):
        self.datx_path = data_path("detector_geometry/KM3NeT_00000232.detector.datx")
        self.tripod_path = data_path("detector_geometry/KM3NeT_00000232.tripod.txt")
        self.hydrophone_path = data_path(
            "detector_geometry/KM3NeT_00000232.hydrophone.txt"
        )
        self.transmitter_path = data_path(
            "detector_geometry/KM3NeT_00000232.transmitter.txt"
        )
        self.detector = Detector(self.datx_path)

    def test_tripod_read(self):
        tripod = Tripods(self.tripod_path)
        tripod = Tripods(self.tripod_path, self.datx_path)
        tripod = Tripods(self.tripod_path, self.detector)

        assert len(tripod.raw) == 8
        assert len(tripod.absolute) == 8
        assert len(tripod.relative) == 8

    def test_hydrophone_read(self):
        hydrophone = Hydrophones(self.hydrophone_path)
        hydrophone = Hydrophones(self.hydrophone_path, self.datx_path)
        hydrophone = Hydrophones(self.hydrophone_path, self.detector)

        assert len(hydrophone.raw) == 29
        assert len(hydrophone.absolute) == 29
        assert len(hydrophone.relative) == 29

    def test_transmitter_read(self):
        transmitter = Transmitters(self.transmitter_path)
        transmitter = Transmitters(self.transmitter_path, self.datx_path)
        transmitter = Transmitters(self.transmitter_path, self.detector)

        assert len(transmitter.raw) == 5
        assert len(transmitter.absolute) == 5
        assert len(transmitter.relative) == 5

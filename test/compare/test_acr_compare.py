import unittest
import pandas as pd
from statistics import NormalDist  # only run on version >= Python 3.8

from acr_compare import calc_overlap, create_bins


class CalcOverlap(unittest.TestCase):

    def test_unique(self):
        self.assertEqual(calc_overlap(10, 0.5, None, None, True), 0)

    def test_same(self):
        self.assertEqual(calc_overlap(10, 0.5, 10, 0.5, False), 1)

    def test_far(self):
        self.assertEqual(calc_overlap(0, 0.5, 1000, 0.5, False), 0)
        self.assertEqual(calc_overlap(10, 0.0001, 20, 0.0001, False), 0)

    def test_exact(self):
        self.assertEqual(calc_overlap(5, 1, 10, 1, False), NormalDist(10, 1).cdf(7.5) * 2)
        self.assertEqual(calc_overlap(5, 0.25, 5.1, 0.2, False),
                         NormalDist(5, 0.25).overlap(NormalDist(5.1, 0.2)))

    def test_order(self):
        self.assertEqual(calc_overlap(10, 0.5, 11, 0.4, False), calc_overlap(11, 0.4, 10, 0.5, False))


class Bins(unittest.TestCase):

    def setUp(self) -> None:
        self.segments2 = pd.DataFrame([[10, 20, 1, 1, 1, 1],
                                       [30, 40, 2, 2, 2, 2],
                                       [41, 45, 3, 3, 3, 3]],
                                      columns=['Start.bp', 'End.bp', 'mu.minor',
                                               'sigma.minor', 'mu.major', 'sigma.major'])
        self.one_stats = pd.Series([1, 1, 1, 1],
                                   ['mu.minor', 'sigma.minor', 'mu.major', 'sigma.major'])
        self.two_stats = pd.Series([2, 2, 2, 2],
                                   ['mu.minor', 'sigma.minor', 'mu.major', 'sigma.major'])
        self.three_stats = pd.Series([3, 3, 3, 3],
                                     ['mu.minor', 'sigma.minor', 'mu.major', 'sigma.major'])
        self.five_stats = pd.Series([5, 5, 5, 5],
                                    ['mu.minor', 'sigma.minor', 'mu.major', 'sigma.major'])

        self.chrom = 1

    def test_past_seg2(self):
        bin, pointer = create_bins(50, 59, self.segments2, 3, self.five_stats, self.chrom)
        self.assertEqual(len(bin), 1)
        self.assertEqual(bin[0]['length'], 9)
        self.assertEqual(bin[0]['mu.minor_1'], 5)  # todo test all
        self.assertIsNone(bin[0]['mu.minor_2'])
        self.assertEqual(pointer, 3)

    def test_single(self):
        bin, pointer = create_bins(10, 15, self.segments2, 0, self.five_stats, self.chrom)
        self.assertEqual(len(bin), 1)
        self.assertEqual(bin[0]['length'], 5)
        self.assertEqual(bin[0]['mu.minor_1'], 5)
        self.assertEqual(bin[0]['mu.minor_2'], 1)
        self.assertEqual(pointer, 0)

        bin, pointer = create_bins(32, 40, self.segments2, 0, self.five_stats, self.chrom)
        self.assertEqual(len(bin), 1)
        self.assertEqual(bin[0]['length'], 8)
        self.assertEqual(bin[0]['mu.minor_1'], 5)
        self.assertEqual(bin[0]['mu.minor_2'], 2)
        self.assertEqual(pointer, 1)

    def test_multiple(self):
        bin, pointer = create_bins(8, 25, self.segments2, 0, self.five_stats, self.chrom)
        self.assertEqual(len(bin), 3)
        self.assertEqual(pointer, 1)
        self.assertEqual(bin[0]['length'], 2)
        self.assertEqual(bin[0]['mu.minor_1'], 5)
        self.assertIsNone(bin[0]['mu.minor_2'])
        self.assertEqual(bin[1]['length'], 10)
        self.assertEqual(bin[1]['mu.minor_1'], 5)
        self.assertEqual(bin[1]['mu.minor_2'], 1)
        self.assertEqual(bin[2]['length'], 5)
        self.assertEqual(bin[2]['mu.minor_1'], 5)
        self.assertIsNone(bin[2]['mu.minor_2'])

        bin, pointer = create_bins(18, 42, self.segments2, 0, self.five_stats, self.chrom)
        self.assertEqual(len(bin), 5)
        self.assertEqual(pointer, 2)
        self.assertEqual(bin[0]['length'], 2)
        self.assertEqual(bin[0]['mu.minor_1'], 5)
        self.assertEqual(bin[0]['mu.minor_2'], 1)
        self.assertEqual(bin[1]['length'], 10)
        self.assertEqual(bin[1]['mu.minor_1'], 5)
        self.assertIsNone(bin[1]['mu.minor_2'])
        self.assertEqual(bin[2]['length'], 10)
        self.assertEqual(bin[2]['mu.minor_1'], 5)
        self.assertEqual(bin[2]['mu.minor_2'], 2)
        self.assertEqual(bin[3]['length'], 1)
        self.assertEqual(bin[3]['mu.minor_1'], 5)
        self.assertIsNone(bin[3]['mu.minor_2'])
        self.assertEqual(bin[4]['length'], 1)
        self.assertEqual(bin[4]['mu.minor_1'], 5)
        self.assertEqual(bin[4]['mu.minor_2'], 3)

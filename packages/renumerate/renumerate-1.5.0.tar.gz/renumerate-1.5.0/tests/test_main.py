# Copyright (c) 2016 Adam Karpierz
# SPDX-License-Identifier: Zlib

import unittest
import types

from renumerate import renumerate


class MainTestCase(unittest.TestCase):

    def setUp(self):
        self.seasons = ["Spring", "Summer", "Fall", "Winter"]

    def test_renumerate_type(self):
        self.assertIs(type(renumerate(self.seasons)), types.GeneratorType)
        self.assertIsInstance(renumerate(self.seasons), types.GeneratorType)
        for item in renumerate(self.seasons):
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIs(type(item[0]), int)

    def test_renumerate_as_tuple(self):
        self.assertTupleEqual(tuple(renumerate(self.seasons)),
                              ((3, "Winter"), (2, "Fall"), (1, "Summer"), (0, "Spring")))
        self.assertTupleEqual(tuple(renumerate(self.seasons, start=4)),
                              ((4, "Winter"), (3, "Fall"), (2, "Summer"), (1, "Spring")))
        self.assertTupleEqual(tuple(renumerate(self.seasons, end=2)),
                              ((5, "Winter"), (4, "Fall"), (3, "Summer"), (2, "Spring")))
        with self.assertRaises(TypeError):
            renumerate(self.seasons, start=4, end=2)

    def test_renumerate_as_list(self):
        self.assertListEqual(list(renumerate(self.seasons)),
                             [(3, "Winter"), (2, "Fall"), (1, "Summer"), (0, "Spring")])
        self.assertListEqual(list(renumerate(self.seasons, start=4)),
                             [(4, "Winter"), (3, "Fall"), (2, "Summer"), (1, "Spring")])
        self.assertListEqual(list(renumerate(self.seasons, end=2)),
                             [(5, "Winter"), (4, "Fall"), (3, "Summer"), (2, "Spring")])
        with self.assertRaises(TypeError):
            renumerate(self.seasons, start=4, end=2)

#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Tests for :py:mod:`hawat.utils`.
"""

import unittest

from hawat import utils
from hawat.test import HawatTestCase
from hawat.test.runner import TestRunnerMixin


class UtilsTestCase(TestRunnerMixin, HawatTestCase):
    """
    Class for testing `hawat.utils`.
    """

    def test_get_format_byte_size_function_no_args(self):
        """
        Test the function :py:func:`hawat.utils.get_format_byte_size_function`
        without any arguments.
        """

        f = utils.get_format_byte_size_function()
        self.assertEqual(f(0), "0 B")
        self.assertEqual(f(1024), "1 KB")
        self.assertEqual(f(1024**2), "1 MB")
        self.assertEqual(f(1024**3), "1 GB")
        self.assertEqual(f(-31415926), "-29.96 MB")
        self.assertEqual(f(1024**7), "1024 EB")

    def test_get_format_byte_size_function_custom_base(self):
        """
        Test the function :py:func:`hawat.utils.get_format_byte_size_function`
        with base = 1000.
        """

        f = utils.get_format_byte_size_function(base=1000)
        self.assertEqual(f(0), "0 B")
        self.assertEqual(f(1024), "1.024 KB")
        self.assertEqual(f(1000**2), "1 MB")
        self.assertEqual(f(10123 * 1000**2), "10.12 GB")
        self.assertEqual(f(-31415926), "-31.42 MB")
        self.assertEqual(f(1000**7 + 1), "1000 EB")

    def test_get_format_byte_size_function_custom_format(self):
        """
        Test the function :py:func:`hawat.utils.get_format_byte_size_function`
        with custom format function.
        """

        f = utils.get_format_byte_size_function(format_func=lambda x: f"{x:.2f}")
        self.assertEqual(f(0), "0.00 B")
        self.assertEqual(f(1024), "1.00 KB")
        self.assertEqual(f(1024**2), "1.00 MB")
        self.assertEqual(f(1024**3), "1.00 GB")
        self.assertEqual(f(-31415926), "-29.96 MB")
        self.assertEqual(f(1024**7), "1024.00 EB")

    def test_get_format_byte_size_function_custom_format_and_base(self):
        """
        Test the function :py:func:`hawat.utils.get_format_byte_size_function`
        with custom format function and base = 1000.
        """

        f = utils.get_format_byte_size_function(format_func=lambda x: f"{x:.5f}", base=1234)
        self.assertEqual(f(0), "0.00000 B")
        self.assertEqual(f(1024), "1024.00000 B")
        self.assertEqual(f(1235), "1.00081 KB")
        self.assertEqual(f(1234**2), "1.00000 MB")
        self.assertEqual(f(1234**3), "1.00000 GB")
        self.assertEqual(f(-31415926), "-20.63097 MB")
        self.assertEqual(f(1234**7), "1234.00000 EB")

    def test_fallback_formatter(self):
        """
        Test the function :py:func:`hawat.utils.fallback_formatter`.
        """

        @utils.fallback_formatter
        def formatter(x):
            return f"{1 / x:.2f}"

        self.assertEqual(formatter(2), "0.50")
        self.assertEqual(formatter(0), "🗙")
        self.assertEqual(formatter(-1), "-1.00")
        self.assertEqual(formatter(0.1), "10.00")
        self.assertEqual(formatter(0.0), "🗙")


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()

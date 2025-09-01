#! /usr/bin/env python3

from py2be.truthy import (
    string_is_falsey,
    string_is_truey,
    string_is_truthy,
)

import unittest
from unittest.mock import patch

import re

try:

    from StringIO import StringIO
except ImportError:

    from io import StringIO


class Truthy_tester(unittest.TestCase):


    def test__string_is_falsey(self):

        self.assertFalse(string_is_falsey(""))
        self.assertFalse(string_is_falsey("Copyright ©"))

        self.assertTrue(string_is_falsey("0"))
        self.assertTrue(string_is_falsey("false"))
        self.assertTrue(string_is_falsey(" FALSE"))
        self.assertTrue(string_is_falsey("False"))
        self.assertTrue(string_is_falsey("FaLSe"))
        self.assertTrue(string_is_falsey("no"))
        self.assertTrue(string_is_falsey("No "))
        self.assertTrue(string_is_falsey("NO"))
        self.assertTrue(string_is_falsey(" Off "))
        self.assertTrue(string_is_falsey("off"))
        self.assertTrue(string_is_falsey("OFF"))

        self.assertFalse(string_is_falsey("1"))
        self.assertFalse(string_is_falsey("true"))
        self.assertFalse(string_is_falsey("TRUE"))
        self.assertFalse(string_is_falsey("True"))
        self.assertFalse(string_is_falsey("tRuE"))
        self.assertFalse(string_is_falsey("yes"))
        self.assertFalse(string_is_falsey(" YES"))
        self.assertFalse(string_is_falsey("Yes   "))
        self.assertFalse(string_is_falsey("yEs"))


    def test__string_is_truey(self):

        self.assertFalse(string_is_truey(""))
        self.assertFalse(string_is_truey("Copyright ©"))

        self.assertFalse(string_is_truey("0"))
        self.assertFalse(string_is_truey("false"))
        self.assertFalse(string_is_truey(" FALSE"))
        self.assertFalse(string_is_truey("False"))
        self.assertFalse(string_is_truey("FaLSe"))
        self.assertFalse(string_is_truey("no"))
        self.assertFalse(string_is_truey("No "))
        self.assertFalse(string_is_truey("NO"))
        self.assertFalse(string_is_truey(" Off "))
        self.assertFalse(string_is_truey("off"))
        self.assertFalse(string_is_truey("OFF"))

        self.assertTrue(string_is_truey("1"))
        self.assertTrue(string_is_truey("true"))
        self.assertTrue(string_is_truey("TRUE"))
        self.assertTrue(string_is_truey("True"))
        self.assertTrue(string_is_truey("tRuE"))
        self.assertTrue(string_is_truey("yes"))
        self.assertTrue(string_is_truey(" YES"))
        self.assertTrue(string_is_truey("Yes   "))
        self.assertTrue(string_is_truey("yEs"))


    def test__string_is_truthy(self):

        self.assertFalse(string_is_truthy(""))
        self.assertFalse(string_is_truthy("Copyright ©"))

        self.assertTrue(string_is_truthy("0"))
        self.assertTrue(string_is_truthy("false"))
        self.assertTrue(string_is_truthy(" FALSE"))
        self.assertTrue(string_is_truthy("False"))
        self.assertTrue(string_is_truthy("FaLSe"))
        self.assertTrue(string_is_truthy("no"))
        self.assertTrue(string_is_truthy("No "))
        self.assertTrue(string_is_truthy("NO"))
        self.assertTrue(string_is_truthy(" Off "))
        self.assertTrue(string_is_truthy("off"))
        self.assertTrue(string_is_truthy("OFF"))

        self.assertTrue(string_is_truthy("1"))
        self.assertTrue(string_is_truthy("true"))
        self.assertTrue(string_is_truthy("TRUE"))
        self.assertTrue(string_is_truthy("True"))
        self.assertTrue(string_is_truthy("tRuE"))
        self.assertTrue(string_is_truthy("yes"))
        self.assertTrue(string_is_truthy(" YES"))
        self.assertTrue(string_is_truthy("Yes   "))
        self.assertTrue(string_is_truthy("yEs"))


if '__main__' == __name__:

    unittest.main()


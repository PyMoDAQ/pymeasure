#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# Expected frames were generated with the minimalmodbus library.

from pymeasure.instruments.eurotherm import Eurotherm3216
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(Eurotherm3216, []):
        pass


def test_program_status():
    with expected_protocol(
        Eurotherm3216,
        [(b"\x01\x03\x00\x17\x00\x014\x0e", b"\x01\x03\x02\x00\x01y\x84")],
    ) as inst:
        assert inst.program_status == "run"


def test_program_status_setter():
    with expected_protocol(
        Eurotherm3216,
        [(b"\x01\x10\x00\x17\x00\x01\x02\x00\x01d\xb7", b"\x01\x10\x00\x17\x00\x01\xb1\xcd")],
    ) as inst:
        inst.program_status = "run"


def test_segment_dwell():
    with expected_protocol(
        Eurotherm3216,
        [(b"\x01\x03\x8a\x00\x00\x02\xee\x13", b"\x01\x03\x04\x00\x01_\x90\x92o")],
    ) as inst:
        assert inst.segments[1].dwell == 90


def test_segment_dwell_setter():
    with expected_protocol(
        Eurotherm3216,
        [(b"\x01\x10\x8a\x00\x00\x02\x04\x00\x01_\x90\x84\x95", b"\x01\x10\x8a\x00\x00\x02k\xd0")],
    ) as inst:
        inst.segment_1.dwell = 90

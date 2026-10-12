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

from pymeasure.instruments.eurotherm import Eurotherm2200
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(Eurotherm2200, []):
        pass


def test_operating_mode():
    with expected_protocol(
        Eurotherm2200,
        [(b"\x01\x03\x01\x11\x00\x01\xd5\xf3", b"\x01\x03\x02\x00\x01y\x84")],
    ) as inst:
        assert inst.operating_mode == "manual"


def test_operating_mode_setter():
    with expected_protocol(
        Eurotherm2200,
        [(b"\x01\x10\x01\x11\x00\x01\x02\x00\x01t\x11", b"\x01\x10\x01\x11\x00\x01P0")],
    ) as inst:
        inst.operating_mode = "manual"


def test_program_status():
    with expected_protocol(
        Eurotherm2200,
        [(b"\x01\x03\x00\x17\x00\x014\x0e", b"\x01\x03\x02\x00\x10\xb9\x88")],
    ) as inst:
        assert inst.program_status == "end"


def test_run_program():
    with expected_protocol(
        Eurotherm2200,
        [(b'\x01\x10\x009\x00\x01\x02\x00\x02"\xf8', b"\x01\x10\x009\x00\x01\xd1\xc4")],
    ) as inst:
        inst.run_program()

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

# Loop 2 parameters are at the loop 1 address plus 1024.

import pytest

from pymeasure.instruments.eurotherm import Eurotherm3500
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(Eurotherm3500, []):
        pass


def test_loop_2_process_value():
    with expected_protocol(
        Eurotherm3500,
        [(b"\x01\x03\x88\x02\x00\x02Nk", b"\x01\x03\x04C\x16\x80\x00o\xb3")],
    ) as inst:
        assert inst.loop_2.process_value == 150.5


def test_loop_2_target_setpoint_setter():
    with expected_protocol(
        Eurotherm3500,
        [(b"\x01\x10\x88\x04\x00\x02\x04C\x16\x00\x00\x00\x1a",
          b"\x01\x10\x88\x04\x00\x02+\xa9")],
    ) as inst:
        inst.loop_2.target_setpoint = 150


def test_loop_2_setpoint_rate_disabled_setter():
    with expected_protocol(
        Eurotherm3500,
        [(b"\x01\x10\x04N\x00\x01\x02\x00\x01-\xbe", b"\x01\x10\x04N\x00\x01`\xee")],
    ) as inst:
        inst.loop_2.setpoint_rate_disabled = True


def test_instrument_type():
    with expected_protocol(
        Eurotherm3500,
        [(b"\x01\x03\x00z\x00\x01\xa5\xd3", b"\x01\x03\x02\x00\x01y\x84")],
    ) as inst:
        assert inst.instrument_type == "3504"


def test_active_setpoint_invalid():
    with expected_protocol(Eurotherm3500, []) as inst, pytest.raises(ValueError):
        inst.loop_1.active_setpoint = 3


def test_loop_2_alternative_setpoint():
    with expected_protocol(
        Eurotherm3500,
        [(b"\x01\x03\x8b\xca\x00\x02\xcf\xd1", b"\x01\x03\x04C\x16\x80\x00o\xb3")],
    ) as inst:
        assert inst.loop_2.alternative_setpoint == 150.5

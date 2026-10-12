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

from pymeasure.instruments.eurotherm import Eurotherm2400
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(Eurotherm2400, []):
        pass


def test_program_status():
    with expected_protocol(
        Eurotherm2400,
        [(b"\x01\x03\x00\x17\x00\x014\x0e", b"\x01\x03\x02\x00\x10\xb9\x88")],
    ) as inst:
        assert inst.program_status == "complete"


def test_setpoint_setter():
    with expected_protocol(
        Eurotherm2400,
        [(b"\x01\x10\x81X\x00\x02\x04B(\x00\x00\x0f\x13", b"\x01\x10\x81X\x00\x02\xe8'")],
    ) as inst:
        inst.setpoints[11].value = 42


def test_segment_type():
    with expected_protocol(
        Eurotherm2400,
        [(b"\x01\x03 \x90\x00\x01\x8f\xe7", b"\x01\x03\x02\x00\x01y\x84")],
    ) as inst:
        assert inst.programs[1].segments[1].segment_type == "ramp rate"


def test_segment_target_setpoint_setter():
    with expected_protocol(
        Eurotherm2400,
        [(b'\x01\x10\xc1"\x00\x02\x04Cz\x00\x00\x19\xa6', b'\x01\x10\xc1"\x00\x02\xdc>')],
    ) as inst:
        inst.program_1.segment_1.target_setpoint = 250


def test_remote_setpoint_enabled():
    with expected_protocol(
        Eurotherm2400,
        [(b"\x01\x03\x01\x14\x00\x01\xc5\xf2", b"\x01\x03\x02\x00\x01y\x84")],
    ) as inst:
        assert inst.remote_setpoint_enabled is True

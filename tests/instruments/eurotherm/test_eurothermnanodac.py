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

# The nanodac is addressed through Modbus TCP. Parameters are read from the IEEE region at
# 0x8000 + 2 * address, with the addresses of the nanodac user guide (HA030554).
# The loop 2 addresses are those of loop 1 plus 128 (runtime parameters, below 0x1000) or
# plus 256 (configuration parameters).

import struct

import pytest

from pymeasure.instruments.eurotherm import EurothermNanodac
from pymeasure.test import expected_protocol


def read_pair(address, value, transaction=1):
    """Request and response frames to read the float parameter at `address`."""
    tid = transaction.to_bytes(2, "big")
    native = 0x8000 + 2 * address
    request = tid + b"\x00\x00\x00\x06\x01\x03" + native.to_bytes(2, "big") + b"\x00\x02"
    response = tid + b"\x00\x00\x00\x07\x01\x03\x04" + struct.pack(">f", value)
    return request, response


def write_pair(address, value):
    """Request and response frames to write the float parameter at `address` (transaction 1)."""
    native = 0x8000 + 2 * address
    head = native.to_bytes(2, "big") + b"\x00\x02"
    request = (b"\x00\x01\x00\x00\x00\x0b\x01\x10" + head + b"\x04"
               + struct.pack(">f", value))
    response = b"\x00\x01\x00\x00\x00\x06\x01\x10" + head
    return request, response


def test_init():
    with expected_protocol(EurothermNanodac, []):
        pass


def test_process_value_is_loop_1():
    with expected_protocol(EurothermNanodac, [read_pair(512, 25.5)]) as inst:
        assert inst.process_value == 25.5


def test_loop_1_target_setpoint_setter():
    with expected_protocol(EurothermNanodac, [write_pair(514, 150.0)]) as inst:
        inst.loop_1.target_setpoint = 150


def test_loop_2_process_value_uses_runtime_offset():
    with expected_protocol(EurothermNanodac, [read_pair(640, 30.25)]) as inst:
        assert inst.loop_2.process_value == 30.25


def test_loop_2_working_setpoint():
    with expected_protocol(EurothermNanodac, [read_pair(643, 100.0)]) as inst:
        assert inst.loop_2.working_setpoint == 100.0


def test_loop_2_output_level():
    with expected_protocol(EurothermNanodac, [read_pair(644, 12.5)]) as inst:
        assert inst.loop_2.output_level == 12.5


def test_loop_2_target_setpoint_setter():
    with expected_protocol(EurothermNanodac, [write_pair(642, 150.0)]) as inst:
        inst.loop_2.target_setpoint = 150


def test_loop_2_proportional_band_uses_config_offset():
    with expected_protocol(EurothermNanodac, [read_pair(5947, 20.0)]) as inst:
        assert inst.loop_2.proportional_band == 20.0


def test_loop_2_setpoint_rate_limit_setter():
    with expected_protocol(EurothermNanodac, [write_pair(5986, 5.0)]) as inst:
        inst.loop_2.setpoint_rate_limit = 5


def test_loop_1_pid_attributes():
    with expected_protocol(
        EurothermNanodac,
        [read_pair(5691, 1.5), read_pair(5692, 2.5, 2), read_pair(5693, 3.5, 3)],
    ) as inst:
        values = (inst.proportional_band, inst.integral_time, inst.derivative_time)
        assert values == (1.5, 2.5, 3.5)


@pytest.mark.parametrize("channel, address", [(1, 256), (2, 260), (3, 264), (4, 268)])
def test_channel_process_value(channel, address):
    with expected_protocol(EurothermNanodac, [read_pair(address, 21.5)]) as inst:
        assert getattr(inst, f"channel_{channel}").process_value == 21.5


def test_mode():
    request = b"\x00\x01\x00\x00\x00\x06\x01\x03\x02\x01\x00\x01"
    response = b"\x00\x01\x00\x00\x00\x05\x01\x03\x02\x00\x01"
    with expected_protocol(EurothermNanodac, [(request, response)]) as inst:
        assert inst.loop_1.mode == "manual"


def test_loop_2_active_setpoint_invalid():
    with expected_protocol(EurothermNanodac, []) as inst, pytest.raises(ValueError):
        inst.loop_2.active_setpoint = 3


def test_loop_2_active_setpoint():
    # integer register 5723 + 256 = 5979 = 0x175b
    request = b"\x00\x01\x00\x00\x00\x06\x01\x03\x17\x5b\x00\x01"
    response = b"\x00\x01\x00\x00\x00\x05\x01\x03\x02\x00\x01"
    with expected_protocol(EurothermNanodac, [(request, response)]) as inst:
        assert inst.loop_2.active_setpoint == 2

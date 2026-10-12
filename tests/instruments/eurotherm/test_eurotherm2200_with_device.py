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

# Tests to run on a real controller. They are skipped unless pytest gets an address:
#
#   pytest tests/instruments/eurotherm/test_eurotherm2200_with_device.py \
#       --device-address ASRL3::INSTR -rX
#
# Set EUROTHERM_ADDRESS (Modbus address, default 1) and EUROTHERM_BAUD_RATE if needed.
# Run them on an idle controller: they read parameters, change a few settings (PID,
# rate limits, units) and restore them, and never start a program or heat.
#
# Every test is marked @UNVERIFIED until it passed on hardware. A test that passes is
# reported as XPASS (listed by -rX): remove its @UNVERIFIED line and fill in the record.
#
# Hardware verification record (one line per run):
#   date | who | model, firmware | link (RTU or TCP) | tests unflagged
#   -    | -   | -               | -                 | -

import pytest
from eurotherm_device_utils import (
    UNVERIFIED,
    assert_changes_and_restores,
    assert_plausible_output,
    assert_plausible_temperature,
    connection_kwargs,
)

from pymeasure.instruments.eurotherm import Eurotherm2200


@pytest.fixture(scope="module")
def controller(connected_device_address):
    controller = Eurotherm2200(connected_device_address, **connection_kwargs())
    try:
        assert_plausible_temperature(controller.process_value)
    except Exception as exc:  # noqa: BLE001
        # Stop here, otherwise the failure would be hidden as XFAIL in every test.
        pytest.exit(f"Cannot communicate with the controller: {exc!r}", returncode=1)
    yield controller
    controller.adapter.close()


@UNVERIFIED
def test_process_value(controller):
    assert_plausible_temperature(controller.process_value)


@UNVERIFIED
def test_working_setpoint(controller):
    assert_plausible_temperature(controller.working_setpoint)


@UNVERIFIED
def test_output_level(controller):
    assert_plausible_output(controller.output_level)


@UNVERIFIED
def test_target_setpoint_rewrite(controller):
    """Write back the current target setpoint, which does not change anything."""
    setpoint = controller.target_setpoint
    assert_plausible_temperature(setpoint)
    controller.target_setpoint = setpoint
    assert controller.target_setpoint == pytest.approx(setpoint)


@UNVERIFIED
@pytest.mark.parametrize("name", ["proportional_band", "integral_time", "derivative_time"])
def test_pid(controller, name):
    old = getattr(controller, name)
    assert_changes_and_restores(controller, name, old + 1)


@UNVERIFIED
def test_active_setpoint(controller):
    assert controller.active_setpoint in (1, 2)


@UNVERIFIED
@pytest.mark.parametrize("name", ["setpoint1", "setpoint2"])
def test_setpoint_read(controller, name):
    """Only read: these setpoints are stored in non-volatile memory."""
    assert_plausible_temperature(getattr(controller, name))


@UNVERIFIED
def test_setpoint_rate_limit(controller):
    old = controller.setpoint_rate_limit
    assert_changes_and_restores(controller, "setpoint_rate_limit", old + 1)


@UNVERIFIED
def test_operating_mode(controller):
    assert controller.operating_mode in ["auto", "manual"]


@UNVERIFIED
def test_dwell_time(controller):
    assert controller.dwell_time >= 0


@UNVERIFIED
def test_end_type(controller):
    old = controller.end_type
    new = next(value for value in ["dwell", "reset", "hold", "standby"] if value != old)
    assert_changes_and_restores(controller, "end_type", new)


@UNVERIFIED
def test_program_status(controller):
    assert controller.program_status in ["off", "run", "hold", "end", "dwell", "ramp"]

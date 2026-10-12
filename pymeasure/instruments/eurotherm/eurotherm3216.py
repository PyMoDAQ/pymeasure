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

from pymeasure.instruments import AdapterType, Instrument

from .eurotherm_base import (
    EurothermBase,
    OffsetChannel,
    enum_control,
    float_control,
    int_control,
    time_control,
)


class Eurotherm3216Segment(OffsetChannel):
    """A program segment of the Eurotherm 3216: a ramp to a target setpoint and a dwell."""

    def offset(self) -> int:
        """Return the address offset of this segment."""
        return 1280 + 3 * (self.number - 1)

    dwell = time_control(
        0,
        """Control the dwell duration of the segment in s (float).""",
    )

    target_setpoint = float_control(
        1,
        """Control the target setpoint of the segment (float).""",
    )

    ramp_rate = float_control(
        2,
        """Control the ramp rate of the segment in units per :attr:`~Eurotherm3216.ramp_units`
        (float).""",
    )

    def clear(self) -> None:
        """Set target setpoint, ramp rate and dwell time to 0."""
        self.target_setpoint = 0
        self.ramp_rate = 0
        self.dwell = 0


class Eurotherm3216(EurothermBase):
    """Eurotherm 3216 temperature controller with its 8 segment programmer.

    It communicates via Modbus RTU (8 data bits, 1 stop bit, no parity by default).
    Set the address and baud rate configured on the controller.

    .. code-block:: python

        from pymeasure.instruments.eurotherm import Eurotherm3216

        controller = Eurotherm3216("ASRL3::INSTR", address=1)
        print(controller.process_value)
        controller.segments[1].target_setpoint = 300
        controller.segments[1].ramp_rate = 10
        controller.program_status = "run"
    """

    segments = Instrument.MultiChannelCreator(
        Eurotherm3216Segment, list(range(1, 9)), prefix="segment_"
    )

    def __init__(self, adapter: AdapterType, name: str = "Eurotherm 3216", **kwargs):
        super().__init__(adapter, name, **kwargs)

    working_output = float_control(
        4,
        """Control the working output in percent (float, read-only in auto mode).""",
    )

    program_status = enum_control(
        23,
        """Control the program status (str 'reset', 'run', 'hold' or 'end').""",
        values={"reset": 0, "run": 1, "hold": 2, "end": 3},
    )

    remote_setpoint = float_control(
        26,
        """Control the remote (communications) setpoint (float).

        It is used if :attr:`remote_setpoint_enabled` is True.""",
    )

    calculated_error = Instrument.measurement(
        "F,39",
        """Measure the calculated error, i.e. process value minus setpoint (float).""",
    )

    remote_setpoint_enabled = enum_control(
        276,
        """Control whether the remote setpoint is used instead of the local one (bool).""",
        values={False: 0, True: 1},
    )

    end_type = enum_control(
        328,
        """Control the programmer end type (str 'setpoint1' or 'dwell').""",
        values={"setpoint1": 0, "dwell": 1},
    )

    program_cycles = int_control(
        332,
        """Control the number of program cycles to run (int).""",
    )

    current_program_cycle = Instrument.measurement(
        "I,333",
        """Measure the current program cycle number (int).""",
        cast=int,
    )

    ramp_units = enum_control(
        531,
        """Control the ramp rate time unit (str 'mins', 'hours' or 'secs').""",
        values={"mins": 0, "hours": 1, "secs": 2},
    )

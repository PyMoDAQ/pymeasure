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
from pymeasure.instruments.validators import strict_discrete_set

from .eurotherm2200 import OPERATING_MODES
from .eurotherm_base import (
    EurothermBase,
    OffsetChannel,
    enum_control,
    float_control,
    int_control,
    time_control,
)

#: Addresses of the setpoints SP1 to SP16.
SETPOINT_ADDRESSES = (24, 25, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
                      176, 177)

SEGMENT_TYPES = {"end": 0, "ramp rate": 1, "ramp time": 2, "dwell": 3, "step": 4, "call": 5}

TIME_UNITS = {"secs": 0, "mins": 1, "hours": 2}


class Eurotherm2400Setpoint(OffsetChannel):
    """One of the 16 setpoints of the Eurotherm 2400."""

    def offset(self) -> int:
        """Return the address of this setpoint."""
        return SETPOINT_ADDRESSES[self.id - 1]

    value = float_control(
        0,
        """Control the setpoint value (float).

        Do not write continuously changing values to it, as it is stored in
        non-volatile memory.""",
    )


class Eurotherm2400Segment(OffsetChannel):
    """A segment of a Eurotherm 2400 program.

    Which parameters are meaningful depends on the :attr:`segment_type`:

    * 'ramp rate': :attr:`target_setpoint` and :attr:`ramp_rate`,
    * 'ramp time': :attr:`target_setpoint` and :attr:`duration`,
    * 'dwell': :attr:`duration`,
    * 'step': :attr:`target_setpoint`,
    * 'call': :attr:`called_program`,
    * 'end': :attr:`end_power` and :attr:`end_type`.

    Set the segment type first, as it defines the other parameters.
    """

    def offset(self) -> int:
        """Return the address offset of this segment within its program."""
        return 8 * self.id

    segment_type = enum_control(
        0,
        """Control the segment type
        (str 'end', 'ramp rate', 'ramp time', 'dwell', 'step' or 'call').""",
        values=SEGMENT_TYPES,
    )

    target_setpoint = float_control(
        1,
        """Control the target setpoint of a ramp or step segment (float).""",
    )

    ramp_rate = float_control(
        2,
        """Control the ramp rate of a 'ramp rate' segment in units per ramp unit (float).""",
    )

    duration = time_control(
        2,
        """Control the duration of a 'ramp time' or 'dwell' segment in s (float).""",
    )

    called_program = int_control(
        3,
        """Control the program number called by a 'call' segment (int).""",
    )

    end_power = float_control(
        1,
        """Control the output power in percent of an 'end' segment (float).""",
    )

    end_type = enum_control(
        3,
        """Control the end type of an 'end' segment (str 'dwell' or 'reset').""",
        values={"dwell": 0, "reset": 1},
    )


class Eurotherm2400Program(OffsetChannel):
    """A program of the Eurotherm 2400 with its general data and 16 segments.

    Program 0 is the working program, which is read-only.
    """

    segments = Instrument.MultiChannelCreator(
        Eurotherm2400Segment, list(range(1, 17)), prefix="segment_"
    )

    def offset(self) -> int:
        """Return the address offset of this program."""
        return 8192 + 136 * self.id

    holdback_type = enum_control(
        0,
        """Control the holdback type (str 'none', 'low', 'high' or 'band').""",
        values={"none": 0, "low": 1, "high": 2, "band": 3},
    )

    holdback_value = float_control(
        1,
        """Control the holdback value (float).""",
    )

    ramp_units = enum_control(
        2,
        """Control the ramp rate time unit (str 'secs', 'mins' or 'hours').""",
        values=TIME_UNITS,
    )

    dwell_units = enum_control(
        3,
        """Control the dwell time unit shown on the display (str 'secs', 'mins' or 'hours').""",
        values=TIME_UNITS,
    )

    cycles = int_control(
        4,
        """Control the number of program cycles (int).""",
    )


class Eurotherm2400(EurothermBase):
    """Eurotherm 2400 series (2404, 2408, 2416...) temperature controller and programmer.

    It communicates via Modbus RTU (8 data bits, 1 stop bit, no parity by default).
    Set the address and baud rate configured on the controller.

    The setpoints SP1 to SP16 are available in :attr:`setpoints`, the programs 0
    (working program, read-only) to 20 in :attr:`programs`. Depending on the model
    and options, fewer setpoints and programs may be available.

    .. code-block:: python

        from pymeasure.instruments.eurotherm import Eurotherm2400

        controller = Eurotherm2400("ASRL3::INSTR", address=1)
        program = controller.programs[1]
        program.segments[1].segment_type = "ramp rate"
        program.segments[1].target_setpoint = 300
        program.segments[1].ramp_rate = 10
        program.segments[2].segment_type = "end"
        controller.current_program = 1
        controller.program_status = "run"
    """

    setpoints = Instrument.MultiChannelCreator(
        Eurotherm2400Setpoint, list(range(1, 17)), prefix="sp_"
    )

    programs = Instrument.MultiChannelCreator(
        Eurotherm2400Program, list(range(21)), prefix="program_"
    )

    def __init__(self, adapter: AdapterType, name: str = "Eurotherm 2400", **kwargs):
        super().__init__(adapter, name, **kwargs)

    active_setpoint = int_control(
        15,
        """Control which setpoint is active (int from 1 to 16).""",
        validator=strict_discrete_set,
        values=list(range(1, 17)),
        get_process=lambda v: int(v) + 1,
        set_process=lambda v: v - 1,
    )

    operating_mode = enum_control(
        273,
        """Control the operating mode (str 'auto' or 'manual').""",
        values=OPERATING_MODES,
    )

    current_program = int_control(
        22,
        """Control the active program number (int).""",
    )

    program_status = enum_control(
        23,
        """Control the program status
        (str 'reset', 'run', 'hold', 'holdback' or 'complete').""",
        values={"reset": 1, "run": 2, "hold": 4, "holdback": 8, "complete": 16},
    )

    current_segment = Instrument.measurement(
        "I,56",
        """Measure the number of the running segment (int).""",
        cast=int,
    )

    current_segment_type = Instrument.measurement(
        "I,29",
        """Measure the type of the running segment (str, see
        :attr:`Eurotherm2400Segment.segment_type`).""",
        values=SEGMENT_TYPES,
        map_values=True,
    )

    segment_time_remaining = Instrument.measurement(
        "T,36",
        """Measure the time remaining in the running segment in s (float).""",
    )

    segment_setpoint = Instrument.measurement(
        "F,160",
        """Measure the target setpoint of the running segment (float).""",
    )

    segment_ramp_rate = Instrument.measurement(
        "F,161",
        """Measure the ramp rate of the running segment (float).""",
    )

    programmer_setpoint = Instrument.measurement(
        "F,163",
        """Measure the programmer setpoint (float).""",
    )

    program_cycles_remaining = Instrument.measurement(
        "I,59",
        """Measure the number of program cycles remaining (int).""",
        cast=int,
    )

    program_time_remaining = Instrument.measurement(
        "T,58",
        """Measure the time remaining in the running program in s (float).""",
    )

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

from .eurotherm_base import EurothermBase, enum_control, time_control

OPERATING_MODES = {"auto": 0, "manual": 1}


class Eurotherm2200(EurothermBase):
    """Eurotherm 2200 series (2208, 2216...) temperature controller.

    It communicates via Modbus RTU (8 data bits, 1 stop bit, no parity by default).
    Set the address and baud rate configured on the controller.

    The simple programmer ramps from setpoint 1 to setpoint 2 at
    :attr:`setpoint_rate_limit`, then dwells for :attr:`dwell_time`.

    .. code-block:: python

        from pymeasure.instruments.eurotherm import Eurotherm2200

        controller = Eurotherm2200("ASRL3::INSTR", address=1)
        controller.target_setpoint = 300
        print(controller.process_value)
    """

    def __init__(self, adapter: AdapterType, name: str = "Eurotherm 2200", **kwargs):
        super().__init__(adapter, name, **kwargs)

    operating_mode = enum_control(
        273,
        """Control the operating mode (str 'auto' or 'manual').""",
        values=OPERATING_MODES,
    )

    dwell_time = time_control(
        62,
        """Control the programmer dwell time in s after ramping to setpoint 2 (float).""",
    )

    end_type = enum_control(
        517,
        """Control the state at the end of the program
        (str 'dwell', 'reset', 'hold' or 'standby').""",
        values={"dwell": 0, "reset": 1, "hold": 2, "standby": 3},
    )

    program_status = Instrument.measurement(
        "I,23",
        """Measure the program status (str 'off', 'run', 'hold', 'end', 'dwell' or 'ramp').""",
        values={"off": 1, "run": 2, "hold": 4, "end": 16, "dwell": 32, "ramp": 64},
        map_values=True,
    )

    def run_program(self) -> None:
        """Run the program."""
        self.write("I,57,2")
        self.check_set_errors()

    def reset_program(self) -> None:
        """Reset the program."""
        self.write("I,57,1")
        self.check_set_errors()

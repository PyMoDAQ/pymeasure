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

from .eurotherm_base import EurothermBase, OffsetChannel, enum_control, float_control, int_control

BOOLEANS = {False: 0, True: 1}

#: Address offset between the parameters of two consecutive loops.
LOOP_OFFSET = 1024


class Eurotherm3500Loop(OffsetChannel):
    """One control loop of the Eurotherm 3500.

    Parameters of loop 2 are at the loop 1 address plus 1024.
    """

    def offset(self) -> int:
        """Return the address offset of this loop."""
        return LOOP_OFFSET * (self.number - 1)

    process_value = Instrument.measurement(
        "F,1",
        """Measure the process value, e.g. the temperature (float).""",
    )

    target_setpoint = float_control(
        2,
        """Control the target setpoint (float).""",
    )

    manual_output = float_control(
        3,
        """Control the output power used in manual mode in percent (float).""",
    )

    output_level = Instrument.measurement(
        "F,4",
        """Measure the active output power level in percent (float).""",
    )

    working_setpoint = Instrument.measurement(
        "F,5",
        """Measure the working setpoint, i.e. the setpoint currently used (float).""",
    )

    proportional_band = float_control(
        6,
        """Control the PID proportional band (float).""",
    )

    integral_time = float_control(
        8,
        """Control the PID integral time in s (float).""",
    )

    derivative_time = float_control(
        9,
        """Control the PID derivative time in s (float).""",
    )

    active_setpoint = int_control(
        15,
        """Control which setpoint is active (int, 1 for SP1, 2 for SP2).""",
        validator=strict_discrete_set,
        values=[1, 2],
        get_process=lambda v: int(v) + 1,
        set_process=lambda v: v - 1,
    )

    setpoint1 = float_control(
        24,
        """Control the setpoint 1 (float).

        Do not write continuously changing values to it, as it is stored in
        non-volatile memory with a limited number of write cycles (typically 100,000).""",
    )

    setpoint2 = float_control(
        25,
        """Control the setpoint 2 (float).

        Do not write continuously changing values to it, as it is stored in
        non-volatile memory with a limited number of write cycles (typically 100,000).""",
    )

    setpoint_rate_limit = float_control(
        35,
        """Control the setpoint rate limit in units per ramp unit (float, 0 means no limit).""",
    )

    output_rate_limit = float_control(
        37,
        """Control the output rate limit in percent per second (float, 0 means no limit).""",
    )

    alternative_setpoint = float_control(
        485,
        """Control the alternative (remote) setpoint of the loop (float).

        It is used if the alternative setpoint is enabled on the controller (Alt SP En).

        .. warning::

            The loop 1 address follows the AERCO 3508 user guide, the loop 2 address is
            inferred. Whether this setpoint is kept out of non-volatile memory and must be
            refreshed periodically is not confirmed.""",
    )

    setpoint_rate_disabled = enum_control(
        78,
        """Control whether the setpoint rate limit is disabled (bool).""",
        values=BOOLEANS,
    )


class Eurotherm3500(EurothermBase):
    """Eurotherm 3500 series (3504, 3508) controller with two control loops.

    It communicates via Modbus RTU over a serial link, or via Modbus TCP over Ethernet.
    The register addresses follow the 3500 driver of
    `PABausson/pymodaq_plugins_eurotherm
    <https://github.com/PABausson/pymodaq_plugins_eurotherm>`__.
    The parameters inherited from :class:`EurothermBase` act on loop 1, the parameters
    of each loop are available through :attr:`loop_1` and :attr:`loop_2`.

    .. code-block:: python

        from pymeasure.instruments.eurotherm import Eurotherm3500

        controller = Eurotherm3500("ASRL3::INSTR", address=1)
        controller.loop_2.target_setpoint = 150
        print(controller.loop_1.process_value, controller.loop_2.process_value)

    .. warning::

        This driver has not been tested on hardware yet. Parameters are read from the
        IEEE region (full resolution floats), whereas the reference driver reads the
        scaled 16-bit registers. The addresses of :attr:`Eurotherm3500Loop.manual_output`
        and of the loop 2 rate limit disable are inferred from the loop 1 addresses.
    """

    loops = Instrument.MultiChannelCreator(Eurotherm3500Loop, [1, 2], prefix="loop_")

    def __init__(
        self,
        adapter: AdapterType,
        name: str = "Eurotherm 3500",
        baud_rate: int = 19200,
        **kwargs,
    ):
        super().__init__(adapter, name, baud_rate=baud_rate, **kwargs)

    output_level = Instrument.measurement(
        "F,4",
        """Measure the active output power level of loop 1 in percent (float).""",
    )

    instrument_type = Instrument.measurement(
        "I,122",
        """Measure the instrument type (str '3508' or '3504').""",
        values={"3508": 0, "3504": 1},
        map_values=True,
    )

    temperature_units = enum_control(
        516,
        """Control the display temperature units (str 'C', 'F' or 'K').""",
        values={"C": 0, "F": 1, "K": 2},
    )

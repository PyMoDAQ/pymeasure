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

#: Address offset between consecutive loops, for the runtime parameters (below 0x1000).
LOOP_RUNTIME_OFFSET = 128
#: Address offset between consecutive loops, for the configuration parameters.
LOOP_CONFIG_OFFSET = 256
#: First address of the configuration parameters of a loop.
CONFIG_START = 0x1000
#: Address offset between consecutive channels.
CHANNEL_OFFSET = 4


class EurothermNanodacChannel(OffsetChannel):
    """One input channel of the Eurotherm nanodac.

    The process value of channel N is at the channel 1 address plus 4 * (N - 1).
    """

    def offset(self) -> int:
        """Return the address offset of this channel."""
        return CHANNEL_OFFSET * (self.number - 1)

    process_value = Instrument.measurement(
        "F,256",
        """Measure the process value of the channel (float), in the units of the channel.""",
    )


class EurothermNanodacLoop(OffsetChannel):
    """One control loop of the Eurotherm nanodac.

    The addresses are those of loop 1 of the nanodac user guide (HA030554). The
    runtime parameters of loop N are at the loop 1 address plus 128 * (N - 1), the
    configuration parameters (from 0x1000) at the loop 1 address plus 256 * (N - 1).
    """

    def offset(self) -> int:
        """Return the address offset of this loop for a runtime parameter."""
        return LOOP_RUNTIME_OFFSET * (self.number - 1)

    def insert_id(self, command: str) -> str:
        """Shift the register address of `command` by the loop offset."""
        kind, address, *value = command.split(",")
        step = LOOP_CONFIG_OFFSET if int(address) >= CONFIG_START else LOOP_RUNTIME_OFFSET
        return ",".join([kind, str(int(address) + step * (self.number - 1)), *value])

    process_value = Instrument.measurement(
        "F,512",
        """Measure the process value of the loop (float).""",
    )

    mode = enum_control(
        513,
        """Control the loop mode (str 'auto' or 'manual').""",
        values={"auto": 0, "manual": 1},
    )

    target_setpoint = float_control(
        514,
        """Control the target setpoint (float).

        This parameter is not in the list of parameters the nanodac user guide says not to
        write continuously (EEPROM), but see the warning of :class:`EurothermNanodac`.""",
    )

    working_setpoint = Instrument.measurement(
        "F,515",
        """Measure the working setpoint, i.e. the setpoint currently used (float).""",
    )

    output_level = Instrument.measurement(
        "F,516",
        """Measure the working output in percent (float).""",
    )

    proportional_band = float_control(
        5691,
        """Control the PID proportional band of set 1 (float).

        The nanodac user guide lists it among the parameters not to write continuously.""",
    )

    integral_time = float_control(
        5692,
        """Control the PID integral time of set 1 in s (float).

        The nanodac user guide lists it among the parameters not to write continuously.""",
    )

    derivative_time = float_control(
        5693,
        """Control the PID derivative time of set 1 in s (float).

        The nanodac user guide lists it among the parameters not to write continuously.""",
    )

    manual_output = float_control(
        5760,
        """Control the output used in manual mode in percent (float).""",
    )

    active_setpoint = int_control(
        5723,
        """Control which setpoint is active (int, 1 for SP1, 2 for SP2).""",
        validator=strict_discrete_set,
        values=[1, 2],
        get_process=lambda v: int(v) + 1,
        set_process=lambda v: v - 1,
    )

    setpoint1 = float_control(
        5724,
        """Control the setpoint 1 (float).""",
    )

    setpoint2 = float_control(
        5725,
        """Control the setpoint 2 (float).""",
    )

    alternative_setpoint = float_control(
        5728,
        """Control the alternative setpoint (float).

        It is used if :attr:`alternative_setpoint_enabled` is set.""",
    )

    alternative_setpoint_enabled = enum_control(
        5729,
        """Control whether the alternative setpoint is used (bool).""",
        values=BOOLEANS,
    )

    setpoint_rate_limit = float_control(
        5730,
        """Control the setpoint rate limit in units per ramp unit (float, 0 means no limit).""",
    )

    setpoint_rate_disabled = enum_control(
        5731,
        """Control whether the setpoint rate limit is disabled (bool).""",
        values=BOOLEANS,
    )


class EurothermNanodac(EurothermBase):
    """Eurotherm nanodac recorder/controller with two control loops and four channels.

    It communicates via Modbus TCP over Ethernet (the nanodac has no serial Modbus).
    The register addresses follow the nanodac user guide (HA030554, issue 12), parameters
    are read as IEEE floating point numbers (address ``0x8000 + 2 * address``), so the
    number of decimals configured on the instrument does not matter.
    The parameters inherited from :class:`EurothermBase` act on loop 1, the parameters
    of each loop are available through :attr:`loop_1` and :attr:`loop_2`, the process
    value of each input channel through :attr:`channel_1` to :attr:`channel_4`.

    .. code-block:: python

        from pymeasure.instruments.eurotherm import EurothermNanodac

        controller = EurothermNanodac("TCPIP::192.168.1.10::502::SOCKET")
        controller.loop_2.target_setpoint = 150
        print(controller.loop_1.process_value, controller.channel_2.process_value)

    .. warning::

        This driver has not been tested on hardware yet.

        A write of several registers with an invalid value is silently ignored by the
        nanodac, without an error response: read the parameter back to check it.
        The user guide lists the PID parameters, the output limits and the setpoint ranges
        among the parameters which must not be written continuously (EEPROM). The target
        setpoint, SP1, SP2, the alternative setpoint and the setpoint rate limit are not
        in that list, but this has not been checked on hardware.
        The nanodac may answer slowly while it archives: use a generous timeout.
    """

    loops = Instrument.MultiChannelCreator(EurothermNanodacLoop, [1, 2], prefix="loop_")
    channels = Instrument.MultiChannelCreator(EurothermNanodacChannel, [1, 2, 3, 4],
                                              prefix="channel_")

    def __init__(
        self,
        adapter: AdapterType,
        name: str = "Eurotherm nanodac",
        tcp: bool = True,
        timeout: int = 3000,
        **kwargs,
    ):
        super().__init__(adapter, name, tcp=tcp, timeout=timeout, **kwargs)

    # The parameters inherited from the base class have the addresses of the 2000 and 3000
    # series: replace them by those of loop 1.
    process_value = Instrument.measurement(
        "F,512",
        """Measure the process value of loop 1 (float).""",
    )

    target_setpoint = float_control(
        514,
        """Control the target setpoint of loop 1 (float).""",
    )

    working_setpoint = Instrument.measurement(
        "F,515",
        """Measure the working setpoint of loop 1 (float).""",
    )

    output_level = Instrument.measurement(
        "F,516",
        """Measure the working output of loop 1 in percent (float).""",
    )

    proportional_band = float_control(
        5691,
        """Control the PID proportional band of loop 1, set 1 (float).""",
    )

    integral_time = float_control(
        5692,
        """Control the PID integral time of loop 1, set 1 in s (float).""",
    )

    derivative_time = float_control(
        5693,
        """Control the PID derivative time of loop 1, set 1 in s (float).""",
    )

    active_setpoint = int_control(
        5723,
        """Control which setpoint of loop 1 is active (int, 1 for SP1, 2 for SP2).""",
        validator=strict_discrete_set,
        values=[1, 2],
        get_process=lambda v: int(v) + 1,
        set_process=lambda v: v - 1,
    )

    setpoint1 = float_control(
        5724,
        """Control the setpoint 1 of loop 1 (float).""",
    )

    setpoint2 = float_control(
        5725,
        """Control the setpoint 2 of loop 1 (float).""",
    )

    setpoint_rate_limit = float_control(
        5730,
        """Control the setpoint rate limit of loop 1 (float, 0 means no limit).""",
    )

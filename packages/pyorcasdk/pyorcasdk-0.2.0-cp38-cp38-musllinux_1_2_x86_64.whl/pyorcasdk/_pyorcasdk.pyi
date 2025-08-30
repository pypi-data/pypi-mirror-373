"""
Python binding for the C++ orcaSDK
"""

from __future__ import annotations
import typing

__all__ = [
    "Actuator",
    "ConstF",
    "Damper",
    "ForceMode",
    "HapticEffect",
    "HapticMode",
    "Inertia",
    "KinematicMode",
    "MessagePriority",
    "MotorMode",
    "OrcaError",
    "OrcaResultInt16",
    "OrcaResultInt32",
    "OrcaResultList",
    "OrcaResultMotorMode",
    "OrcaResultUInt16",
    "Osc0",
    "Osc1",
    "OscillatorType",
    "PositionMode",
    "Pulse",
    "Sine",
    "SleepMode",
    "Spring0",
    "Spring1",
    "Spring2",
    "SpringCoupling",
    "StreamData",
    "both",
    "important",
    "not_important",
    "positive",
]

class Actuator:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    @typing.overload
    def __init__(self, name: str, modbus_server_address: int = 1) -> None:
        """Constructs an actuator object.

        Args:
            name (str): The name of the actuator, also available through the public member variable Actuator.name.
            modbus_server_address (int, optional): The modbus server address. Defaults to 1.
        """
        ...

    @typing.overload
    def __init__(
        self,
        serial_interface: ...,
        clock: ...,
        name: str,
        modbus_server_address: int = 1,
    ) -> None:
        """Constructs an actuator object when custom serial communication and clock implementations are necessary.
        This constructor is suitable for testing or for use on platforms that are not yet supported.

        Args:
            serial_interface: An custom implementation of the SerialInterface class.
            clock: An custom implementation of the Clock class with custom behaviour.
            name (str): The name of the actuator, also available through the public member variable Actuator.name.
            modbus_server_address (int, optional): The modbus server address. Defaults to 1.
        """
        ...

    @typing.overload
    def begin_serial_logging(self, log_name: str) -> OrcaError:
        """Begins logging serial communication to a file, between this application and the motor.

        Args:
            log_name (str): The name of the file to be written to. Assumes relative path of the built executable file.
        """
        ...

    @typing.overload
    def begin_serial_logging(self, log_name: str, log: ...) -> OrcaError:
        """Begins logging to a custom log interface.

        Args:
            log_name (str): The name of the file to be written to. Assumes relative path to the location of the built executable file.
            log: A pointer to a custom implementation of the LogInterface. Used for custom logging behaviour.
        """
        ...

    def clear_errors(self) -> OrcaError:
        """Clears the motor's active errors. If the condition causing the errors remains, the errors will appear immediately again."""
        ...

    def close_serial_port(self) -> None:
        """Closes open serial ports, releasing all associated handles."""
        ...

    def disable_stream(self) -> None:
        """Disables communication with server and transitions to disconnecting state, disabling the transceiver hardware."""
        ...

    def enable_haptic_effects(self, effects: int) -> OrcaError:
        """Sets the haptic effect to enabled or disabled according to the input bits.

        Args:
            effects (int): The bitmask representing which haptic effects to enable. This value is a bitwise combination of HapticEffect enum values.

        Note:
            Refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def enable_stream(self) -> None:
        """Enables command streaming with the ORCA.

        Command streaming is the main form of asynchronous communication with the Orca, and required for Position, Force, and Haptic modes.
        When enabled, the motor object automatically injects command stream messages when run() is called, unless the object is waiting on an active message.
        Returned data is stored in the public stream_cache member of type StreamData.

        Note:
            See the ORCA Series Modbus User Guide, ORCA-specific Function Codes section for details on command streaming.
        """
        ...

    def get_errors(self) -> OrcaResultUInt16:
        """Returns the bitmask representing the motor's active errors.

        Returns:
            Bitmask representing the motor's active errors.

        Note:
            To check for a specific error, a bitwise AND can be combined with the value of the error of interest.
            See the ORCA Reference Manual, Errors: Active and Latched Error Registers, for further details on error types.
        """
        ...

    def get_force_mN(self) -> OrcaResultInt32:
        """Returns the total amount of force sensed by the motor.

        Returns:
            Force in millinewtons.
        """
        ...

    def get_latched_errors(self) -> OrcaResultUInt16:
        """Displays all errors that have been encountered since the last time the errors were manually cleared."""
        ...

    def get_major_version(self) -> OrcaResultUInt16:
        """Returns the firmware's major version.

        Returns:
            Firmware's major version.
        """
        ...

    def get_mode(self) -> OrcaResultMotorMode:
        """Requests the current mode of operation from the motor.

        Returns:
            The ORCA's current mode of operation.
        """
        ...

    def get_position_um(self) -> OrcaResultInt32:
        """Returns the position of the motor's shaft in micrometers. The position is based on the distance from the zero position.

        Returns:
            Position in micrometers.
        """
        ...

    def get_power_W(self) -> OrcaResultUInt16:
        """Returns the amount of power drawn by the motor, in Watts.

        Returns:
            Power in Watts.
        """
        ...

    def get_release_state(self) -> OrcaResultUInt16:
        """Returns the firmware release state (minor version).

        Returns:
            Firmware's minor version.
        """
        ...

    def get_revision_number(self) -> OrcaResultUInt16:
        """Returns the firmware's revision number.

        Returns:
            Firmware's revision number.
        """
        ...

    def get_serial_number(self) -> ...:
        """Returns the actuator's serial number.

        Returns:
            The actuator's serial number.
        """
        ...

    def get_stream_data(self) -> StreamData:
        """Provides access to the stream_cache member variable.

        Returns:
            Returns an object containing the most recently obtained stream cache from the command stream.
        """
        ...

    def get_temperature_C(self) -> OrcaResultUInt16:
        """Returns the motor's temperature, in Celsius, as measured by the motor's onboard sensor.

        Returns:
            The motor's onboard sensor temperature in Celsius.
        """
        ...

    def get_voltage_mV(self) -> OrcaResultUInt16:
        """Returns the motor's voltage, in millivolts, as measured by the motor's onboard sensor.

        Returns:
            The voltage detected by the motor's onboard sensor.
        """
        ...

    @typing.overload
    def open_serial_port(
        self, port_number: int, baud_rate: int = 19200, interframe_delay: int = 2000
    ) -> OrcaError:
        """Opens serial port using port number.

        Args:
            port_number (int): The port number of the RS422 cable that connects to the desired device.
            baud_rate (int): The speed of data transmission between the connected device and the motor, defaults to 19200 bps.
            interframe_delay (int): The time gap between consecutive frames in a sequence of data, defaults to 2000 microseconds.
        """
        ...

    @typing.overload
    def open_serial_port(
        self, port_path: str, baud_rate: int = 19200, interframe_delay: int = 2000
    ) -> OrcaError:
        """Opens serial port using port path.

        Args:
            port_path (str): The file path of the RS422 cable that connects to the desired device.
            baud_rate (int): The speed of data transmission between the connected device and the motor, defaults to 19200 bps.
            interframe_delay (int): The time gap between consecutive frames in a sequence of data, defaults to 2000 microseconds.
        """
        ...

    def read_multiple_registers_blocking(
        self,
        reg_start_address: int,
        num_registers: int,
        priority: MessagePriority = ...,
    ) -> OrcaResultList:
        """Reads multiple registers from the motor.

        Args:
            reg_start_address (int): The starting register address.
            num_registers (int): How many registers to read.
            priority (enum): Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def read_register_blocking(
        self, reg_address: int, priority: MessagePriority = ...
    ) -> OrcaResultUInt16:
        """Reads a register from the motor.

        Args:
            reg_address (int): The register to read.
            priority (enum): Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def read_wide_register_blocking(
        self, reg_address: int, priority: MessagePriority = ...
    ) -> OrcaResultInt32:
        """Reads a double-wide (32-bit) register from the motor.

        Args:
            reg_address (int): The register to read.
            priority (enum): Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def run(self) -> None:
        """Performs command streaming related work with the ORCA.

        Checks for incoming serial data and sends any queued data.
        If communicating with the motor asynchronously, call this function in a regular loop.
        When using a high-speed stream and no messages are queued, this injects stream commands based on the motor mode set by the most recent call to set_mode().
        """
        ...

    def set_constant_force(self, force: int) -> OrcaError:
        """Sets the constant force value in Haptic Mode.

        Args:
            force (int): Force in millinewtons.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_constant_force_filter(self, force_filter: int) -> OrcaError:
        """Sets the constant force filter value in Haptic Mode.

        Args:
            force_filter (int): Amount to filter the constant force inputs.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_damper(self, damping: int) -> OrcaError:
        """Sets the damping value in Haptic Mode.

        Args:
            damping (int): The damping gain, in 4 Ns/mm.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_inertia(self, inertia: int) -> OrcaError:
        """Sets the inertia value in Haptic Mode.

        Args:
            inertia (int): The inertia gain, in 64 Ns^2/mm.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_kinematic_motion(
        self,
        id: int,
        position: int,
        time: int,
        delay: int,
        type: int,
        auto_next: int,
        next_id: int = -1,
    ) -> OrcaError:
        """Triggers a kinematic motion, and will run any chained motions. This function will only return a result if the motor is in Kinematic mode.

        Args:
            id (int): The ID of the motion to trigger.
            position (int): The position to start at, in micrometers.
            time (int): The duration of the motion, in milliseconds.
            delay (int): The delay following the motion, in milliseconds.
            type (int): 0 = minimizes power, 1 = maximizes smoothness.
            auto_next (int): 0 = stop after the current motion executes, 1 = execute the next motion after the current one finishes.
            next_id (int): Represents the motion that should be completed next, if the previous variable is set to true.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Kinematic Controller for details.
        """
        ...

    def set_max_force(self, max_force: int) -> OrcaError:
        """Sets the maximum force allowed by the motor.

        Args:
            max_force (int): Maximum force in millinewtons.
        """
        ...

    def set_max_power(self, set_max_power: int) -> OrcaError:
        """Sets the maximum power allowed by the motor.

        Args:
            max_power (int): Maximum power in Watts.
        """
        ...

    def set_max_temp(self, max_temp: int) -> OrcaError:
        """Sets the maximum temperature allowed by the motor.

        Args:
            max_temp (int): Maximum temperature in Celsius.
        """
        ...

    def set_mode(self, orca_mode: MotorMode) -> OrcaError:
        """Writes to the ORCA control register to change the motor's mode of operation.
        Also Changes the type of command stream that will be sent during high-speed streaming.
        """
        ...

    def set_osc_effect(
        self,
        osc_id: int,
        amplitude: int,
        frequency_dhz: int,
        duty: int,
        type: OscillatorType,
    ) -> OrcaError:
        """Configures the oscillation effect, based on the provided parameters.

        Args:
            osc_id (int): ID of the oscillation effect.
            amplitude (int): Amplitude of the oscillation effect.
            frequency_dhz (int): Frequency, in decihertz, of the oscillation effect.
            duty (int): Duty-cycle of the oscillation effect. Only relevant for pulse type effects.
            type (OscillatorType): Type of oscillation effect to create. Pulse = 0, is the default,
        """
        ...

    def set_pctrl_tune_softstart(self, t_in_ms: int) -> OrcaError:
        """Sets the fade period when changing the tune of the position controller in miliseconds.

        Args:
            t_in_ms (int): Time period in milliseconds.
        """
        ...

    def set_safety_damping(self, max_safety_damping: int) -> OrcaError:
        """Sets the damping gain value to use when communication is interrupted.

        Args:
            max_safety_damping (int): The maximum safety damping value.
        """
        ...

    def set_spring_effect(
        self,
        spring_id: int,
        gain: int,
        center: int,
        dead_zone: int = 0,
        saturation: int = 0,
        coupling: SpringCoupling = ...,
    ) -> OrcaError:
        """Configures a spring effect, based on the provided parameters.

        Args:
            spring_id (int): The ID of the spring effect to configure.
            gain (int): The gain amount, or force per distance from spring center, for the spring effect.
            center (int): The center of the spring effect.
            dead_zone (int): The radius of the dead zone for the spring. For any position within the radius of the dead zone from the spring center, no spring force will be applied.
            saturation (int): The maximum force that can be applied by the spring.
            coupling (SpringCoupling): The direction from the center where the spring force applies.
            Options include: both (apply force in both directions), positive (apply force in the positive direction only), and negative (apply force in the negative direction only).

        Note:
            Please refer to the ORCA Series Reference Manual, seection Controllers: Haptic Controller for details.
        """
        ...

    def set_streamed_force_mN(self, force: int) -> None:
        """Sets or adjusts the force that the motor exerts when in motor_command stream mode.

        Args:
            force (int): The force in millinewtons.
        """
        ...

    def set_streamed_position_um(self, position: int) -> None:
        """Sets or adjusts the position that the motor is aiming for when in motor_command stream mode.

        Args:
            position (int): The position in micrometers.
        """
        ...

    def time_since_last_response_microseconds(self) -> int:
        """Returns the time, in microseconds, since the last successful message the motor completed.

        Returns:
            Time in microseconds since the last message completed successfully.
        """
        ...

    def trigger_kinematic_motion(self, id: int) -> OrcaError:
        """Triggers the start of a kinematic motion, if the motor is in Kinematic mode, including any chained motions.

        Args:
            id (int): The ID of the motion to be triggered.
        """
        ...

    def tune_position_controller(
        self, pgain: int, igain: int, dvgain: int, sat: int, dgain: int = 0
    ) -> None:
        """Sets the PID controller tuning values for the motor's position controller.

        Args:
            pgain (int): Proportional gain.
            igain (int): Integral gain.
            dvgain (int): Derivative gain with respect to velocy.
            sat (int): Maximum force (set for safety purposes).
            dgain (int): Derivative gain with respect to error.

        Note: The position controller's PID tuning affects the behaviour of the motor in position and kinematic control modes.
        Please refer to the ORCA Series Reference Manual, section Controllers: Position Controller for details.
        """
        ...

    def update_haptic_stream_effects(self, effects: int) -> None:
        """Update which haptic effects will be set through the motor's command frame.

        Args:
            effects (int): The bitmap describing which haptic effects should be enabled or disabled.
        """
        ...

    def write_register_blocking(
        self, reg_address: int, write_data: int, priority: MessagePriority = ...
    ) -> OrcaError:
        """Writes a register value to the motor.

        Args:
            reg_address (int): The register address to write to.
            write_data (int): The data to write to the register.
            priority (MessagePriority): Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def write_wide_register_blocking(
        self, reg_address: int, write_data: int, priority: MessagePriority = ...
    ) -> OrcaError:
        """Writes a double-wide (32-bit) register to the motor.

        Args:
            reg_address (int): The register address to write to.
            write_data (int): The data to write to the register.
            priority (MessagePriority): Whether the message is high-priority - indicated with a 0, or not_important - indicated with a 1.
        """
        ...

    def zero_position(self) -> OrcaError:
        """Sets the motor's zero position to its currently sensed position."""
        ...

    @property
    def name(self) -> str: ...

class HapticEffect:
    """
    Represents a set of predefined haptic effects that can be applied to the motor.

    Members:
      ConstF: Constant force effect.
      Spring0: Spring effect 0.
      Spring1: Spring effect 1.
      Spring2: Spring effect 2.
      Damper: Damping effect; applies a force to reduce the motor's speed of movement.
      Inertia: Inertia effect; applies a force to reduce acceleration of the motor.
      Osc0: Oscillatory effect 0.
      Osc1: Oscillatory effect 1.
    """

    ConstF: typing.ClassVar[HapticEffect]  # value = <HapticEffect.ConstF: 1>
    Damper: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Damper: 16>
    Inertia: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Inertia: 32>
    Osc0: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Osc0: 64>
    Osc1: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Osc1: 128>
    Spring0: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Spring0: 2>
    Spring1: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Spring1: 4>
    Spring2: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Spring2: 8>
    __members__: typing.ClassVar[
        dict[str, HapticEffect]
    ]  # value = {'ConstF': <HapticEffect.ConstF: 1>, 'Spring0': <HapticEffect.Spring0: 2>, 'Spring1': <HapticEffect.Spring1: 4>, 'Spring2': <HapticEffect.Spring2: 8>, 'Damper': <HapticEffect.Damper: 16>, 'Inertia': <HapticEffect.Inertia: 32>, 'Osc0': <HapticEffect.Osc0: 64>, 'Osc1': <HapticEffect.Osc1: 128>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class MessagePriority:
    """
    Represents the priority level of a message.

    Members:
      important: High-priority message.
      not_important: Low-priority message.
    """

    __members__: typing.ClassVar[
        dict[str, MessagePriority]
    ]  # value = {'important': <MessagePriority.important: 0>, 'not_important': <MessagePriority.not_important: 1>}
    important: typing.ClassVar[
        MessagePriority
    ]  # value = <MessagePriority.important: 0>
    not_important: typing.ClassVar[
        MessagePriority
    ]  # value = <MessagePriority.not_important: 1>
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class MotorMode:
    """
    Represents the operating mode of the motor.

    Members:
      AutoZeroMode: Auto Zeroes motor, putting it into a routine that will retract the shaft until reaching a hard stop and set the zero position to that location.
      SleepMode: Force and position commands are ignored. Entering sleep mode will clear persistent errors. 
      ForceMode: Uses the force controller to achieve the commanded force.
      PositionMode: Calculates and applies force to reach positions based on the configured PID tuning, set point, and current shaft position.
      HapticMode: Uses the haptic controller to generate force commands.
      KinematicMode: Uses the kinematic controller to set position targets.
    """

    AutoZeroMode: typing.ClassVar[MotorMode] # value = <MotorMode.AutoZeroMode: 55>
    ForceMode: typing.ClassVar[MotorMode]  # value = <MotorMode.ForceMode: 2>
    HapticMode: typing.ClassVar[MotorMode]  # value = <MotorMode.HapticMode: 4>
    KinematicMode: typing.ClassVar[MotorMode]  # value = <MotorMode.KinematicMode: 5>
    PositionMode: typing.ClassVar[MotorMode]  # value = <MotorMode.PositionMode: 3>
    SleepMode: typing.ClassVar[MotorMode]  # value = <MotorMode.SleepMode: 1>

    __members__: typing.ClassVar[dict[str, MotorMode]]  # value = {'SleepMode': <MotorMode.SleepMode: 1>, 'ForceMode': <MotorMode.ForceMode: 2>, 'PositionMode': <MotorMode.PositionMode: 3>, 'HapticMode': <MotorMode.HapticMode: 4>, 'KinematicMode': <MotorMode.KinematicMode: 5>, <MotorMode.AutoZeroMode: 55>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class OrcaError:
    """To determine if an instance of this type represents an error, convert to a boolean. If the boolean evalues to true, then an error has occured, whose details can be found through the OrcaError.what() function.
    If the conversion evaluates to false, then no error has occured and the operation that returned this type resulted in a success."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __bool__(self) -> bool: ...
    def __init__(self, failure_type: int, error_message: str = "") -> None: ...
    def __repr__(self) -> str: ...
    def what(self) -> str: ...

class OrcaResultInt16:
    """An int value, or an error if an error has occured."""
    error: OrcaError
    value: int
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultInt32:
    """An int value, or an error if an error has occured."""
    error: OrcaError
    value: int
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultList:
    """A list containing integers representing the values returned from the motors, or their errors if an error has occured."""
    error: OrcaError
    value: list[int]
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultMotorMode:
    """Represents the ORCA's operating Mode."""
    error: OrcaError
    value: MotorMode
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultUInt16:
    """An int value, or an error if an error has occured."""
    error: OrcaError
    value: int
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OscillatorType:
    """Represents the shape of the oscillator waveform.

    Members:
      Pulse: Produces a pulse oscillation effect. Requires setting the duty cycle parameter.
      Sine: Produces a sine oscillation effect.
      Triangle: Produces a triangle shaped oscillation effect.
      Saw: Produces a saw shaped oscillation effect.
    """

    Pulse: typing.ClassVar[OscillatorType]  # value = <OscillatorType.Pulse: 0>
    Sine: typing.ClassVar[OscillatorType]  # value = <OscillatorType.Sine: 1>
    __members__: typing.ClassVar[
        dict[str, OscillatorType]
    ]  # value = {'Pulse': <OscillatorType.Pulse: 0>, 'Sine': <OscillatorType.Sine: 1>, 'Triangle ': <OscillatorType.Triangle : 2>, 'Saw  ': <OscillatorType.Saw  : 3>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class SpringCoupling:
    """Valid options for Spring Coupling Settings.

    Members:
      both: Applies spring force in both directions.
      positive: Applies spring force in the positive direction.
      negative: Applies spring force in the negative direction.
    """

    __members__: typing.ClassVar[
        dict[str, SpringCoupling]
    ]  # value = {'both': <SpringCoupling.both: 0>, 'positive': <SpringCoupling.positive: 1>, 'negative ': <SpringCoupling.negative : 2>}
    both: typing.ClassVar[SpringCoupling]  # value = <SpringCoupling.both: 0>
    positive: typing.ClassVar[SpringCoupling]  # value = <SpringCoupling.positive: 1>
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class StreamData:
    errors: int
    force: int
    position: int
    power: int
    temperature: int
    voltage: int
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

ConstF: HapticEffect  # value = <HapticEffect.ConstF: 1>
Damper: HapticEffect  # value = <HapticEffect.Damper: 16>
ForceMode: MotorMode  # value = <MotorMode.ForceMode: 2>
HapticMode: MotorMode  # value = <MotorMode.HapticMode: 4>
Inertia: HapticEffect  # value = <HapticEffect.Inertia: 32>
KinematicMode: MotorMode  # value = <MotorMode.KinematicMode: 5>
Osc0: HapticEffect  # value = <HapticEffect.Osc0: 64>
Osc1: HapticEffect  # value = <HapticEffect.Osc1: 128>
PositionMode: MotorMode  # value = <MotorMode.PositionMode: 3>
Pulse: OscillatorType  # value = <OscillatorType.Pulse: 0>
Sine: OscillatorType  # value = <OscillatorType.Sine: 1>
SleepMode: MotorMode  # value = <MotorMode.SleepMode: 1>
Spring0: HapticEffect  # value = <HapticEffect.Spring0: 2>
Spring1: HapticEffect  # value = <HapticEffect.Spring1: 4>
Spring2: HapticEffect  # value = <HapticEffect.Spring2: 8>
both: SpringCoupling  # value = <SpringCoupling.both: 0>
important: MessagePriority  # value = <MessagePriority.important: 0>
not_important: MessagePriority  # value = <MessagePriority.not_important: 1>
positive: SpringCoupling  # value = <SpringCoupling.positive: 1>

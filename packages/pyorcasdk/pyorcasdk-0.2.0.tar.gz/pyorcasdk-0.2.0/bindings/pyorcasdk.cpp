
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/chrono.h>
#include <pybind11/functional.h>
#include "actuator.h"

namespace py = pybind11;

PYBIND11_MODULE(_pyorcasdk, m)
{
    m.doc() = "Python bindings for the C++ orcaSDK";

     py::class_<orcaSDK::StreamData>(m, "StreamData")
        .def_readwrite("position", &orcaSDK::StreamData::position)
        .def_readwrite("force", &orcaSDK::StreamData::force)
        .def_readwrite("power", &orcaSDK::StreamData::power)
        .def_readwrite("temperature", &orcaSDK::StreamData::temperature)
        .def_readwrite("voltage", &orcaSDK::StreamData::voltage)
        .def_readwrite("errors", &orcaSDK::StreamData::errors);

     py::enum_<orcaSDK::MotorMode>(m, "MotorMode")
        .value("AutoZeroMode", orcaSDK::AutoZeroMode)
        .value("SleepMode", orcaSDK::SleepMode)
        .value("ForceMode", orcaSDK::ForceMode)
        .value("PositionMode", orcaSDK::PositionMode)
        .value("HapticMode", orcaSDK::HapticMode)
        .value("KinematicMode", orcaSDK::KinematicMode)
        .export_values();  // This allows access to the enum values in Python

        
     py::enum_<orcaSDK::Actuator::HapticEffect>(m, "HapticEffect", py::arithmetic())
          .value("ConstF", orcaSDK::Actuator::HapticEffect::ConstF)
          .value("Spring0", orcaSDK::Actuator::HapticEffect::Spring0)
          .value("Spring1", orcaSDK::Actuator::HapticEffect::Spring1)
          .value("Spring2", orcaSDK::Actuator::HapticEffect::Spring2)
          .value("Damper", orcaSDK::Actuator::HapticEffect::Damper)
          .value("Inertia", orcaSDK::Actuator::HapticEffect::Inertia)
          .value("Osc0", orcaSDK::Actuator::HapticEffect::Osc0)
          .value("Osc1", orcaSDK::Actuator::HapticEffect::Osc1)
          .export_values(); // Makes the values accessible directly under HapticEffect

     py::enum_<orcaSDK::Actuator::SpringCoupling>(m, "SpringCoupling")
          .value("both", orcaSDK::Actuator::SpringCoupling::both)
          .value("positive", orcaSDK::Actuator::SpringCoupling::positive)
          .value("negative ", orcaSDK::Actuator::SpringCoupling::negative)
          .export_values(); // Makes the values accessible directly under HapticEffect

     py::enum_<orcaSDK::Actuator::OscillatorType>(m, "OscillatorType")
          .value("Pulse", orcaSDK::Actuator::OscillatorType::Pulse)
          .value("Sine", orcaSDK::Actuator::OscillatorType::Sine)
          .value("Triangle ", orcaSDK::Actuator::OscillatorType::Triangle)
          .value("Saw  ", orcaSDK::Actuator::OscillatorType::Saw)
          .export_values(); // Makes the values accessible directly under HapticEffect

     py::class_<orcaSDK::OrcaError>(m, "OrcaError")
          .def(py::init<int, std::string>(), py::arg("failure_type"), py::arg("error_message") = "")
          .def("__bool__", &orcaSDK::OrcaError::operator bool)
          .def("what", &orcaSDK::OrcaError::what)
          .def("__repr__", [](const orcaSDK::OrcaError& self) {
               return "<OrcaError failure=" + std::to_string(static_cast<bool>(self)) +
                    ", message='" + self.what() + "'>";
          });

            // Bind OrcaResult<int32_t>
     py::class_<orcaSDK::OrcaResult<int32_t>>(m, "OrcaResultInt32")
          //.def(py::init<>())  // Default constructor
          .def_readwrite("value", &orcaSDK::OrcaResult<int32_t>::value)
          .def_readwrite("error", &orcaSDK::OrcaResult<int32_t>::error);

     py::class_<orcaSDK::OrcaResult<int16_t>>(m, "OrcaResultInt16")
          //.def(py::init<>())  // Default constructor
          .def_readwrite("value", &orcaSDK::OrcaResult<int16_t>::value)
          .def_readwrite("error", &orcaSDK::OrcaResult<int16_t>::error);

     py::class_<orcaSDK::OrcaResult<uint16_t>>(m, "OrcaResultUInt16")
          //.def(py::init<>())  // Default constructor
          .def_readwrite("value", &orcaSDK::OrcaResult<uint16_t>::value)
          .def_readwrite("error", &orcaSDK::OrcaResult<uint16_t>::error);

     py::class_<orcaSDK::OrcaResult<std::vector<uint16_t>>>(m, "OrcaResultList")
          //.def(py::init<>())  // Default constructor
          .def_readwrite("value", &orcaSDK::OrcaResult<std::vector<uint16_t>>::value)
          .def_readwrite("error", &orcaSDK::OrcaResult<std::vector<uint16_t>>::error);

     py::class_<orcaSDK::OrcaResult<orcaSDK::MotorMode>>(m, "OrcaResultMotorMode")
          //.def(py::init<>())  // Default constructor
          .def_readwrite("value", &orcaSDK::OrcaResult<orcaSDK::MotorMode>::value)
          .def_readwrite("error", &orcaSDK::OrcaResult<orcaSDK::MotorMode>::error);


    py::enum_<orcaSDK::MessagePriority>(m, "MessagePriority")
        .value("important", orcaSDK::MessagePriority::important)
        .value("not_important", orcaSDK::MessagePriority::not_important)
        .export_values();
    
    py::class_<orcaSDK::Actuator>(m, "Actuator")
        .def(py::init<const char*, uint8_t>(), py::arg("name"), py::arg("modbus_server_address") = 1)

        .def(py::init<std::shared_ptr<orcaSDK::SerialInterface>, std::shared_ptr<orcaSDK::Clock>, const char*, uint8_t>(),

             py::arg("serial_interface"), py::arg("clock"), py::arg("name"), py::arg("modbus_server_address") = 1)

      .def("open_serial_port", 
            // Integer port version
            py::overload_cast<int, int, int>(
                &orcaSDK::Actuator::open_serial_port
            ),
            py::arg("port_number"),
            py::arg("baud_rate") = orcaSDK::Constants::kDefaultBaudRate,
            py::arg("interframe_delay") = orcaSDK::Constants::kDefaultInterframeDelay_uS,
            "Open serial port using port number"
        )
        .def("open_serial_port",
            // String port version
            py::overload_cast<std::string, int, int>(
                &orcaSDK::Actuator::open_serial_port
            ),
            py::arg("port_path"),
            py::arg("baud_rate") = orcaSDK::Constants::kDefaultBaudRate,
            py::arg("interframe_delay") = orcaSDK::Constants::kDefaultInterframeDelay_uS,
            "Open serial port using port path"
        )

        .def("close_serial_port", &orcaSDK::Actuator::close_serial_port)

        .def("get_force_mN", &orcaSDK::Actuator::get_force_mN)

        .def("get_position_um", &orcaSDK::Actuator::get_position_um)

        .def("get_errors", &orcaSDK::Actuator::get_errors)

        .def("set_mode", &orcaSDK::Actuator::set_mode, py::arg("orca_mode"))

        .def("get_mode", &orcaSDK::Actuator::get_mode)

        .def("clear_errors", &orcaSDK::Actuator::clear_errors)

        .def("read_wide_register_blocking", &orcaSDK::Actuator::read_wide_register_blocking,
             py::arg("reg_address"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("read_register_blocking", &orcaSDK::Actuator::read_register_blocking,
             py::arg("reg_address"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("read_multiple_registers_blocking", &orcaSDK::Actuator::read_multiple_registers_blocking,
             py::arg("reg_start_address"), py::arg("num_registers"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("write_register_blocking", &orcaSDK::Actuator::write_register_blocking,
             py::arg("reg_address"), py::arg("write_data"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("write_wide_register_blocking", &orcaSDK::Actuator::write_wide_register_blocking,
             py::arg("reg_address"), py::arg("write_data"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("write_multiple_registers_blocking", &orcaSDK::Actuator::write_multiple_registers_blocking,
             py::arg("reg_start_address"), py::arg("num_registers"), py::arg("write_data"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("read_write_multiple_registers_blocking", &orcaSDK::Actuator::read_write_multiple_registers_blocking,
             py::arg("read_starting_address"), py::arg("read_num_registers"),
             py::arg("write_starting_address"), py::arg("write_num_registers"),
             py::arg("write_data"), py::arg("priority") = orcaSDK::MessagePriority::important)

        .def("begin_serial_logging", py::overload_cast<const std::string&>(&orcaSDK::Actuator::begin_serial_logging),
             py::arg("log_name"))

        .def("begin_serial_logging", py::overload_cast<const std::string&, std::shared_ptr<orcaSDK::LogInterface>>(&orcaSDK::Actuator::begin_serial_logging),
             py::arg("log_name"), py::arg("log"))

        .def("run", &orcaSDK::Actuator::run)

        .def("enable_stream", &orcaSDK::Actuator::enable_stream)

        .def("disable_stream", &orcaSDK::Actuator::disable_stream)

        .def("set_streamed_force_mN", &orcaSDK::Actuator::set_streamed_force_mN, py::arg("force"))

        .def("set_streamed_position_um", &orcaSDK::Actuator::set_streamed_position_um, py::arg("position"))

        .def("update_haptic_stream_effects", &orcaSDK::Actuator::update_haptic_stream_effects, py::arg("effects"))

        .def("get_power_W", &orcaSDK::Actuator::get_power_W)

        .def("get_temperature_C", &orcaSDK::Actuator::get_temperature_C)

        .def("get_voltage_mV", &orcaSDK::Actuator::get_voltage_mV)
        
        .def("zero_position", &orcaSDK::Actuator::zero_position)

        .def("get_latched_errors", &orcaSDK::Actuator::get_latched_errors)

        .def("time_since_last_response_microseconds", &orcaSDK::Actuator::time_since_last_response_microseconds)

        .def("get_stream_data", [](orcaSDK::Actuator& actuator) { return actuator.stream_cache; })

        .def("set_max_force", &orcaSDK::Actuator::set_max_force, py::arg("max_force"))

        .def("set_max_temp", &orcaSDK::Actuator::set_max_temp, py::arg("max_temp"))

        .def("set_max_power", &orcaSDK::Actuator::set_max_power, py::arg("set_max_power"))
        
        .def("set_pctrl_tune_softstart", &orcaSDK::Actuator::set_pctrl_tune_softstart, py::arg("t_in_ms"))

        .def("set_safety_damping", &orcaSDK::Actuator::set_safety_damping, py::arg("max_safety_damping"))

        .def("tune_position_controller", &orcaSDK::Actuator::tune_position_controller, py::arg("pgain"), py::arg("igain"), py::arg("dvgain"), py::arg("sat"), py::arg("dgain") = 0)
        
        .def("set_kinematic_motion", &orcaSDK::Actuator::set_kinematic_motion, py::arg("id"), py::arg("position"), py::arg("time"), py::arg("delay"), py::arg("type"), py::arg("auto_next"), py::arg("next_id") = -1)

        .def("trigger_kinematic_motion", &orcaSDK::Actuator::trigger_kinematic_motion, py::arg("id"))

        .def("enable_haptic_effects", &orcaSDK::Actuator::enable_haptic_effects, py::arg("effects"))

        .def("set_spring_effect", &orcaSDK::Actuator::set_spring_effect, py::arg("spring_id"), py::arg("gain"), py::arg("center"), py::arg("dead_zone") = 0, py::arg("saturation ") = 0, py::arg("coupling") = orcaSDK::Actuator::SpringCoupling::both)

        .def("set_osc_effect", &orcaSDK::Actuator::set_osc_effect, py::arg("osc_id"), py::arg("amplitude"), py::arg("frequency_dhz"), py::arg("duty"), py::arg("type "))

        .def("set_damper", &orcaSDK::Actuator::set_damper, py::arg("damping"))

        .def("set_inertia", &orcaSDK::Actuator::set_inertia, py::arg("inertia"))

        .def("set_constant_force", &orcaSDK::Actuator::set_constant_force, py::arg("force"))

        .def("set_constant_force_filter", &orcaSDK::Actuator::set_constant_force_filter, py::arg("force_filter"))

        .def("get_serial_number", &orcaSDK::Actuator::get_serial_number)

        .def("get_major_version", &orcaSDK::Actuator::get_major_version)

        .def("get_release_state", &orcaSDK::Actuator::get_release_state)

        .def("get_revision_number", &orcaSDK::Actuator::get_revision_number)

        .def_readonly("name", &orcaSDK::Actuator::name);

}

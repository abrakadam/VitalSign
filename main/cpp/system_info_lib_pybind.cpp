#include "system_info_lib.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(system_info_cpp, m) {
    m.doc() = "C++ System Information Library";
    
    py::class_<SystemInfo::HardwareInfo>(m, "HardwareInfo")
        .def(py::init<>())
        .def_readwrite("system_vendor", &SystemInfo::HardwareInfo::system_vendor)
        .def_readwrite("product_name", &SystemInfo::HardwareInfo::product_name)
        .def_readwrite("product_version", &SystemInfo::HardwareInfo::product_version)
        .def_readwrite("board_vendor", &SystemInfo::HardwareInfo::board_vendor)
        .def_readwrite("board_name", &SystemInfo::HardwareInfo::board_name)
        .def_readwrite("bios_vendor", &SystemInfo::HardwareInfo::bios_vendor)
        .def_readwrite("bios_version", &SystemInfo::HardwareInfo::bios_version)
        .def_readwrite("bios_date", &SystemInfo::HardwareInfo::bios_date)
        .def_readwrite("cpu_model", &SystemInfo::HardwareInfo::cpu_model)
        .def_readwrite("total_memory", &SystemInfo::HardwareInfo::total_memory);
    
    py::class_<SystemInfo::OSInfo>(m, "OSInfo")
        .def(py::init<>())
        .def_readwrite("system", &SystemInfo::OSInfo::system)
        .def_readwrite("release", &SystemInfo::OSInfo::release)
        .def_readwrite("version", &SystemInfo::OSInfo::version)
        .def_readwrite("machine", &SystemInfo::OSInfo::machine)
        .def_readwrite("hostname", &SystemInfo::OSInfo::hostname)
        .def_readwrite("distribution", &SystemInfo::OSInfo::distribution)
        .def_readwrite("kernel_version", &SystemInfo::OSInfo::kernel_version);
    
    py::class_<SystemInfo::EnvironmentInfo>(m, "EnvironmentInfo")
        .def(py::init<>())
        .def_readwrite("desktop_environment", &SystemInfo::EnvironmentInfo::desktop_environment)
        .def_readwrite("display_server", &SystemInfo::EnvironmentInfo::display_server)
        .def_readwrite("shell", &SystemInfo::EnvironmentInfo::shell)
        .def_readwrite("window_manager", &SystemInfo::EnvironmentInfo::window_manager);
    
    py::class_<SystemInfo::BootloaderInfo>(m, "BootloaderInfo")
        .def(py::init<>())
        .def_readwrite("name", &SystemInfo::BootloaderInfo::name)
        .def_readwrite("path", &SystemInfo::BootloaderInfo::path)
        .def_readwrite("active", &SystemInfo::BootloaderInfo::active);
    
    py::class_<SystemInfo::SystemInfoLib>(m, "SystemInfoLib")
        .def(py::init<>())
        .def("get_hardware_info", &SystemInfo::SystemInfoLib::get_hardware_info)
        .def("get_os_info", &SystemInfo::SystemInfoLib::get_os_info)
        .def("get_environment_info", &SystemInfo::SystemInfoLib::get_environment_info)
        .def("get_bootloaders", &SystemInfo::SystemInfoLib::get_bootloaders)
        .def("get_installed_os", &SystemInfo::SystemInfoLib::get_installed_os)
        .def("get_bios_info", &SystemInfo::SystemInfoLib::get_bios_info)
        .def("get_drivers", &SystemInfo::SystemInfoLib::get_drivers)
        .def("get_serial_number", &SystemInfo::SystemInfoLib::get_serial_number);
}

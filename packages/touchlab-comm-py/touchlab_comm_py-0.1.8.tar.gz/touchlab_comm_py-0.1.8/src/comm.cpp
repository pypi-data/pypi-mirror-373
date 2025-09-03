// Copyright (c) 2025 Touchlab Limited. All Rights Reserved
// Unauthorized copying or modifications of this file, via any medium is strictly prohibited.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <touchlab_comm/touchlab_comm.hpp>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;
using touchlab_comm::TouchlabComms;

PYBIND11_MODULE(touchlab_comm_py, m)
{
#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif

  py::class_<TouchlabComms>(m, "TouchlabComms", "TouchlabComms wrapper")
    .def(py::init(), "Constructs TouchlabComms object")
    .def("init", &TouchlabComms::init, py::arg("file_name") = "", "Initialise sensor comms")
    .def("connect", &TouchlabComms::connect, py::arg("port"), "Connects to the sensor")
    .def("read", [](TouchlabComms* instance, long timeout) {
      std::vector<double> ret;
      ret.reserve(100);
      instance->read(ret, timeout);
      return ret;}, py::arg("timeout") = 500, "Reads and returns data")
    .def("read_raw", [](TouchlabComms* instance, long timeout) {
      std::vector<double> ret;
      ret.reserve(100);
      instance->read_raw(ret, timeout);
      return ret;}, py::arg("timeout") = 500, "Reads and returns raw data")
    .def("read_register", [](TouchlabComms* instance, uint16_t address, uint16_t id, long timeout) {
      std::vector<uint8_t> ret;
      ret.reserve(256);
      instance->read_register(address, id, ret, timeout);
      std::string_view content{reinterpret_cast<char*>(ret.data()), ret.size()};
      return py::bytes(content);}, py::arg("address"), py::arg("id"), py::arg("timeout") = 500,
      "Reads register data")
    .def("write_register", [](TouchlabComms* instance, uint16_t address, uint16_t id,
      py::bytes data, long timeout) {
        std::string_view content{data};
        std::vector<uint8_t> data_(content.data(), content.data() + content.size());
        instance->write_register(address, id, data_, timeout);},
        py::arg("address"), py::arg("id"), py::arg("data"), py::arg("timeout") = 500,
        "Writes register data")
    .def("is_connected", &TouchlabComms::is_connected, "Is sensor connected?")
    .def("zero", py::overload_cast<const std::vector<int>&>(&TouchlabComms::zero),
      "Zeroes the sensor", py::arg("taxel_ids"))
    .def("zero", py::overload_cast<const std::vector<std::vector<double>>&,
      const std::vector<int>&>(&TouchlabComms::zero), "Zeroes the sensor with data from a buffer",
      py::arg("data_buf"), py::arg("taxel_ids"))
    .def_property_readonly_static("version", [](py::object) {
      return TouchlabComms::get_version(); }, "Returns the version string");
}

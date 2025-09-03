// Copyright (c) 2025 Touchlab Limited. All Rights Reserved
// Unauthorized copying or modifications of this file, via any medium is strictly prohibited.

#ifndef TOUCHLAB_COMM__TOUCHLAB_COMM_HPP_
#define TOUCHLAB_COMM__TOUCHLAB_COMM_HPP_

#include <map>
#include <memory>
#include <string>
#include <vector>

/**
 * \mainpage Touchlab Driver
 *
 * ## Overview
 * The Touchlab Driver Library provides an interface for communicating with Touchlab sensors.
 * It supports reading raw and calibrated data, managing sensor offsets,
 * and configuring the sensors. The library is a cross-paltform C++ library
 * that works on both Linux and Windows operating systems.
 * The library is designed to be easy to use and integrate into new and existing projects.
 * All functionality is exposed through API implemented in a single class,
 * \link touchlab_comm::TouchlabComms TouchlabComms \endlink.
 *
 * For an example of how to use this library, see the
 * \htmlonly <a href="example_8cpp_source.html">example code</a> \endhtmlonly.
 *
 * ## Dependencies
 * The depends only on the C++ standard library:
 * - Linux: `glibc >= 2.31`
 * - Windows: `MSVC >= 2015`
 *
 */

namespace touchlab_comm
{
/**
 * @class TouchlabComms touchlab_comm.hpp touchlab_comm/touchlab_comm.hpp
 * @brief Touchlab communication main class.
 *
 */
class TouchlabComms
{
public:
  /**
   * @brief Construct a new Touchlab Comms object
   *
   */
  TouchlabComms();

  /**
   * @brief Destroy the Touchlab Comms object
   *
   */
  virtual ~TouchlabComms();

  /**
   * @brief Init comm
   *
   * @param filename path to the sensor param binary file
   */
  void init(const std::string & filename = "");

  /**
   * @brief Connect to the sensor
   *
   * @param port Serial port name, e.g. `COM1`, or `/dev/ttyACM0`.
   *
   */
  void connect(const std::string & port);

  /**
   * @brief Read raw signal
   *
   * @param data Returned raw data vector from the latest data packet
   * @param timeout Timeout in ms
   */
  void read_raw(std::vector<double> & data, int64_t timeout = 500.0);

  /**
   * @brief Read calibrated data
   *
   * @param data Return data calibrated by the model defined by the SensorParameters class
   * @param timeout Timeout in ms
   */
  void read(std::vector<double> & data, int64_t timeout = 500.0);

  /**
   * @brief Read a value of a register
   * This method is not intended for end users and it will fail with an exception.
   *
   * @param device Device ID
   * @param reg Register address
   * @param data Output data vector
   * @param timeout Timeout in ms
   */
  void read_register(uint16_t device, uint16_t reg, std::vector<uint8_t> & data,
    int64_t timeout = 500.0);

  /**
   * @brief Write a value to a register
   * This method is not intended for end users and it will fail with an exception.
   *
   * @param device Device ID
   * @param reg Register address
   * @param data Data vector to write
   * @param timeout Timeout in ms
   */
  void write_register(uint16_t device, uint16_t reg, const std::vector<uint8_t> & data,
    int64_t timeout = 500.0);

  /**
   * @brief Get the version of the API
   *
   * @return std::string Version string
   */
  static std::string get_version();

  /**
   * @brief Returns if the sensor is connected and communicating
   *
   * @return std::string True if connected
   */
  bool is_connected();

  /**
   * @brief Zero out sensor offset
   *
   * @param ind Optional vector of sensor indices to zero out. If empty, all taxels will be zeroed.
   */
  void zero(const std::vector<int>& ind = {});

  /**
   * @brief Zero out sensor offset with custom data
   *
   * @param data Custom data used to zero the sensor. Inner vector should have one element for each taxel. The outer vector should contain n samples of input data.
   * @param ind Optional vector of sensor indices to zero out. If empty, all taxels will be zeroed.
   */
  void zero(const std::vector<std::vector<double>>& data, const std::vector<int>& ind = {});

  /**
   * @brief Translate raw data sample into calibrated values
   *
   * @param raw Input raw data
   * @param calibrated Output calibrated data
   */
  void translate(const std::vector<double>& raw, std::vector<double>& calibrated);

private:
  class Implementation;
  std::unique_ptr<Implementation> impl_;
};

}  // namespace touchlab_comm

#endif  // TOUCHLAB_COMM__TOUCHLAB_COMM_HPP_

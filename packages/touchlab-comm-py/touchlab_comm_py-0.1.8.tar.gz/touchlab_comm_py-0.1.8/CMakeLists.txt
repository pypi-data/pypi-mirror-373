cmake_minimum_required(VERSION 3.15.0)
project(touchlab_comm_py)

set(TOUCHLAB_COMM_VERSION 0.1.8)

find_package(Python COMPONENTS Interpreter Development)
add_subdirectory(pybind11)

option(INSTALL_NATIVE "Install into root of the install directory" OFF)

include_directories(
  include
)

pybind11_add_module(touchlab_comm_py src/comm.cpp)
set_property(TARGET touchlab_comm_py PROPERTY CXX_STANDARD 17)
set_property(TARGET touchlab_comm_py PROPERTY CXX_STANDARD_REQUIRED ON)
target_link_libraries(touchlab_comm_py PRIVATE pybind11::module)
if(APPLE)
  # OSX not supported
  message(FATAL_ERROR "Mac is not supported")
elseif(UNIX)
  # If unix
  message(STATUS "Linking linux library")
  target_link_libraries(touchlab_comm_py PRIVATE ${CMAKE_CURRENT_LIST_DIR}/lib/libtouchlab_comm_static.a)
else()
  # If windows
  message(STATUS "Linking windows library")
  target_link_libraries(touchlab_comm_py PRIVATE ${CMAKE_CURRENT_LIST_DIR}/lib/touchlab_comm_static.lib)
endif()
set_property(TARGET touchlab_comm_py PROPERTY POSITION_INDEPENDENT_CODE ON)
target_compile_definitions(touchlab_comm_py PRIVATE VERSION_INFO=${TOUCHLAB_COMM_VERSION})

if (INSTALL_NATIVE)
  install(TARGETS touchlab_comm_py DESTINATION ${PROJECT_NAME})
  install(DIRECTORY examples/
        DESTINATION ${PROJECT_NAME}/examples/
      )
else()
  install(TARGETS touchlab_comm_py DESTINATION lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages)
  install(DIRECTORY examples/
        DESTINATION share/${PROJECT_NAME}/examples/
      )
endif()


if (MSVC)
    macro(append_cxx_flag text)
        foreach (flag
            CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
            CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)

            string(APPEND ${flag} " ${text}")

        endforeach()
    endmacro()
    append_cxx_flag("/Zc:preprocessor")
endif()

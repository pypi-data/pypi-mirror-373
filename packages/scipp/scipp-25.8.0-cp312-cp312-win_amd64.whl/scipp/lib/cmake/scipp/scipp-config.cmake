# ~~~
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
# ~~~

####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was scipp-config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

# Call find_package(scipp ... COMPONENTS conan-config) to use conan for
# install of dependencies. Then call a second time without COMPONENTS to
# get the actual package, with dependencies. If system dependencies should
# be used instead the call with "conan-config" can be omitted.
if(scipp_FIND_COMPONENTS)
  foreach(_comp ${scipp_FIND_COMPONENTS})
    if (NOT _comp STREQUAL "conan-config")
      message(FATAL_ERROR "bad")
    endif()
  endforeach()
  include("${CMAKE_CURRENT_LIST_DIR}/scipp-conan.cmake")
else()
  include("${CMAKE_CURRENT_LIST_DIR}/scipp-targets.cmake")

  check_required_components(scipp-targets)

  include(CMakeFindDependencyMacro)
  find_dependency(Boost 1.69)
  find_dependency(Eigen3)
  find_dependency(LLNL-Units)
  find_dependency(TBB)
endif()


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was metatensor-config.in.cmake                            ########

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

cmake_minimum_required(VERSION 3.16)

include(FindPackageHandleStandardArgs)

if(metatensor_FOUND)
    return()
endif()

enable_language(CXX)

get_filename_component(METATENSOR_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

if (WIN32)
    set(METATENSOR_SHARED_LOCATION ${METATENSOR_PREFIX_DIR}/bin/libmetatensor.so)
    set(METATENSOR_IMPLIB_LOCATION ${METATENSOR_PREFIX_DIR}/lib/libmetatensor.so.lib)
else()
    set(METATENSOR_SHARED_LOCATION ${METATENSOR_PREFIX_DIR}/lib/libmetatensor.so)
endif()

set(METATENSOR_STATIC_LOCATION ${METATENSOR_PREFIX_DIR}/lib/libmetatensor.a)
set(METATENSOR_INCLUDE ${METATENSOR_PREFIX_DIR}/include/)

if (NOT EXISTS ${METATENSOR_INCLUDE}/metatensor.h OR NOT EXISTS ${METATENSOR_INCLUDE}/metatensor.hpp)
    message(FATAL_ERROR "could not find metatensor headers in '${METATENSOR_INCLUDE}', please re-install metatensor")
endif()


# Shared library target
if (OFF OR ON)
    if (NOT EXISTS ${METATENSOR_SHARED_LOCATION})
        message(FATAL_ERROR "could not find metatensor library at '${METATENSOR_SHARED_LOCATION}', please re-install metatensor")
    endif()

    add_library(metatensor::shared SHARED IMPORTED)
    set_target_properties(metatensor::shared PROPERTIES
        IMPORTED_LOCATION ${METATENSOR_SHARED_LOCATION}
        INTERFACE_INCLUDE_DIRECTORIES ${METATENSOR_INCLUDE}
        BUILD_VERSION "0.1.17"
    )

    target_compile_features(metatensor::shared INTERFACE cxx_std_11)

    if (WIN32)
        if (NOT EXISTS ${METATENSOR_IMPLIB_LOCATION})
            message(FATAL_ERROR "could not find metatensor library at '${METATENSOR_IMPLIB_LOCATION}', please re-install metatensor")
        endif()

        set_target_properties(metatensor::shared PROPERTIES
            IMPORTED_IMPLIB ${METATENSOR_IMPLIB_LOCATION}
        )
    endif()
endif()


# Static library target
if (OFF OR NOT ON)
    if (NOT EXISTS ${METATENSOR_STATIC_LOCATION})
        message(FATAL_ERROR "could not find metatensor library at '${METATENSOR_STATIC_LOCATION}', please re-install metatensor")
    endif()

    add_library(metatensor::static STATIC IMPORTED)
    set_target_properties(metatensor::static PROPERTIES
        IMPORTED_LOCATION ${METATENSOR_STATIC_LOCATION}
        INTERFACE_INCLUDE_DIRECTORIES ${METATENSOR_INCLUDE}
        INTERFACE_LINK_LIBRARIES "gcc_s;util;rt;pthread;m;dl;c"
        BUILD_VERSION "0.1.17"
    )

    target_compile_features(metatensor::static INTERFACE cxx_std_11)
endif()

if (${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.18")
    # Export either the shared or static library as the metatensor target
    # This requires cmake 3.18+ to use ALIAS for non-GLOBAL IMPORTED targets
    if (ON)
        add_library(metatensor ALIAS metatensor::shared)
    else()
        add_library(metatensor ALIAS metatensor::static)
    endif()
endif()


if (ON)
    find_package_handle_standard_args(metatensor DEFAULT_MSG METATENSOR_SHARED_LOCATION METATENSOR_INCLUDE)
else()
    find_package_handle_standard_args(metatensor DEFAULT_MSG METATENSOR_STATIC_LOCATION METATENSOR_INCLUDE)
endif()

# Config file for the metkit package
# Defines the following variables:
#
#  metkit_FEATURES       - list of enabled features
#  metkit_VERSION        - version of the package
#  metkit_GIT_SHA1       - Git revision of the package
#  metkit_GIT_SHA1_SHORT - short Git revision of the package
#


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was project-config.cmake.in                            ########

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

### computed paths
set_and_check(metkit_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib64/cmake/metkit")
set_and_check(metkit_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(METKIT_CMAKE_DIR ${metkit_CMAKE_DIR})
  set(METKIT_BASE_DIR ${metkit_BASE_DIR})
endif()

### export version info
set(metkit_VERSION           "1.14.4")
set(metkit_GIT_SHA1          "f7e645d0f89c1f10aba00142c10d161c3e50d021")
set(metkit_GIT_SHA1_SHORT    "f7e645d")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(METKIT_VERSION           "1.14.4" )
  set(METKIT_GIT_SHA1          "f7e645d0f89c1f10aba00142c10d161c3e50d021" )
  set(METKIT_GIT_SHA1_SHORT    "f7e645d" )
endif()

### has this configuration been exported from a build tree?
set(metkit_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(METKIT_IS_BUILD_DIR_EXPORT ${metkit_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${metkit_CMAKE_DIR}/metkit-import.cmake)
  set(metkit_IMPORT_FILE "${metkit_CMAKE_DIR}/metkit-import.cmake")
  include(${metkit_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT metkit_BINARY_DIR)
  find_file(metkit_TARGETS_FILE
    NAMES metkit-targets.cmake
    HINTS ${metkit_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(metkit_TARGETS_FILE)
    include(${metkit_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${metkit_CMAKE_DIR}/metkit-post-import.cmake)
  set(metkit_POST_IMPORT_FILE "${metkit_CMAKE_DIR}/metkit-post-import.cmake")
  include(${metkit_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(METKIT_LIBRARIES         "")
  set(METKIT_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(metkit_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(metkit_IMPORT_FILE)
  set(METKIT_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(METKIT_IMPORT_FILE)
endif()

### export features and check requirements
set(metkit_FEATURES "TESTS;PKGCONFIG;BUILD_TOOLS;GRIB;BUFR;METKIT_CONFIG;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(METKIT_FEATURES ${metkit_FEATURES})
endif()
foreach(_f ${metkit_FEATURES})
  set(metkit_${_f}_FOUND 1)
  set(metkit_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(METKIT_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(metkit)

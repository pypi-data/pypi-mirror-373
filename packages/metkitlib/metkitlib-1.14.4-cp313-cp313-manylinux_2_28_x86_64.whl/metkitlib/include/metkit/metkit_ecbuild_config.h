/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef METKIT_ecbuild_config_h
#define METKIT_ecbuild_config_h

/* ecbuild info */

#ifndef ECBUILD_VERSION_STR
#define ECBUILD_VERSION_STR "3.11.0"
#endif
#ifndef ECBUILD_VERSION
#define ECBUILD_VERSION "3.11.0"
#endif
#ifndef ECBUILD_MACROS_DIR
#define ECBUILD_MACROS_DIR  "/src/ecbuild/cmake"
#endif

/* config info */

#define METKIT_OS_NAME          "Linux-4.18.0-372.26.1.el8_6.x86_64"
#define METKIT_OS_BITS          64
#define METKIT_OS_BITS_STR      "64"
#define METKIT_OS_STR           "linux.64"
#define METKIT_OS_VERSION       "4.18.0-372.26.1.el8_6.x86_64"
#define METKIT_SYS_PROCESSOR    "x86_64"

#define METKIT_BUILD_TIMESTAMP  "20250902153143"
#define METKIT_BUILD_TYPE       "RelWithDebInfo"

#define METKIT_C_COMPILER_ID      "GNU"
#define METKIT_C_COMPILER_VERSION "13.3.1"

#define METKIT_CXX_COMPILER_ID      "GNU"
#define METKIT_CXX_COMPILER_VERSION "13.3.1"

#define METKIT_C_COMPILER       "/opt/rh/gcc-toolset-13/root/usr/bin/cc"
#define METKIT_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define METKIT_CXX_COMPILER     "/opt/rh/gcc-toolset-13/root/usr/bin/c++"
#define METKIT_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define METKIT_INSTALL_DIR       "/tmp/metkit/target/metkit"
#define METKIT_INSTALL_BIN_DIR   "/tmp/metkit/target/metkit/bin"
#define METKIT_INSTALL_LIB_DIR   "/tmp/metkit/target/metkit/lib64"
#define METKIT_INSTALL_DATA_DIR  "/tmp/metkit/target/metkit/share/metkit"

#define METKIT_DEVELOPER_SRC_DIR "/src/proj"
#define METKIT_DEVELOPER_BIN_DIR "/tmp/metkit/build"

/* Fortran support */

#if 0

#define METKIT_Fortran_COMPILER_ID      ""
#define METKIT_Fortran_COMPILER_VERSION ""

#define METKIT_Fortran_COMPILER "/opt/intel/oneapi/compiler/latest/bin/ifx"
#define METKIT_Fortran_FLAGS    ""

#endif

#endif /* METKIT_ecbuild_config_h */

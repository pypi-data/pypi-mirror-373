#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "metkit" for configuration "RelWithDebInfo"
set_property(TARGET metkit APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(metkit PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libmetkit.dylib"
  IMPORTED_SONAME_RELWITHDEBINFO "@rpath/libmetkit.dylib"
  )

list(APPEND _cmake_import_check_targets metkit )
list(APPEND _cmake_import_check_files_for_metkit "${_IMPORT_PREFIX}/lib/libmetkit.dylib" )

# Import target "parse-mars-request" for configuration "RelWithDebInfo"
set_property(TARGET parse-mars-request APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(parse-mars-request PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/parse-mars-request"
  )

list(APPEND _cmake_import_check_targets parse-mars-request )
list(APPEND _cmake_import_check_files_for_parse-mars-request "${_IMPORT_PREFIX}/bin/parse-mars-request" )

# Import target "bufr-sanity-check" for configuration "RelWithDebInfo"
set_property(TARGET bufr-sanity-check APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(bufr-sanity-check PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/bufr-sanity-check"
  )

list(APPEND _cmake_import_check_targets bufr-sanity-check )
list(APPEND _cmake_import_check_files_for_bufr-sanity-check "${_IMPORT_PREFIX}/bin/bufr-sanity-check" )

# Import target "mars-archive-script" for configuration "RelWithDebInfo"
set_property(TARGET mars-archive-script APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(mars-archive-script PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/mars-archive-script"
  )

list(APPEND _cmake_import_check_targets mars-archive-script )
list(APPEND _cmake_import_check_files_for_mars-archive-script "${_IMPORT_PREFIX}/bin/mars-archive-script" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

set( metkit_HAVE_GRIB True )
set( metkit_HAVE_ODB  0  )

include( CMakeFindDependencyMacro )

find_dependency( eckit HINTS ${CMAKE_CURRENT_LIST_DIR}/../eckit /tmp/metkit/prereqs/eckitlib/lib64/cmake/eckit )

if( metkit_HAVE_GRIB )
  find_dependency( eccodes HINTS ${CMAKE_CURRENT_LIST_DIR}/../eccodes  )
endif()

if( metkit_HAVE_ODB )
  find_dependency( odc HINTS ${CMAKE_CURRENT_LIST_DIR}/../odc odc_DIR-NOTFOUND )
endif()

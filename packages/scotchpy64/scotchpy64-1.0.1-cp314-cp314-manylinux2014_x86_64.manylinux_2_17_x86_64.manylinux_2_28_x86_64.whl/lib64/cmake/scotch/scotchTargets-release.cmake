#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCOTCH::scotch" for configuration "Release"
set_property(TARGET SCOTCH::scotch APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(SCOTCH::scotch PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libscotch.so.7.0.9"
  IMPORTED_SONAME_RELEASE "libscotch.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::scotch )
list(APPEND _cmake_import_check_files_for_SCOTCH::scotch "${_IMPORT_PREFIX}/lib64/libscotch.so.7.0.9" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

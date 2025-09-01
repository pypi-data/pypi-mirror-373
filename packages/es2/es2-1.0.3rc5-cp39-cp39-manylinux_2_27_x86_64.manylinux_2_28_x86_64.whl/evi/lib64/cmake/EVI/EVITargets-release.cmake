#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "EVI::EVI" for configuration "Release"
set_property(TARGET EVI::EVI APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(EVI::EVI PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libEVI.so"
  IMPORTED_SONAME_RELEASE "libEVI.so"
  )

list(APPEND _cmake_import_check_targets EVI::EVI )
list(APPEND _cmake_import_check_files_for_EVI::EVI "${_IMPORT_PREFIX}/lib64/libEVI.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

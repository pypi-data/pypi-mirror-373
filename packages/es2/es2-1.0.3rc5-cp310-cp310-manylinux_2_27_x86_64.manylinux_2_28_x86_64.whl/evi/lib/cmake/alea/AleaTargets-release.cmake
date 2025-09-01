#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "alea::alea" for configuration "Release"
set_property(TARGET alea::alea APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(alea::alea PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libalea.a"
  )

list(APPEND _cmake_import_check_targets alea::alea )
list(APPEND _cmake_import_check_files_for_alea::alea "${_IMPORT_PREFIX}/lib/libalea.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

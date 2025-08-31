#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "nmodl::nmodl" for configuration "Release"
set_property(TARGET nmodl::nmodl APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nmodl::nmodl PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/neuron/.data/bin/nmodl"
  )

list(APPEND _cmake_import_check_targets nmodl::nmodl )
list(APPEND _cmake_import_check_files_for_nmodl::nmodl "${_IMPORT_PREFIX}/neuron/.data/bin/nmodl" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

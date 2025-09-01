#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "nvf_cutlass" for configuration "Release"
set_property(TARGET nvf_cutlass APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nvf_cutlass PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "torch;c10"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libnvf_cutlass.so"
  IMPORTED_SONAME_RELEASE "libnvf_cutlass.so"
  )

list(APPEND _cmake_import_check_targets nvf_cutlass )
list(APPEND _cmake_import_check_files_for_nvf_cutlass "${_IMPORT_PREFIX}/lib/libnvf_cutlass.so" )

# Import target "nvfuser_codegen" for configuration "Release"
set_property(TARGET nvfuser_codegen APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nvfuser_codegen PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libnvfuser_codegen.so"
  IMPORTED_SONAME_RELEASE "libnvfuser_codegen.so"
  )

list(APPEND _cmake_import_check_targets nvfuser_codegen )
list(APPEND _cmake_import_check_files_for_nvfuser_codegen "${_IMPORT_PREFIX}/lib/libnvfuser_codegen.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

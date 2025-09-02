#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "power_grid_model::power_grid_model_c" for configuration "Release"
set_property(TARGET power_grid_model::power_grid_model_c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(power_grid_model::power_grid_model_c PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/power_grid_model_c.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/power_grid_model_c.dll"
  )

list(APPEND _cmake_import_check_targets power_grid_model::power_grid_model_c )
list(APPEND _cmake_import_check_files_for_power_grid_model::power_grid_model_c "${_IMPORT_PREFIX}/lib/power_grid_model_c.lib" "${_IMPORT_PREFIX}/bin/power_grid_model_c.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

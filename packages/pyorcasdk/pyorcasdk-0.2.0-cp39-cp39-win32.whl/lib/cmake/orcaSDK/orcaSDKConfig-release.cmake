#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "orcaSDK::core" for configuration "Release"
set_property(TARGET orcaSDK::core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(orcaSDK::core PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/orcaSDK_core.lib"
  )

list(APPEND _cmake_import_check_targets orcaSDK::core )
list(APPEND _cmake_import_check_files_for_orcaSDK::core "${_IMPORT_PREFIX}/lib/orcaSDK_core.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

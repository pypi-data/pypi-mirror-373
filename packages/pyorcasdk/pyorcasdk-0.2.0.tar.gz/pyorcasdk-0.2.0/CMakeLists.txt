cmake_minimum_required(VERSION 3.17...3.27)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  DESCRIPTION "C++ bindings for Iris Dynamics orcaSDK"
  LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(FetchContent)

FetchContent_Declare(
  orcaSDK
  GIT_REPOSITORY https://github.com/IrisDynamics/orcaSDK.git
  GIT_TAG main
)

FetchContent_MakeAvailable(orcaSDK)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    add_compile_options(-fPIC)
    set_target_properties(orcaSDK_core PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()

add_subdirectory(extern/pybind11 pybind11)

pybind11_add_module(_pyorcasdk
    SHARED
    bindings/pyorcasdk.cpp
) 

target_link_libraries(_pyorcasdk PRIVATE orcaSDK::core)

set_target_properties(_pyorcasdk PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/_pyorcasdk"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/_pyorcasdk"
)

install(TARGETS _pyorcasdk DESTINATION ${SKBUILD_PROJECT_NAME})
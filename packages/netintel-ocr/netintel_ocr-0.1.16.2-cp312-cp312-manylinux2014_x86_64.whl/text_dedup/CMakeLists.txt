cmake_minimum_required(VERSION 3.12)
project(netintel_ocr_dedup_core)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(pybind11 REQUIRED)

# Find OpenMP (optional)
find_package(OpenMP)

# Set optimization flags
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# Platform-specific flags
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
endif()

# Add source files
set(SOURCES
    dedup_cpp/simhash.cpp
    dedup_cpp/cdc.cpp
    python_bindings.cpp
)

# Create the module
pybind11_add_module(dedup_core ${SOURCES})

# Add OpenMP if found
if(OpenMP_CXX_FOUND)
    target_link_libraries(dedup_core PRIVATE OpenMP::OpenMP_CXX)
    target_compile_definitions(dedup_core PRIVATE USE_OPENMP)
endif()

# Set properties
target_compile_features(dedup_core PRIVATE cxx_std_14)
set_target_properties(dedup_core PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    INTERPROCEDURAL_OPTIMIZATION TRUE
)
cmake_minimum_required(VERSION 3.12)
project(netintel_ocr_dedup_core)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Try to find Python executable from environment or CMake variables
if(DEFINED Python_EXECUTABLE)
    set(PYTHON_EXECUTABLE ${Python_EXECUTABLE})
endif()

if(NOT PYTHON_EXECUTABLE)
    find_package(Python COMPONENTS Interpreter Development REQUIRED)
    set(PYTHON_EXECUTABLE ${Python_EXECUTABLE})
endif()

# Find pybind11 using Python
execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE pybind11_not_found
)

if(pybind11_not_found)
    message(FATAL_ERROR "pybind11 not found. Please install it with: pip install pybind11")
endif()

message(STATUS "Found pybind11 at: ${pybind11_DIR}")
list(APPEND CMAKE_PREFIX_PATH "${pybind11_DIR}")
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
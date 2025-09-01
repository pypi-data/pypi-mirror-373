#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

// Include the actual implementations
#include "dedup_cpp/simhash.cpp"
#include "dedup_cpp/cdc.cpp"

namespace py = pybind11;

// Check if OpenMP is available at runtime
bool openmp_available() {
#ifdef USE_OPENMP
    return true;
#else
    return false;
#endif
}

PYBIND11_MODULE(dedup_core, m) {
    m.doc() = "NetIntel-OCR C++ Deduplication Core";
    
    // Module-level functions
    m.def("_openmp_available", &openmp_available, 
          "Check if OpenMP is available");
    
    // SimHash class
    py::class_<SimHash>(m, "SimHash")
        .def(py::init<int>(), py::arg("bits") = 64)
        .def("compute", [](SimHash& self, const std::string& text) {
            auto fp = self.compute(text);
            return py::bytes(reinterpret_cast<const char*>(fp.data()), fp.size());
        }, py::arg("text"), "Compute SimHash fingerprint")
        .def_static("hamming_distance", [](const py::bytes& fp1, const py::bytes& fp2) {
            std::string s1 = fp1;
            std::string s2 = fp2;
            std::vector<uint8_t> v1(s1.begin(), s1.end());
            std::vector<uint8_t> v2(s2.begin(), s2.end());
            return SimHash::hamming_distance(v1, v2);
        }, py::arg("fp1"), py::arg("fp2"), 
        "Calculate Hamming distance between two fingerprints");
    
    // CDC class
    py::class_<CDC>(m, "CDC")
        .def(py::init<size_t>(), py::arg("chunk_size") = 1024)
        .def("chunk", [](CDC& self, const py::bytes& data) {
            std::string s = data;
            std::vector<uint8_t> v(s.begin(), s.end());
            auto chunks = self.chunk(v);
            
            py::list result;
            for (const auto& chunk : chunks) {
                result.append(py::bytes(
                    reinterpret_cast<const char*>(chunk.data()), 
                    chunk.size()
                ));
            }
            return result;
        }, py::arg("data"), "Split data into content-defined chunks")
        .def("deduplicate", [](CDC& self, const py::list& chunks) {
            std::vector<std::vector<uint8_t>> chunk_vec;
            for (auto item : chunks) {
                std::string s = py::cast<py::bytes>(item);
                chunk_vec.emplace_back(s.begin(), s.end());
            }
            
            auto [unique, reduction] = self.deduplicate(chunk_vec);
            
            py::list unique_list;
            for (const auto& chunk : unique) {
                unique_list.append(py::bytes(
                    reinterpret_cast<const char*>(chunk.data()), 
                    chunk.size()
                ));
            }
            
            return py::make_tuple(unique_list, reduction);
        }, py::arg("chunks"), 
        "Deduplicate chunks and return unique chunks with reduction percentage");
    
    // Version information
    m.attr("__version__") = "1.0.0";
    
#ifdef __AVX2__
    m.attr("has_avx2") = true;
#else
    m.attr("has_avx2") = false;
#endif
    
#ifdef USE_OPENMP
    m.attr("has_openmp") = true;
#else  
    m.attr("has_openmp") = false;
#endif
}
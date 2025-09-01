/**
 * @file bindings.cpp
 * @brief Python bindings for the noLZSS factorization library.
 *
 * This file contains the Python bindings for the non-overlapping Lempel-Ziv-Storer-Szymanski
 * factorization algorithm. The bindings provide both in-memory and file-based factorization
 * capabilities with proper GIL management for performance.
 *
 * The module exposes the following functions:
 * - factorize(): Factorize in-memory text
 * - factorize_file(): Factorize text from file
 * - count_factors(): Count factors in text
 * - count_factors_file(): Count factors in file
 * - write_factors_binary_file(): Write factors to binary file
 *
 * All functions require input data to end with '$' sentinel for correct factorization.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/pytypes.h>
#include <string>
#include <string_view>
#include <stdexcept>
#include "factorizer.hpp"
#include "version.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_noLZSS, m) {
    m.doc() = "Non-overlapping Lempel-Ziv-Storer-Szymanski factorization\n\n"
              "This module provides efficient text factorization using compressed suffix trees.\n"
              "All input strings and files must end with '$' sentinel for correct results.";

    // Factor class documentation
    py::class_<noLZSS::Factor>(m, "Factor", "Represents a single factorization factor with start position and length")
        .def_readonly("start", &noLZSS::Factor::start, "Starting position of the factor in the original text")
        .def_readonly("length", &noLZSS::Factor::length, "Length of the factor substring");

    // factorize function documentation
    m.def("factorize", [](py::buffer b) {
        // Accept any bytes-like 1-byte-per-item contiguous buffer (e.g. bytes, bytearray, memoryview)
        py::buffer_info info = b.request();
        if (info.itemsize != 1) {
            throw std::invalid_argument("factorize: buffer must be a bytes-like object with itemsize==1");
        }
        if (info.ndim != 1) {
            throw std::invalid_argument("factorize: buffer must be a 1-dimensional bytes-like object");
        }

        const char* data = static_cast<const char*>(info.ptr);
        std::string_view sv(data, static_cast<size_t>(info.size));

        // Release GIL while doing heavy C++ work
        py::gil_scoped_release release;
        auto factors = noLZSS::factorize(sv);
        py::gil_scoped_acquire acquire;

        py::list out;
        for (auto &f : factors) out.append(py::make_tuple(f.start, f.length));
        return out;
    }, py::arg("data"), R"doc(Factorize a text string into LZSS factors.

This is the main factorization function for in-memory text processing.
It accepts any Python bytes-like object and returns a list of (start, length) tuples.

Args:
    data: Python bytes-like object containing text that must end with '$' sentinel

Returns:
    List of (start, length) tuples representing the factorization

Raises:
    ValueError: if data is not a valid bytes-like object

Note:
    The input data must end with '$' sentinel for correct factorization.
    GIL is released during computation for better performance with large data.
)doc");

    // factorize_file function documentation
    m.def("factorize_file", [](const std::string& path, size_t reserve_hint) {
        // Release GIL while doing heavy C++ work
        py::gil_scoped_release release;
        auto factors = noLZSS::factorize_file(path, reserve_hint);
        py::gil_scoped_acquire acquire;

        py::list out;
        for (auto &f : factors) out.append(py::make_tuple(f.start, f.length));
        return out;
    }, py::arg("path"), py::arg("reserve_hint") = 0, R"doc(Factorize text from file into LZSS factors.

Reads text from a file and performs factorization. This is more memory-efficient
for large files as it avoids loading the entire file into memory.

Args:
    path: Path to input file containing text that must end with '$' sentinel
    reserve_hint: Optional hint for reserving space in output vector (0 = no hint)

Returns:
    List of (start, length) tuples representing the factorization

Note:
    The file content must end with '$' sentinel for correct factorization.
    Use reserve_hint for better performance when you know approximate factor count.
)doc");

    // count_factors function documentation
    m.def("count_factors", [](py::buffer b) {
        // Accept any bytes-like 1-byte-per-item contiguous buffer
        py::buffer_info info = b.request();
        if (info.itemsize != 1) {
            throw std::invalid_argument("count_factors: buffer must be a bytes-like object with itemsize==1");
        }
        if (info.ndim != 1) {
            throw std::invalid_argument("count_factors: buffer must be a 1-dimensional bytes-like object");
        }

        const char* data = static_cast<const char*>(info.ptr);
        std::string_view sv(data, static_cast<size_t>(info.size));

        // Release GIL while doing heavy C++ work
        py::gil_scoped_release release;
        size_t count = noLZSS::count_factors(sv);
        py::gil_scoped_acquire acquire;

        return count;
    }, py::arg("data"), R"doc(Count number of LZSS factors in text.

This is a memory-efficient alternative to factorize() when you only need
the count of factors rather than the factors themselves.

Args:
    data: Python bytes-like object containing text that must end with '$' sentinel

Returns:
    Number of factors in the factorization

Note:
    The input data must end with '$' sentinel for correct factorization.
    GIL is released during computation for better performance with large data.
)doc");

    // count_factors_file function documentation
    m.def("count_factors_file", [](const std::string& path) {
        // Release GIL while doing heavy C++ work
        py::gil_scoped_release release;
        size_t count = noLZSS::count_factors_file(path);
        py::gil_scoped_acquire acquire;

        return count;
    }, py::arg("path"), R"doc(Count number of LZSS factors in a file.

Reads text from a file and counts factors without storing them.
This is the most memory-efficient way to get factor counts for large files.

Args:
    path: Path to input file containing text that must end with '$' sentinel

Returns:
    Number of factors in the factorization

Note:
    The file content must end with '$' sentinel for correct factorization.
    GIL is released during computation for better performance.
)doc");

    // write_factors_binary_file function documentation
    m.def("write_factors_binary_file", [](const std::string& in_path, const std::string& out_path, bool assume_has_sentinel) {
        // Release GIL while doing heavy C++ work
        py::gil_scoped_release release;
        size_t count = noLZSS::write_factors_binary_file(in_path, out_path, assume_has_sentinel);
        py::gil_scoped_acquire acquire;

        return count;
    }, py::arg("in_path"), py::arg("out_path"), py::arg("assume_has_sentinel") = false, R"doc(Write LZSS factors from file to binary output file.

Reads text from an input file, performs factorization, and writes the factors
in binary format to an output file. Each factor is written as two uint64_t values.

Args:
    in_path: Path to input file containing text that must end with '$' sentinel
    out_path: Path to output file where binary factors will be written
    assume_has_sentinel: Unused parameter (kept for API consistency)

Returns:
    Number of factors written to the output file

Note:
    The input file content must end with '$' sentinel for correct factorization.
    Binary format: each factor is 16 bytes (2 × uint64_t: start, length).
    This function overwrites the output file if it exists.
)doc");

    // Version information
    m.attr("__version__") = std::to_string(noLZSS::VERSION_MAJOR) + "." + std::to_string(noLZSS::VERSION_MINOR) + "." + std::to_string(noLZSS::VERSION_PATCH);
}

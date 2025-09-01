#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/compatibility.hpp>

#include <amulet/zlib/zlib.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_module(py::module m)
{
    pyext::init_compiler_config(m);

    py::register_exception<Amulet::zlib::ZipBombException>(m, "ZipBombException");

    m.def(
        "get_max_decompression_size",
        &Amulet::zlib::get_max_decompression_size,
        py::doc("Get the configured maximum decompressed size in bytes. (Default 100MB)"));
    m.def(
        "set_max_decompression_size",
        &Amulet::zlib::set_max_decompression_size,
        py::doc(
            "Set the configured maximum decompressed size in bytes.\n"
            "If decompression requires more memory than this it will raise ZipBombException."));

    m.def(
        "decompress_zlib_gzip",
        [](py::bytes src) {
            std::string dst;
            {
                py::gil_scoped_release nogil;
                Amulet::zlib::decompress_zlib_gzip(src, dst);
            }
            return py::bytes(dst);
        },
        py::doc(
            "Decompress a bytes object compressed with either zlib or gzip.\n"
            "Raises ZipBombException if decompression requires more than the configured maximum decompression size."));
    m.def(
        "compress_zlib",
        [](py::bytes src) {
            std::string dst;
            {
                py::gil_scoped_release nogil;
                Amulet::zlib::compress_zlib(src, dst);
            }
            return py::bytes(dst);
        },
        py::doc("Compress a bytes object using the zlib compression format."));
    m.def(
        "compress_gzip",
        [](py::bytes src) {
        std::string dst;
        {
            py::gil_scoped_release nogil;
            Amulet::zlib::compress_gzip(src, dst);
        }
        return py::bytes(dst); },
        py::doc("Compress a bytes object using the gzip compression format."));
}

PYBIND11_MODULE(_amulet_zlib, m)
{
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}

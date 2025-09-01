#pragma once

#include <stdexcept>
#include <string>
#include <string_view>

#include <amulet/zlib/export.hpp>

namespace Amulet {
namespace zlib {

    class AMULET_ZLIB_EXPORT_EXCEPTION ZipBombException : public std::runtime_error {
    public:
        using std::runtime_error::runtime_error;
    };

    // Get the configured maximum decompressed size in bytes. (Default 100MB)
    AMULET_ZLIB_EXPORT size_t get_max_decompression_size();

    // Set the configured maximum decompressed size in bytes.
    // If decompression requires more memory than this it will raise ZipBombException.
    AMULET_ZLIB_EXPORT void set_max_decompression_size(size_t);

    // Decompress zlib or gzip compressed data from src into dst.
    // Throws ZipBombException if decompression requires more than the configured maximum decompression size.
    AMULET_ZLIB_EXPORT void decompress_zlib_gzip(const std::string_view src, std::string& dst);

    // Compress the data in src in zlib format and append to dst.
    AMULET_ZLIB_EXPORT void compress_zlib(const std::string_view src, std::string& dst);

    // Compress the data in src in gzip format and append to dst.
    AMULET_ZLIB_EXPORT void compress_gzip(const std::string_view src, std::string& dst);

} // namespace zlib
} // namespace Amulet

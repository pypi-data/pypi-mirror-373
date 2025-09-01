#include <string>
#include <string_view>

#include "image.hpp"

// TODO: switch to #embed

constexpr char _missing_no[] = { -119, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 16, 0, 0, 0, 16, 8, 2, 0, 0, 0, -112, -111, 104, 54, 0, 0, 0, 9, 112, 72, 89, 115, 0, 0, 11, 19, 0, 0, 11, 19, 1, 0, -102, -100, 24, 0, 0, 0, 7, 116, 73, 77, 69, 7, -29, 7, 12, 11, 32, 47, -106, -14, 86, 62, 0, 0, 0, 29, 105, 84, 88, 116, 67, 111, 109, 109, 101, 110, 116, 0, 0, 0, 0, 0, 67, 114, 101, 97, 116, 101, 100, 32, 119, 105, 116, 104, 32, 71, 73, 77, 80, 100, 46, 101, 7, 0, 0, 0, 38, 73, 68, 65, 84, 40, -49, 99, -4, -63, -16, -125, 1, 27, -32, 96, -32, -64, 42, -50, -60, 64, 34, 24, -43, 64, 12, 96, -60, 37, -127, 43, 126, 70, -125, -107, 38, 26, 0, 18, -81, 4, 15, -103, -42, 104, -28, 0, 0, 0, 0, 73, 69, 78, 68, -82, 66, 96, -126 };
constexpr std::string_view missing_no(_missing_no, sizeof(_missing_no));

namespace PIL {
namespace Image {
    bool is_image(py::handle obj)
    {
        py::object ImageCls = py::module::import("PIL.Image").attr("Image");
        py::object isinstance = py::module::import("builtins").attr("isinstance");
        return isinstance(obj, ImageCls).cast<bool>();
    }

    size_t Image::get_width() const
    {
        return attr("width").cast<size_t>();
    }

    size_t Image::get_height() const
    {
        return attr("height").cast<size_t>();
    }

    std::string Image::get_mode() const
    {
        return attr("mode").cast<std::string>();
    }

    py::buffer Image::get_buffer() const
    {
        return *this;
    }

    Image open(const std::filesystem::path& path)
    {
        return py::module::import("PIL.Image").attr("open")(path.string());
    }

    Image load(std::string_view data)
    {
        py::bytes py_data(data);
        auto f = py::module::import("io").attr("BytesIO")(py_data);
        return py::module::import("PIL.Image").attr("open")(f);
    }

} // namespace Image
} // namespace PIL

namespace Amulet {

PIL::Image::Image get_missing_no_icon()
{
    return PIL::Image::load(missing_no);
}

} // namespace Amulet


use std::cell::RefCell;
use std::path::Path;

#[macro_use]
extern crate cpython;

use cpython::{PyResult, PyObject};

use image::{
    ImageBuffer, RgbaImage,
    Rgba,
};

mod rect;
mod drawing;

use rect::Rect;
use drawing::{
    clear,
    draw_filled_rect_mut,
};

py_module_initializer!(rasterizer, initrasterizer, PyInit_rasterizer, |py, m| {
    m.add(py, "__doc__", "Rasterizer module implemented in Rust")?;

    m.add_class::<PyImage>(py)?;

    Ok(())
});

py_class!(class PyImage |py| {
    data img: RefCell<RgbaImage>;

    def __new__(_cls, width: u32, height: u32, background: (u8, u8, u8, u8) = (0, 0, 0, 255)) -> PyResult<PyImage> {
        let img = ImageBuffer::from_pixel(width, height, Rgba([background.0, background.1, background.2, background.3]));

        PyImage::create_instance(py, RefCell::new(img))
    }

    def width(&self) -> PyResult<u32> {
        let img = self.img(py).borrow();

        Ok(img.width())
    }

    def height(&self) -> PyResult<u32> {
        let img = self.img(py).borrow();

        Ok(img.height())
    }

    @staticmethod
    def load(filename: String) -> PyResult<PyImage> {
        let img = image::open(filename).unwrap();
        let img = img.to_rgba();

        PyImage::create_instance(py, RefCell::new(img))
    }

    def save(&self, filename: String) -> PyResult<PyObject> {
        let img = self.img(py).borrow();

        img.save(&Path::new(&filename)).unwrap();

        Ok(py.None())
    }

    def clear(&self, fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        let mut img = self.img(py).borrow_mut();

        clear(&mut img, Rgba([fill.0, fill.1, fill.2, fill.3]));

        Ok(py.None())
    }

    def draw_rect(&self, rect: (i32, i32, u32, u32), fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        let mut img = self.img(py).borrow_mut();

        draw_filled_rect_mut(&mut img, &Rect::new(rect.0, rect.1, rect.2, rect.3), Rgba([fill.0, fill.1, fill.2, fill.3]));

        Ok(py.None())
    }
});


use std::cell;
use std::path::Path;

#[macro_use]
extern crate cpython;

use cpython::{PyResult, PyObject};

mod rasterizer;
use rasterizer::{Color, Image};

py_module_initializer!(rasterizer, initrasterizer, PyInit_rasterizer, |py, m| {
    m.add(py, "__doc__", "Rasterizer module implemented in Rust")?;

    m.add_class::<TImage>(py)?;

    Ok(())
});

py_class!(class TImage |py| {
    data img: cell::RefCell<Image>;

    def __new__(_cls, width: u32, height: u32, background: (u8, u8, u8, u8)) -> PyResult<TImage> {
        TImage::create_instance(py, cell::RefCell::new(Image::new(width, height, Color(background.0, background.1, background.2, background.3))))
    }

    def save(&self, filename: String) -> PyResult<PyObject> {
        self.img(py).borrow().save(&Path::new(&filename));

        Ok(py.None())
    }

    def clear(&self, fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        self.img(py).borrow_mut().clear(Color(fill.0, fill.1, fill.2, fill.3));

        Ok(py.None())
    }

    def draw_rect(&self, rect: (i32, i32, i32, i32), fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        self.img(py).borrow_mut().draw_rect(rect, Color(fill.0, fill.1, fill.2, fill.3));

        Ok(py.None())
    }

    def draw_line(&self, line: (i32, i32, i32, i32), color: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        self.img(py).borrow_mut().draw_line(line, Color(color.0, color.1, color.2, color.3));

        Ok(py.None())
    }
});

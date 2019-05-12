
use std::cell::RefCell;
use std::path::Path;
use std::fs::File;
use std::io::Read;

#[macro_use]
extern crate cpython;

use cpython::{PyResult, PyObject};

use image::{
    RgbaImage,
    Rgba,
};

use rusttype::{FontCollection, Font, Scale, point};

mod rect;
mod drawing;

use rect::Rect;
use drawing::{
    clear,
    draw_filled_rect_mut,
    draw_image_mut,
    draw_text_mut,
    draw_line_segment_mut,
    draw_filled_circle_mut,
    draw_filled_ellipse_mut,
};

py_module_initializer!(rasterizer, initrasterizer, PyInit_rasterizer, |py, m| {
    m.add(py, "__doc__", "Rasterizer module implemented in Rust")?;

    m.add_class::<PyImage>(py)?;
    m.add_class::<PyFont>(py)?;

    Ok(())
});

py_class!(class PyImage |py| {
    data img: RefCell<RgbaImage>;

    def __new__(_cls, width: u32, height: u32, background: (u8, u8, u8, u8) = (0, 0, 0, 255)) -> PyResult<PyImage> {
        // let img = RgbaImage::new(width, height);
        let img = RgbaImage::from_pixel(width, height, Rgba([background.0, background.1, background.2, background.3]));

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

    def draw_image(&self, rect: (i32, i32, u32, u32), image: &PyImage) -> PyResult<PyObject> {
        let img1 = self.img(py);
        let img2 = image.img(py);

        let same = (img1 as *const _) == (img2 as *const _);

        let mut img1 = img1.borrow_mut();

        if same {
            let img2 = img1.clone();

            draw_image_mut(&mut img1, &Rect::new(rect.0, rect.1, rect.2, rect.3), &img2);
        } else {
            let img2 = img2.borrow();

            draw_image_mut(&mut img1, &Rect::new(rect.0, rect.1, rect.2, rect.3), &img2);
        }

        Ok(py.None())
    }

    def draw_text(&self, top_left: (i32, i32), text: &str, font: &PyFont, size: f32, fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        let mut img = self.img(py).borrow_mut();

        let font = font.font(py).borrow();
        let scale = Scale::uniform(size);

        draw_text_mut(&mut img, top_left, text, &font, scale, Rgba([fill.0, fill.1, fill.2, fill.3]));

        Ok(py.None())
    }

    def draw_line(&self, start: (i32, i32), end: (i32, i32), color: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        let mut img = self.img(py).borrow_mut();

        draw_line_segment_mut(&mut img, start, end, Rgba([color.0, color.1, color.2, color.3]));

        Ok(py.None())
    }

    def draw_circle(&self, center: (i32, i32), radius: u32, fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        let mut img = self.img(py).borrow_mut();

        draw_filled_circle_mut(&mut img, center, radius, Rgba([fill.0, fill.1, fill.2, fill.3]));

        Ok(py.None())
    }

    def draw_ellipse(&self, center: (i32, i32), radius: (u32, u32), fill: (u8, u8, u8, u8)) -> PyResult<PyObject> {
        let mut img = self.img(py).borrow_mut();

        draw_filled_ellipse_mut(&mut img, center, radius, Rgba([fill.0, fill.1, fill.2, fill.3]));

        Ok(py.None())
    }
});

py_class!(class PyFont |py| {
    data font: RefCell<Font<'static>>;

    @staticmethod
    def load(filename: String) -> PyResult<PyFont> {
        let mut file = File::open(filename).unwrap();
        let mut data = Vec::new();

        file.read_to_end(&mut data).unwrap();

        let font = FontCollection::from_bytes(data).unwrap().into_font().unwrap();

        PyFont::create_instance(py, RefCell::new(font))
    }

    def measure_line(&self, text: &str, size: f32) -> PyResult<(u32, u32)> {
        let font = self.font(py).borrow();
        let scale = Scale::uniform(size);

        let v_metrics = font.v_metrics(scale);
        let glyphs: Vec<_> = font
            .layout(text, scale, point(0.0, v_metrics.ascent))
            .collect();

        let glyphs_height = (v_metrics.ascent - v_metrics.descent).ceil() as u32;

        let glyphs_width = {
            let min_x = glyphs
                .first()
                .map(|g| g.pixel_bounding_box().unwrap().min.x)
                .unwrap();
            let max_x = glyphs
                .last()
                .map(|g| g.pixel_bounding_box().unwrap().max.x)
                .unwrap();
            (max_x - min_x) as u32
        };

        Ok((glyphs_width, glyphs_height))
    }
});

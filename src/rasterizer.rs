
use std::path::Path;

extern crate image;

#[derive(Copy, Clone, Debug)]
pub struct Color(pub u8, pub u8, pub u8, pub u8);

impl Color {
    fn blend(&self, other: Color) -> Color {
        let ba = self.3 as f32 / 255.0;
        let fa = other.3 as f32 / 255.0;
        let a = 1.0 - (1.0 - fa) * (1.0 - ba);

        let r = other.0 as f32 * fa / a + self.0 as f32 * ba * (1.0 - fa) / a;
        let g = other.1 as f32 * fa / a + self.1 as f32 * ba * (1.0 - fa) / a;
        let b = other.2 as f32 * fa / a + self.2 as f32 * ba * (1.0 - fa) / a;

        let r = r.max(0.0).min(255.0) as u8;
        let g = g.max(0.0).min(255.0) as u8;
        let b = b.max(0.0).min(255.0) as u8;
        let a = (a * 255.0) as u8;

        Color(r, g, b, a)
    }
}

#[derive(Debug)]
pub struct Image {
    width: u32,
    height: u32,
    data: Vec<Color>,
}

impl Image {
    pub fn new(width: u32, height: u32, background: Color) -> Image {
        let size = (width * height) as usize;
        let data = vec![background; size];

        Image {
            width: width,
            height: height,
            data: data,
        }
    }

    pub fn save(&self, filename: &Path) {
        let size = self.width as usize * self.height as usize * 4usize;

        let view = self.data.as_ptr() as *const _ as *const u8;
        let data: &[u8] = unsafe {
            std::slice::from_raw_parts(view, size)
        };

        image::save_buffer(filename, data, self.width, self.height, image::RGBA(8)).unwrap();
    }

    pub fn clear(&mut self, color: Color) {
        let w = self.width as usize;
        let h = self.height as usize;

        for y in 0..h {
            for x in 0..w {
                self.data[x + y * w] = color;
            }
        }
    }

    pub fn draw_rect(&mut self, rect: (i32, i32, i32, i32), fill: Color) {
        if fill.3 == 0 {
            return;
        }

        let (x, y, w, h) = rect;
        let (x2, y2) = (x + w, y + h);

        if (x2 <= 0) || (y2 <= 0) {
            return;
        }

        let x = x.max(0) as usize;
        let y = y.max(0) as usize;

        let x2 = x2.min(self.width as i32) as usize;
        let y2 = y2.min(self.height as i32) as usize;

        let area = (x2 - x) * (y2 - y);

        if area <= 0 {
            return;
        }

        let h = self.height as usize;

        if fill.3 == 255 {
            for y in y..y2 {
                for x in x..x2 {
                    self.data[x + y * h] = fill;
                }
            }
        } else {
            for y in y..y2 {
                for x in x..x2 {
                    self.data[x + y * h] = self.data[x + y * h].blend(fill);
                }
            }
        }
    }
}


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

    pub fn get_pixel(&self, x: usize, y: usize) -> &Color {
        &self.data[x + y * self.width as usize]
    }

    pub fn get_pixel_mut(&mut self, x: usize, y: usize) -> &mut Color {
        &mut self.data[x + y * self.width as usize]
    }

    pub fn set_pixel(&mut self, x: usize, y: usize, pixel: Color) {
        *self.get_pixel_mut(x, y) = pixel;
    }

    pub fn set_pixel_blend(&mut self, x: usize, y: usize, pixel: Color) {
        let p = self.get_pixel_mut(x, y);

        if pixel.3 == 255 {
            *p = pixel;
        } else {
            *p = p.blend(pixel);
        }
    }

    pub fn contains(&self, x: usize, y: usize) -> bool {
        (x < self.width as usize) &&
        (y < self.height as usize)
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

    // Bresenham's line algorithm
    pub fn draw_line(&mut self, line: (i32, i32, i32, i32), color: Color) {
        if color.3 == 0 {
            return;
        }

        let (mut x0, mut y0, x1, y1) = line;

        let dx =  (x1 - x0).abs();
        let dy = -(y1 - y0).abs();

        let sx = if x0 < x1 { 1 } else { -1 };
        let sy = if y0 < y1 { 1 } else { -1 };

        let mut err = dx + dy;
        let mut err2;

        loop {
            let (x, y) = (x0 as usize, y0 as usize);

            if self.contains(x, y) {
                self.set_pixel_blend(x, y, color);
            }

            if (x0 == x1) && (y0 == y1) {
                break;
            }

            err2 = err * 2;

            if err2 >= dy {
                err += dy;
                x0 += sx;
            }

            if err2 <= dx {
                err += dx;
                y0 += sy;
            }
        }
    }
}

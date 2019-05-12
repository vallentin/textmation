
use image::{
    GenericImage, GenericImageView,
    RgbaImage,
    Rgba,
    imageops::resize,
    imageops::FilterType,
};

use rusttype::{
    FontCollection,
    Font,
    Scale,
    point,
};

use crate::rect::Rect;

#[inline(always)]
fn in_bounds(image: &RgbaImage, x: i32, y: i32) -> bool {
    (x >= 0) && (y >= 0) && (x < (image.width() as i32)) && (y < (image.height() as i32))
}

#[inline(always)]
unsafe fn unsafe_put_pixel_blend(image: &mut RgbaImage, x: u32, y: u32, pixel: Rgba<u8>) {
    let current = image.unsafe_get_pixel(x as u32, y as u32);
    image.unsafe_put_pixel(x as u32, y as u32, blend_color(current, pixel));
}

#[inline(always)]
fn put_pixel_if_in_bounds(image: &mut RgbaImage, x: i32, y: i32, pixel: Rgba<u8>) {
    if in_bounds(image, x, y) {
        unsafe {
            image.unsafe_put_pixel(x as u32, y as u32, pixel);
        }
    }
}

#[inline(always)]
fn put_pixel_blend_if_in_bounds(image: &mut RgbaImage, x: i32, y: i32, pixel: Rgba<u8>) {
    if in_bounds(image, x, y) {
        unsafe {
            unsafe_put_pixel_blend(image, x as u32, y as u32, pixel);
        }
    }
}

pub fn blend_color(back: Rgba<u8>, front: Rgba<u8>) -> Rgba<u8> {
    let [br, bg, bb, ba] = back.data;
    let [fr, fg, fb, fa] = front.data;

    let ba = (ba as f32) / 255.0;
    let fa = (fa as f32) / 255.0;

    let a = 1.0 - (1.0 - fa) * (1.0 - ba);

    let r = fr as f32 * fa / a + br as f32 * ba * (1.0 - fa) / a;
    let g = fg as f32 * fa / a + bg as f32 * ba * (1.0 - fa) / a;
    let b = fb as f32 * fa / a + bb as f32 * ba * (1.0 - fa) / a;

    let r = r.max(0.0).min(255.0) as u8;
    let g = g.max(0.0).min(255.0) as u8;
    let b = b.max(0.0).min(255.0) as u8;
    let a = (a * 255.0) as u8;

    Rgba([r, g, b, a])
}

pub fn clear(image: &mut RgbaImage, color: Rgba<u8>) {
    for pixel in image.pixels_mut() {
        *pixel = color;
    }
}

pub fn draw_filled_rect_mut(image: &mut RgbaImage, rect: &Rect, fill: Rgba<u8>) {
    let alpha = fill.data[3];

    if alpha == 0 {
        return;
    }

    let image_bounds = Rect::new(0, 0, image.width(), image.height());
    let intersection = image_bounds.intersect(rect);

    if intersection.is_empty() {
        return;
    }

    if alpha == 255 {
        for y in intersection.top..=intersection.bottom() {
            for x in intersection.left..=intersection.right() {
                unsafe {
                    image.unsafe_put_pixel(x as u32, y as u32, fill);
                }
            }
        }
    } else {
        for y in intersection.top..=intersection.bottom() {
            for x in intersection.left..=intersection.right() {
                unsafe {
                    unsafe_put_pixel_blend(image, x as u32, y as u32, fill);
                }
            }
        }
    }
}

pub fn draw_image_at(image: &mut RgbaImage, top_left: (i32, i32), other: &RgbaImage) {
    let (left, top) = top_left;

    let image_bounds = Rect::new(0, 0, image.width(), image.height());
    let other_bounds = Rect::new(left, top, other.width(), other.height());
    let intersection = image_bounds.intersect(&other_bounds);

    if intersection.is_empty() {
        return;
    }

    for y in 0..intersection.height {
        for x in 0..intersection.width {
            unsafe {
                let front = other.unsafe_get_pixel(x, y);

                let x = (left as u32) + x;
                let y = (top as u32) + y;

                let back  = image.unsafe_get_pixel(x, y);

                image.unsafe_put_pixel(x, y, blend_color(back, front));
            }
        }
    }
}

pub fn draw_image_mut(image: &mut RgbaImage, rect: &Rect, other: &RgbaImage) {
    let image_bounds = Rect::new(0, 0, image.width(), image.height());
    let intersection = image_bounds.intersect(rect);

    if intersection.is_empty() {
        return;
    }

    if (rect.width != other.width()) || (rect.height != other.height()) {
        // TODO: Sample instead of resizing
        let other = resize(other, rect.width, rect.height, FilterType::Triangle);
        draw_image_at(image, (rect.left, rect.top), &other);
    } else {
        draw_image_at(image, (rect.left, rect.top), other);
    }
}

pub fn draw_text_mut(image: &mut RgbaImage, top_left: (i32, i32), text: &str, font: &Font, scale: Scale, fill: Rgba<u8>) {
    let (x, y) = top_left;
    let [r, g, b, a] = fill.data;

    if a == 0 {
        return;
    }

    let v_metrics = font.v_metrics(scale);
    let glyphs: Vec<_> = font
        .layout(text, scale, point(0.0, v_metrics.ascent))
        .collect();

    let min_x = glyphs
        .first()
        .map(|g| g.pixel_bounding_box().unwrap().min.x)
        .unwrap();

    let x = x - min_x;
    let a = a as f32;

    for glyph in glyphs {
        if let Some(bounding_box) = glyph.pixel_bounding_box() {
            glyph.draw(|gx, gy, v| {
                let x = x + bounding_box.min.x + gx as i32;
                let y = y + bounding_box.min.y + gy as i32;

                if in_bounds(image, x, y) {
                    unsafe {
                        unsafe_put_pixel_blend(image, x as u32, y as u32, Rgba([r, g, b, (v * a) as u8]));
                    }
                }
            });
        }
    }
}

pub fn draw_line_segment_mut(image: &mut RgbaImage, start: (i32, i32), end: (i32, i32), fill: Rgba<u8>) {
    let alpha = fill.data[3];

    if alpha == 0 {
        return;
    }

    let (mut x0, mut y0) = start;
    let (x1, y1) = end;

    let dx =  (x1 - x0).abs();
    let dy = -(y1 - y0).abs();

    let sx = if x0 < x1 { 1 } else { -1 };
    let sy = if y0 < y1 { 1 } else { -1 };

    let mut err = dx + dy;
    let mut err2;

    if alpha == 255 {
        loop {
            put_pixel_if_in_bounds(image, x0, y0, fill);

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
    } else {
        loop {
            put_pixel_blend_if_in_bounds(image, x0, y0, fill);

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

pub fn draw_filled_circle_mut(image: &mut RgbaImage, center: (i32, i32), radius: u32, fill: Rgba<u8>) {
    let alpha = fill.data[3];

    if alpha == 0 {
        return;
    }

    let (cx, cy) = center;

    let image_bounds = Rect::new(0, 0, image.width(), image.height());
    let circle_bounds = Rect::from_min_max(
        cx - radius as i32, cy - radius as i32,
        cx + radius as i32, cy + radius as i32);

    let intersection = image_bounds.intersect(&circle_bounds);

    if intersection.is_empty() {
        return;
    }

    let radius_squared = (radius * radius) as f32;

    if alpha == 255 {
        for py in intersection.top..=intersection.bottom() {
            let y = ((py - cy) as f32) + 0.5;

            for px in intersection.left..=intersection.right() {
                let x = ((px - cx) as f32) + 0.5;

                if (x * x + y * y) <= radius_squared {
                    unsafe {
                        image.unsafe_put_pixel(px as u32, py as u32, fill);
                    }
                }
            }
        }
    } else {
        for py in intersection.top..=intersection.bottom() {
            let y = ((py - cy) as f32) + 0.5;

            for px in intersection.left..=intersection.right() {
                let x = ((px - cx) as f32) + 0.5;

                if (x * x + y * y) <= radius_squared {
                    unsafe {
                        unsafe_put_pixel_blend(image, px as u32, py as u32, fill);
                    }
                }
            }
        }
    }
}

pub fn draw_filled_ellipse_mut(image: &mut RgbaImage, center: (i32, i32), radius: (u32, u32), fill: Rgba<u8>) {
    let alpha = fill.data[3];

    if alpha == 0 {
        return;
    }

    let (cx, cy) = center;

    let (radius_x, radius_y) = radius;

    let image_bounds = Rect::new(0, 0, image.width(), image.height());
    let circle_bounds = Rect::from_min_max(
        cx - radius_x as i32, cy - radius_y as i32,
        cx + radius_x as i32, cy + radius_y as i32);

    let intersection = image_bounds.intersect(&circle_bounds);

    if intersection.is_empty() {
        return;
    }

    if alpha == 255 {
        for py in intersection.top..=intersection.bottom() {
                let y = ((py - cy) as f32) + 0.5;

                for px in intersection.left..=intersection.right() {
                    let x = ((px - cx) as f32) + 0.5;

                    let dist =
                        (x * x) / ((radius_x * radius_x) as f32) +
                        (y * y) / ((radius_y * radius_y) as f32);

                    if dist <= 1.0 {
                        unsafe {
                            image.unsafe_put_pixel(px as u32, py as u32, fill);
                        }
                    }
                }
            }
    } else {
        for py in intersection.top..=intersection.bottom() {
            let y = ((py - cy) as f32) + 0.5;

            for px in intersection.left..=intersection.right() {
                let x = ((px - cx) as f32) + 0.5;

                let dist =
                    (x * x) / ((radius_x * radius_x) as f32) +
                    (y * y) / ((radius_y * radius_y) as f32);

                if dist <= 1.0 {
                    unsafe {
                        unsafe_put_pixel_blend(image, px as u32, py as u32, fill);
                    }
                }
            }
        }
    }
}

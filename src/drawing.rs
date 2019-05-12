
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
                    let pixel = image.unsafe_get_pixel(x as u32, y as u32);
                    image.unsafe_put_pixel(x as u32, y as u32, blend_color(pixel, fill));
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

                if (x >= 0) && (y >= 0) && (x < (image.width() as i32)) && (y < (image.height() as i32)) {
                    unsafe {
                        let pixel = image.unsafe_get_pixel(x as u32, y as u32);
                        let pixel = blend_color(pixel, Rgba([r, g, b, (v * a) as u8]));

                        image.unsafe_put_pixel(x as u32, y as u32, pixel);
                    }
                }
            });
        }
    }
}

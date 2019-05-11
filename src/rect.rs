
#[derive(Debug)]
pub struct Rect {
    pub left: i32,
    pub top: i32,
    pub width: u32,
    pub height: u32,
}

impl Rect {
    pub fn new(left: i32, top: i32, width: u32, height: u32) -> Rect {
        Rect { left, top, width, height }
    }

    pub fn right(&self) -> i32 {
        self.left + (self.width as i32) - 1
    }

    pub fn bottom(&self) -> i32 {
        self.top + (self.height as i32) - 1
    }

    pub fn is_empty(&self) -> bool {
        (self.width == 0) || (self.height == 0)
    }

    pub fn intersect(&self, other: &Rect) -> Rect {
        let left = self.left.max(other.left);
        let top = self.top.max(other.top);
        let right = self.right().min(other.right());
        let bottom = self.bottom().min(other.bottom());

        let width  = 0.max(right - left + 1) as u32;
        let height = 0.max(bottom - top + 1) as u32;

        Rect { left, top, width, height }
    }
}

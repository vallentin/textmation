
fn _move(characters: usize, direction: &str) {
    print!("\u{001b}[{}{}", characters, direction);
}

pub fn move_up(characters: usize) {
    _move(characters, "A");
}

pub fn move_down(characters: usize) {
    _move(characters, "B");
}

pub fn move_right(characters: usize) {
    _move(characters, "C");
}

pub fn move_left(characters: usize) {
    _move(characters, "D");
}

pub fn move_back() {
    move_left(10000);
}

pub fn clear_line() {
    print!("\u{001b}[2K");
}

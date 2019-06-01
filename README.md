
*Note that Textmation is in its infancy. Features as well as syntax might change between early versions.*

# Textmation

Textmation (**Text**-based Ani**mation**) is a tool and language for textually creating animations.
Exporting animations currently supports GIF, MP4, AVI, WebM or exporting individual frames as PNGs.
Exporting video formats requires [ffmpeg](https://ffmpeg.org).


## Installation & Testing

*Note that Textmation currently relies on some Python scripts, and can as such not easily be installed with `cargo install --git [url]`.*

```bash
git clone https://github.com/vallentin/textmation
cd textmation

cargo install --path .

# Check help message to see command-line options
textmation --help

# Run "simple" example and output GIF
textmation examples/example_01_simple.anim

# Export format is inferred from the output filename
textmation -o output.mp4 examples/example_01_simple.anim
```


## Examples

Here are some rendered versions of the examples found in the [examples](https://github.com/Vallentin/textmation/tree/master/examples) directory.

### [Rectangle & Text](https://github.com/vallentin/textmation/blob/master/examples/example_01_simple.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/simple.png">
</p>

### [Templates](https://github.com/vallentin/textmation/blob/master/examples/example_02_template.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/template.png">
</p>

### [VBox & HBox](https://github.com/vallentin/textmation/blob/master/examples/example_03_layout.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/layout.png">
</p>

### Sliding Transitions

<table>
<tr>
<th><a href="https://github.com/vallentin/textmation/blob/master/examples/example_04_slide.anim">Simple Left to Right</a></th>
<th><a href="https://github.com/vallentin/textmation/blob/master/examples/example_05_slide.anim">Various Directions</a></th>
</tr>
<tr>
<td><img src="https://vallentin.io/img/textmation/slide.gif"></td>
<td><img src="https://vallentin.io/img/textmation/slide2.gif"></td>
</tr>
</table>


  [examples]: https://github.com/vallentin/textmation/tree/master/examples

  [cargo]: https://doc.rust-lang.org/cargo/
  [rustup]: https://rustup.rs/

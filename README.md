
*Note that Textmation is in its infancy. Features as well as syntax might change between early versions.*

# Textmation

Textmation (**Text**-based Ani**mation**) is a tool and language for textually creating animations.
Exporting animations currently supports GIF, MP4, AVI, WebM or exporting individual frames as PNGs.
Exporting video formats requires [ffmpeg](https://ffmpeg.org).


## Installation & Testing

*Note that Textmation has currently only been developed and tested with Python 3.7.2.*

```bash
git clone https://github.com/Vallentin/textmation
cd textmation

pip install -r requirements.txt

# Check help message to see command-line options
python -m textmation --help

# Run "simple" example and output GIF
python -m textmation examples/example_01_simple.anim

# Export format is inferred from the output filename
python -m textmation -o output.mp4 examples/example_01_simple.anim
```


## Examples

Here are some rendered versions of the examples found in the [examples](https://github.com/Vallentin/textmation/tree/master/examples) directory.

### [Rectangle & Text](https://github.com/Vallentin/textmation/blob/master/examples/example_01_simple.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/simple.png">
</p>

### [Templates](https://github.com/Vallentin/textmation/blob/master/examples/example_02_template.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/template.png">
</p>

### [VBox & HBox](https://github.com/Vallentin/textmation/blob/master/examples/example_03_layout.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/layout.png">
</p>

### [Sliding Transition](https://github.com/Vallentin/textmation/blob/master/examples/example_04_slide.anim)

<p align="center">
  <img src="https://vallentin.io/img/textmation/slide.gif">
</p>

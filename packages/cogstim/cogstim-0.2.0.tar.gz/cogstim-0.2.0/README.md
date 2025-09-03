# CogStim – Visual Cognitive-Stimulus Generator

CogStim is a small Python toolkit that produces **synthetic image datasets** commonly used in cognitive–neuroscience and psychophysics experiments, such as:

* Two–shape discrimination (e.g. *circle vs star*).
* Two–colour discrimination (e.g. *yellow vs blue* circles).
* Approximate Number System (ANS) dot arrays with two colours.
* Single-colour dot arrays for number-discrimination tasks.
* Custom combinations of geometrical *shapes × colours*.
* Rotated stripe patterns ("lines" dataset) for orientation discrimination.

All stimuli are generated as 512 × 512 px PNG files ready to be fed into machine-learning pipelines or presented in behavioural experiments.

## Installation

```bash
pip install cogstim  
```
## Command-line interface

After installation the `cli` module is available as the *single entry-point* to create datasets. Run it either via `python -m cogstim.cli …` or directly if the `cogstim` package is on your `$PYTHONPATH`.

```text
usage: cli.py [-h] (--shape_recognition | --color_recognition | --ans | --one_colour | --lines | --custom) [--shapes {circle,star,triangle,square} ...]
              [--colors {yellow,blue,red,green} ...] [--train_num TRAIN_NUM] [--test_num TEST_NUM] [--output_dir OUTPUT_DIR]
              [--min_surface MIN_SURFACE] [--max_surface MAX_SURFACE] [--no-jitter] [--easy]
              [--version_tag VERSION_TAG] [--min_point_num MIN_POINT_NUM] [--max_point_num MAX_POINT_NUM]
              [--angles ANGLES [ANGLES ...]] [--min_stripes MIN_STRIPES] [--max_stripes MAX_STRIPES]
              [--img_size IMG_SIZE] [--tag TAG] [--min_thickness MIN_THICKNESS] [--max_thickness MAX_THICKNESS]
              [--min_spacing MIN_SPACING] [--max_attempts MAX_ATTEMPTS]
```

> **Note**: train_num and test_num refer to the number of image _sets_ created. An image set is a group of images that comb all the possible parameter combinations. So, for shapes and colors, an image set is of about 200 images, whereas for ANS is of around 75 images, of course always depending on the other parameters.
> **Note**: All cli arguments use British spelling.

## Examples

### Shape recognition – *circle vs star* in yellow
```bash
python -m cogstim.cli --shape_recognition --train_num 60 --test_num 20
```

<table><tr>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/circle.png" alt="Yellow circle" width="220"/></td>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/star.png" alt="Yellow star" width="220"/></td>
</tr></table>

### Colour recognition – yellow vs blue circles (no positional jitter)
```bash
python -m cogstim.cli --color_recognition --no-jitter
```

<table><tr>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/circle.png" alt="Yellow circle" width="220"/></td>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/circle_blue.png" alt="Blue circle" width="220"/></td>
</tr></table>

###  Approximate Number System (ANS) dataset with easy ratios only
```bash
python -m cogstim.cli --ans --easy --train_num 100 --test_num 40
```

<table><tr>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/ans_equalized.png" alt="ANS equalized" width="220"/></td>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/ans.png" alt="ANS non-equalized" width="220"/></td>
</tr></table>

> Note that on the left image, total surfaces are equalized, and, on the right image, dot size is random.

### Single-colour dot arrays numbered 1-5, total surface area held constant
```bash
python -m cogstim.cli --one_colour --min_point_num 1 --max_point_num 5
```

<table><tr>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/dots_two.png" alt="Two circles" width="220"/></td>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/dots_five.png" alt="Five circles" width="220"/></td>
</tr></table>

### Custom dataset – green/red triangles & squares
```bash
python -m cogstim.cli --custom --shapes triangle square --colors red green
```

<table><tr>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/triangle_red.png" alt="Red triangle" width="220"/></td>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/square_green.png" alt="Green square" width="220"/></td>
</tr></table>

### Lines dataset – rotated stripe patterns
```bash
python -m cogstim.cli --lines --train_num 50 --test_num 20 --angles 0 45 90 135 --min_stripes 3 --max_stripes 5
```

<table><tr>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/lines_vertical.png" alt="Vertical lines" width="220"/></td>
  <td><img src="https://raw.githubusercontent.com/eudald-seeslab/cogstim/main/assets/examples/lines_horizontal.png" alt="Horizontal lines" width="220"/></td>
</tr></table>

## Output
The generated folder structure is organised by *phase / class*, e.g.
```
images/two_shapes/
  ├── train/
  │   ├── circle/
  │   └── star/
  └── test/
      ├── circle/
      └── star/
```

## License

This project is distributed under the **MIT License** – see the `LICENSE` file for details.

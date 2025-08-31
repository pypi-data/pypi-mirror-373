# fotolab

A console program to manipulate photos.

## Installation

Stable version From PyPI using `uv`:

```console
uv tool install fotolab
```

Upgrade to latest stable version:

```console
uv tool upgrade fotolab
```

## Usage

```console
fotolab -h
```

<!--help !-->

```console
usage: fotolab [-h] [-o] [-q] [-v] [-d] [-V]
               {animate,auto,border,contrast,env,halftone,info,montage,resize,rotate,sharpen,watermark} ...

A console program to manipulate photos.

website: https://github.com/kianmeng/fotolab
changelog: https://github.com/kianmeng/fotolab/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/fotolab/issues

positional arguments:
  {animate,auto,border,contrast,env,halftone,info,montage,resize,rotate,sharpen,watermark}
                    sub-command help
    animate         animate an image
    auto            auto adjust (resize, contrast, and watermark) a photo
    border          add border to image
    contrast        contrast an image.
    env             print environment information for bug reporting
    halftone        halftone an image
    info            info an image
    montage         montage a list of image
    resize          resize an image
    rotate          rotate an image
    sharpen         sharpen an image
    watermark       watermark an image

options:
  -h, --help        show this help message and exit
  -o, --overwrite   overwrite existing image
  -q, --quiet       suppress all logging
  -v, --verbose     show verbosity of debugging log, use -vv, -vvv for more details
  -d, --debug       show debugging log and stacktrace
  -V, --version     show program's version number and exit
```

<!--help !-->

### fotolab animate

```console
fotolab animate -h
```

<!--help-animate !-->

```console
usage: fotolab animate [-h] [-f FORMAT] [-d DURATION] [-l LOOP] [-op]
                       [--webp-quality QUALITY] [--webp-lossless]
                       [--webp-method METHOD] [-od OUTPUT_DIR]
                       IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filenames

options:
  -h, --help            show this help message and exit
  -f, --format FORMAT   set the image format (default: 'gif')
  -d, --duration DURATION
                        set the duration in milliseconds (must be a positive
                        integer, default: '2500')
  -l, --loop LOOP       set the loop cycle (default: '0')
  -op, --open           open the image using default program (default:
                        'False')
  --webp-quality QUALITY
                        set WEBP quality (0-100, default: '80')
  --webp-lossless       enable WEBP lossless compression (default: 'False')
  --webp-method METHOD  set WEBP encoding method (0=fast, 6=slow/best,
                        default: '4')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-animate !-->

### fotolab auto

```console
fotolab auto -h
```

<!--help-auto !-->

```console
usage: fotolab auto [-h] IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES  set the image filename

options:
  -h, --help       show this help message and exit
```

<!--help-auto !-->

### fotolab border

```console
fotolab border -h
```

<!--help-border !-->

```console
usage: fotolab border [-h] [-c COLOR] [-w WIDTH] [-wt WIDTH] [-wr WIDTH]
                      [-wb WIDTH] [-wl WIDTH] [-op] [-od OUTPUT_DIR]
                      IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filenames

options:
  -h, --help            show this help message and exit
  -c, --color COLOR     set the color of border (default: 'black')
  -w, --width WIDTH     set the width of border in pixels (default: '10')
  -wt, --width-top WIDTH
                        set the width of top border in pixels (default: '0')
  -wr, --width-right WIDTH
                        set the width of right border in pixels (default: '0')
  -wb, --width-bottom WIDTH
                        set the width of bottom border in pixels (default:
                        '0')
  -wl, --width-left WIDTH
                        set the width of left border in pixels (default: '0')
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-border !-->

### fotolab contrast

```console
fotolab contrast -h
```

<!--help-contrast !-->

```console
usage: fotolab contrast [-h] [-c CUTOFF] [-op] [-od OUTPUT_DIR]
                        IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filename

options:
  -h, --help            show this help message and exit
  -c, --cutoff CUTOFF   set the percentage (0-50) of lightest or darkest
                        pixels to discard from histogram (default: '1.0')
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-contrast !-->

### fotolab halftone

```console
fotolab halftone -h
```

<!--help-halftone !-->

```console
usage: fotolab halftone [-h] [-ba] [-op] [-od OUTPUT_DIR] [-c CELLS] [-g]
                        IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filename

options:
  -h, --help            show this help message and exit
  -ba, --before-after   generate a GIF showing before and after changes
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
  -c, --cells CELLS     set number of cells across the image width (default:
                        50)
  -g, --grayscale       convert image to grayscale before applying halftone
```

<!--help-halftone !-->

### fotolab info

```console
fotolab info -h
```

<!--help-info !-->

```console
usage: fotolab info [-h] [-s] [--camera] [--datetime] IMAGE_FILENAME

positional arguments:
  IMAGE_FILENAME  set the image filename

options:
  -h, --help      show this help message and exit
  -s, --sort      show image info by sorted field name
  --camera        show the camera maker details
  --datetime      show the datetime
```

<!--help-info !-->

### fotolab rotate

```console
fotolab rotate -h
```

<!--help-rotate !-->

```console
usage: fotolab rotate [-h] [-r ROTATION] [-cw] [-op] [-od OUTPUT_DIR]
                      IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filenames

options:
  -h, --help            show this help message and exit
  -r, --rotation ROTATION
                        Rotation angle in degrees (default: '0')
  -cw, --clockwise      Rotate clockwise (default: 'False)
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-rotate !-->

### fotolab montage

```console
fotolab montage -h
```

<!--help-montage !-->

```console
usage: fotolab montage [-h] [-op] [-od OUTPUT_DIR]
                       IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filenames

options:
  -h, --help            show this help message and exit
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-montage !-->

### fotolab resize

```console
fotolab resize -h
```

<!--help-resize !-->

```console
usage: fotolab resize [-h] [-c] [-l CANVAS_COLOR] [-W WIDTH | -H HEIGHT] [-op]
                      [-od OUTPUT_DIR]
                      IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filename

options:
  -h, --help            show this help message and exit
  -c, --canvas          paste image onto a larger canvas
  -l, --canvas-color CANVAS_COLOR
                        the color of the extended larger canvas(default:
                        'black')
  -W, --width WIDTH     set the width of the image (default: '600')
  -H, --height HEIGHT   set the height of the image (default: '277')
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-resize !-->

### fotolab sharpen

```console
fotolab sharpen -h
```

<!--help-sharpen !-->

```console
usage: fotolab sharpen [-h] [-r RADIUS] [-p PERCENT] [-t THRESHOLD] [-ba]
                       [-op] [-od OUTPUT_DIR]
                       IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filenames

options:
  -h, --help            show this help message and exit
  -r, --radius RADIUS   set the radius or size of edges (default: '1')
  -p, --percent PERCENT
                        set the amount of overall strength of sharpening
                        effect (default: '100')
  -t, --threshold THRESHOLD
                        set the minimum brightness changed to be sharpened
                        (default: '3')
  -ba, --before-after   generate a GIF showing before and after changes
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-sharpen !-->

### fotolab watermark

```console
fotolab watermark -h
```

<!--help-watermark !-->

```console
usage: fotolab watermark [-h] [-t WATERMARK_TEXT]
                         [-p {top-left,top-right,bottom-left,bottom-right}]
                         [-pd PADDING] [-fs FONT_SIZE] [-fc FONT_COLOR]
                         [-ow OUTLINE_WIDTH] [-oc OUTLINE_COLOR]
                         [-a ALPHA_VALUE] [--camera]
                         [-l | --lowercase | --no-lowercase] [-op]
                         [-od OUTPUT_DIR]
                         IMAGE_FILENAMES [IMAGE_FILENAMES ...]

positional arguments:
  IMAGE_FILENAMES       set the image filenames

options:
  -h, --help            show this help message and exit
  -t, --text WATERMARK_TEXT
                        set the watermark text (default: 'kianmeng.org')
  -p, --position {top-left,top-right,bottom-left,bottom-right}
                        set position of the watermark text (default: 'bottom-
                        left')
  -pd, --padding PADDING
                        set the padding of the watermark text relative to the
                        image (default: '15')
  -fs, --font-size FONT_SIZE
                        set the font size of watermark text (default: '12')
  -fc, --font-color FONT_COLOR
                        set the font color of watermark text (default:
                        'white')
  -ow, --outline-width OUTLINE_WIDTH
                        set the outline width of the watermark text (default:
                        '2')
  -oc, --outline-color OUTLINE_COLOR
                        set the outline color of the watermark text (default:
                        'black')
  -a, --alpha ALPHA_VALUE
                        set the transparency of the watermark text (0-255,
                        where 0 is fully transparent and 255 is fully opaque;
                        default: '128')
  --camera              use camera metadata as watermark
  -l, --lowercase, --no-lowercase
                        lowercase the watermark text
  -op, --open           open the image using default program (default:
                        'False')
  -od, --output-dir OUTPUT_DIR
                        set default output folder (default: 'output')
```

<!--help-watermark !-->

### fotolab env

```console
fotolab env -h
```

<!--help-env !-->

```console
usage: fotolab env [-h]

options:
  -h, --help  show this help message and exit
```

<!--help-env !-->

## Copyright and License

Copyright (C) 2024,2025 Kian-Meng Ang

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.

The fish logo used in the documentation generated by Sphinx is a public domain
drawing of male freshwater phase [Sockeye (red) salmon (Oncorhynchus nerka)]
(https://en.wikipedia.org/w/index.php?oldid=1186575702) from
<https://commons.wikimedia.org/entity/M2787002>.

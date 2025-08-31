## tinyoffice

Make your Office files tiny!

`tinyoffice` attemps to compresses and optionally convert the embedded image files in your Office files.


## Installation

You can install `tinyoffice` from PyPi:

```
% pip install tinyoffice
```

NOTE: `tinyoffice` requires `Pillow` (`PIL` Fork) [Pillow](https://pillow.readthedocs.io/en/stable/), which can have installation conflicts. If you experience any issues while installing `tinyoffice`, please follow the `Pillow` installation steps found here: https://pillow.readthedocs.io/en/stable/installation.html.


## Usage

```
usage: tinyoffice [-h] [-r] [-c] [-v]
                  [-t .docx .pptx .xlsx [.docx .pptx .xlsx ...]] [--overwrite]
                  [-o OUTPUT] [-exts EXTENSIONS [EXTENSIONS ...]]
                  path

Make your Office files tiny!

positional arguments:
  path                  File or directory path.
                        If a file and recurse (-r/--recurse) is not set, only that file will be compressed.
                        If a directory and recurse is not set, only the top-level files in the directory will be compressed.
                        If recurse is set, everything at path and below will be compressed.

options:
  -h, --help            show this help message and exit
  -r, --recurse         Flag for if tinyoffice should recursively search for files. Default is False
  -c, --convert         Flag for if TIFF files should be converted to JPEGs. Default is False
  -v, --verbose         Flag for verbosity levels. Can be set multiple times, e.g., -vv, for increased verbosity
  -t .docx .pptx .xlsx [.docx .pptx .xlsx ...], --types .docx .pptx .xlsx [.docx .pptx .xlsx ...]
                        Filetype extensions to compress.
                        Default is .docx, .pptx, .xlsx
  --overwrite           Flag for if an existing file should be overwritten. Default is False
  -o OUTPUT, --output OUTPUT
                        Path for the output location.
  -exts EXTENSIONS [EXTENSIONS ...], --extensions EXTENSIONS [EXTENSIONS ...]
                        Image extensions to compress. Default will be only the extensions that are supported by Pillow on your system.
                        Should be ignored.
```

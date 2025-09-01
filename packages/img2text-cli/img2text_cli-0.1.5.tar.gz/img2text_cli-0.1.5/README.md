# img2text-cli

A powerful command-line tool to extract text from images using OCR (Optical Character Recognition).

## Features

- 🖼️ **Image to Text**: Convert image files to text using Tesseract OCR
- 📋 **Clipboard Support**: Extract text directly from clipboard images
- 🔄 **Piping Support**: Process images from stdin for automation
- ⚡ **Fast & Efficient**: Built with Python and optimized for performance
- 🎯 **Simple CLI**: Easy-to-use command-line interface

## Installation

### From PyPI (Recommended)

```bash
pip install img2text-cli
```

## Prerequisites

This tool requires **Tesseract OCR** to be installed on your system. For detailed installation instructions, visit the [official Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html).

## Usage

### Basic Usage

Extract text from an image file:
```bash
img2text image.png
```

### Piping Images

Process images from stdin:
```bash
cat image.png | img2text
```

### Clipboard Image

Extract text from an image in your clipboard:
```bash
img2text --clip
```

### Help

Get help and see all options:
```bash
img2text --help
```

## Examples

```bash
# Extract text from a local image file
$ img2text document.png
This is the extracted text from the image...

# Process clipboard image
$ img2text --clip
# Text is automatically copied to clipboard

# Use with other tools
$ ls *.png | xargs -I {} img2text {}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3 (GPLv3) - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - The OCR engine
- [Click](https://click.palletsprojects.com/) - Command line interface creation kit
- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard operations for text
- [pyperclipimg](https://github.com/asweigart/pyperclipimg) - Cross-platform clipboard operations for images
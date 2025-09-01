import io
from PIL import Image
import pytesseract
import sys
import click
import pyperclipimg
import pyperclip


def get_img_data(filename: str | None):
    if sys.stdin.isatty():
        if filename is None:
            raise click.UsageError("No file provided")
        return open(filename, "rb")

    data = sys.stdin.buffer.read()
    return io.BytesIO(data)


def clip_ocr():
    image = pyperclipimg.paste()
    text = pytesseract.image_to_string(image=image)
    pyperclip.copy(text)


@click.command(
    name="img2text",
    epilog="""
Examples:\n
- Image file to text\n
   $ img2text image.png\n
- Piped image to text\n
   $ cat image.png | img2text\n
- Extract text from the clipboard image and copy it to the clipboard\n
   $ img2text --clip\n
""",
)
@click.argument("image_file", type=click.Path(exists=True), required=False)
@click.option(
    "--clip",
    is_flag=True,
    help="Extract text from the clipboard image and copy it to the clipboard",
)
def ocr(clip: bool, image_file: str | None):
    """
    Extract text from an image
    """
    if clip:
        clip_ocr()
        return

    image = Image.open(get_img_data(image_file))
    text = pytesseract.image_to_string(image=image)
    print(text)


if __name__ == "__main__":
    ocr()

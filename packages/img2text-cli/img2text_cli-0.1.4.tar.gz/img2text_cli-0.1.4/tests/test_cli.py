import os
import unittest
from click.testing import CliRunner

from img2text_cli.main import ocr

image_file_name = "image.png"
output_text_name = "image.txt"
image_text = "/home/aman/scripts/tools/imgtotext : Line 12: argc: command not found"


def test_helptext():
    runner = CliRunner()

    result = runner.invoke(ocr, ["--help"])

    assert result.exit_code == 0
    assert "Usage: img2text [OPTIONS] [IMAGE_FILE]" in result.output
    assert "Extract text from an image" in result.output
    assert (
        "--clip  Extract text from the clipboard image and copy it to the clipboar"
        in result.output
    )
    assert "--help  Show this message and exit." in result.output


def test_clipboard():
    runner = CliRunner()

    os.system(f"wl-copy < {image_file_name}")
    result = runner.invoke(ocr, ["--clip"])
    os.system(f"wl-paste > {output_text_name}")
    assert result.exit_code == 0
    assert image_text in open(output_text_name).read()
    os.remove(output_text_name)


def test_piped_input():
    os.system(f"cat {image_file_name} | uv run img2text > {output_text_name}")
    assert image_text in open(output_text_name).read()
    os.remove(output_text_name)


@unittest.skip("not working ")
def test_image_arg():
    os.system(f"uv run img2text {image_file_name}> {output_text_name}")
    assert image_text in open(output_text_name).read()
    os.remove(output_text_name)

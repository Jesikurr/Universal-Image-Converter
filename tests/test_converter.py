import os
import tempfile
import unittest

from PIL import Image

from converter import convert_image_detailed


class ConverterTests(unittest.TestCase):
    def test_convert_image_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "source.png")
            output_dir = os.path.join(tmp_dir, "out")

            image = Image.new("RGB", (32, 32), color="red")
            image.save(input_path)

            result = convert_image_detailed(input_path, output_dir, "jpg")

            self.assertTrue(result.success)
            self.assertIsNotNone(result.output_path)
            self.assertTrue(os.path.isfile(result.output_path or ""))

    def test_convert_image_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = convert_image_detailed("missing-file.png", tmp_dir, "png")

            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)
            self.assertIn("Input file not found", result.error or "")

    def test_convert_image_invalid_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "source.png")
            image = Image.new("RGB", (10, 10), color="blue")
            image.save(input_path)

            result = convert_image_detailed(input_path, tmp_dir, "invalid")

            self.assertFalse(result.success)
            self.assertIn("Unsupported output format", result.error or "")


if __name__ == "__main__":
    unittest.main()

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import cli


class CliTests(unittest.TestCase):
    def test_list_formats_returns_zero(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = cli.main(["--list-formats"])

        self.assertEqual(code, 0)
        self.assertIn("Supported input formats", stream.getvalue())

    def test_missing_required_arguments_returns_error(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = cli.main([])

        self.assertEqual(code, 2)
        self.assertIn("--output-format is required", stream.getvalue())

    def test_invalid_input_folder_returns_error(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = cli.main(
                [
                    "--input-folder",
                    "./missing-folder",
                    "--output-format",
                    "png",
                    "--output-folder",
                    "./out",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("Input folder does not exist", stream.getvalue())

    def test_single_file_conversion_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "source.png")
            output_dir = os.path.join(tmp_dir, "out")

            from PIL import Image

            image = Image.new("RGB", (20, 20), color="green")
            image.save(input_path)

            stream = io.StringIO()
            with redirect_stdout(stream):
                code = cli.main(
                    [
                        "--input",
                        input_path,
                        "--output-format",
                        "jpg",
                        "--output-folder",
                        output_dir,
                    ]
                )

            self.assertEqual(code, 0)
            outputs = [name for name in os.listdir(output_dir) if name.endswith(".jpg")]
            self.assertTrue(outputs)


if __name__ == "__main__":
    unittest.main()

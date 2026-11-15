"""Regression tests for bounded static HTML integrity checks."""
import tempfile
import unittest
from pathlib import Path

from scripts.check_static_html import check


class HtmlIntegrityTests(unittest.TestCase):
    def test_valid_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("<!DOCTYPE html><html>ok</html>", encoding="utf-8")
            (root / "second.html").write_text("<html>Olá</html>", encoding="utf-8")
            got = check(root)
            self.assertEqual(got["html_files"], 2)
            self.assertEqual(got["failures"], [])

    def test_no_index_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "other.html").write_text("<html></html>", encoding="utf-8")
            self.assertIn("index.html is missing", check(root)["failures"])

    def test_empty_page_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("  ", encoding="utf-8")
            self.assertTrue(any("empty page" in item for item in check(root)["failures"]))

    def test_binary_or_invalid_utf8_fails(self):
        for data, expected in [(b"<html>\x00</html>", "NUL byte"),
                               (b"<html>\xff</html>", "invalid UTF-8")]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "index.html").write_bytes(data)
                self.assertTrue(any(expected in item for item in check(root)["failures"]))


if __name__ == "__main__":
    unittest.main()

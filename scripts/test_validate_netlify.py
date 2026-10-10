import tempfile
import unittest
from pathlib import Path

from validate_netlify import validate


class NetlifyValidationTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "netlify.toml"

    def tearDown(self):
        self.temp.cleanup()

    def write_config(self, content):
        self.path.write_text(content, encoding="utf-8")

    def test_valid_configuration(self):
        self.write_config("""
[build]
publish = "frontend"

[[headers]]
for = "/*"
[headers.values]
Content-Security-Policy = "default-src 'self'; script-src 'self'; connect-src 'self'"
""")
        validate(self.path)

    def test_invalid_toml(self):
        self.write_config("[build\npublish = 'frontend'")
        with self.assertRaises(Exception):
            validate(self.path)

    def test_wildcard_csp(self):
        for directive in (
            "default-src",
            "script-src",
            "connect-src",
        ):
            with self.subTest(directive=directive):
                self.write_config(f"""
[build]
publish = "frontend"

[[headers]]
for = "/*"
[headers.values]
Content-Security-Policy = "{directive} *"
""")
                with self.assertRaises(ValueError):
                    validate(self.path)

    def test_missing_for(self):
        self.write_config("""
[build]
publish = "frontend"

[[headers]]
[headers.values]
X-Test = "1"
""")
        with self.assertRaises(ValueError):
            validate(self.path)


if __name__ == "__main__":
    unittest.main()

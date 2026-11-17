import base64
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRequestImport(TransactionCase):
    def wizard(self, data, filename="test.xlsx"):
        return self.env["tucha.request.import"].new({
            "filename": filename, "file_data": data,
        })

    def test_exact_limit_decoded_once(self):
        source = b"x" * (10 * 1024 * 1024)
        wizard = self.wizard(base64.b64encode(source))
        with patch(
            "odoo.addons.tucha_crm.models.request_import.base64.b64decode",
            wraps=base64.b64decode,
        ) as decode:
            self.assertEqual(wizard._source_bytes(), source)
        decode.assert_called_once_with(wizard.file_data, validate=True)

    def test_one_byte_above_limit(self):
        wizard = self.wizard(base64.b64encode(b"x" * (10 * 1024 * 1024 + 1)))
        with self.assertRaisesRegex(ValidationError, "10 MiB"):
            wizard._source_bytes()

    def test_corrupted_base64(self):
        for data in (b"!!!!", b"YQ", b"YQ==!", b"Y Q=="):
            with self.subTest(data=data):
                with self.assertRaisesRegex(ValidationError, "Base64"):
                    self.wizard(data)._source_bytes()

    def test_small_file_and_case_insensitive_extension(self):
        self.assertEqual(self.wizard(b"YWJj", "TEST.XLSX")._source_bytes(), b"abc")

    def test_missing_file(self):
        with self.assertRaisesRegex(ValidationError, "непустой"):
            self.wizard(False)._source_bytes()

    def test_wrong_extension(self):
        with self.assertRaisesRegex(ValidationError, "xlsx"):
            self.wizard(b"YWJj", "test.xls")._source_bytes()

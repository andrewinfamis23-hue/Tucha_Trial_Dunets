import base64
import binascii

from odoo import fields, models
from odoo.exceptions import ValidationError


class TuchaRequestImport(models.TransientModel):
    _name = "tucha.request.import"
    _description = "Импорт заявки из Excel"

    filename = fields.Char(required=True)
    file_data = fields.Binary(required=True, attachment=False)

    def _source_bytes(self) -> bytes:
        """Строго декодировать файл один раз и проверить размер исходных байтов."""
        self.ensure_one()
        if not self.filename or not self.filename.casefold().endswith(".xlsx"):
            raise ValidationError("Выберите файл .xlsx по шаблону компании.")
        if not self.file_data:
            raise ValidationError("Выберите непустой файл Excel.")
        try:
            source = base64.b64decode(self.file_data, validate=True)
        except (binascii.Error, ValueError):
            raise ValidationError("Не удалось прочитать файл: повреждённые данные Base64.") from None

        if len(source) > 10 * 1024 * 1024:
            raise ValidationError("Размер файла Excel не должен превышать 10 MiB (10 485 760 байт).")
        return source

    def action_validate_file(self) -> dict:
        """Даёт кандидату воспроизводимую точку входа через интерфейс."""
        self._source_bytes()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Файл принят",
                "message": "Размер файла не превышает лимит.",
                "type": "success",
                "sticky": False,
            },
        }

# Локальная сдача

## Изменения

1. Повторное открытие корректировки очищает даты получения и проверки,
   сохраняет новую дату запроса и прежние проверки прав.
2. SOLUTION.md описывает оптимизацию списка; код задания 2 не изменён.
3. _source_bytes строго декодирует Base64 один раз, проверяет len(source)
   относительно 10 * 1024 * 1024 и возвращает уже декодированные байты.
   Ровно 10 MiB допускаются, следующий байт отклоняется.

Добавлены серверные тесты в addons/tucha_crm/tests. Серверные Odoo-тесты прошли: 10 тестов, 0 failures, 0 errors.
Восемь быстрых тестов, compileall и compose config также прошли.
UI корректировки под менеджером и загрузки Excel под кандидатом проверен.
Подробные результаты и ограничения — в WORKLOG.md.

## Повторный запуск и проверки

Из корня проекта. Python нужен только для быстрых проверок; Odoo и PostgreSQL запускаются через Docker:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install ruff==0.17.5
.venv/bin/ruff check addons tests
python3 -m compileall -q addons tests
python3 -m unittest discover -s tests -v
docker compose up -d --build
# Дождаться Registry loaded в docker compose logs odoo.
docker compose stop odoo
docker compose run --rm --no-deps --entrypoint odoo odoo \
  --config=/etc/odoo/odoo.conf --database=tucha_sandbox \
  --update=tucha_crm --test-enable --test-tags /tucha_crm \
  --stop-after-init --no-http
docker compose up -d odoo
```

В журнале проверить отсутствие FAIL/ERROR и наличие выполненных тестов
TestRequestCorrection и TestRequestImport. Восстановить запуск odoo даже при
ошибке тестов. Открыть http://localhost, проверить полный цикл корректировки
под менеджером и загрузку небольшого .xlsx под кандидатом. Данные входа — README.md.
Compose использует имя проекта tucha-trial-day: перед запуском проверить,
не работает ли другая копия с тем же именем, чтобы не использовать её volumes.

Для появления кнопки «Проверить Excel» сначала отметьте любую заявку галочкой.
Песочница оставлена запущенной на http://localhost.

Ruff 0.17.5: All checks passed! Все обязательные проверки завершены успешно.

## Состав переносимой копии

В архиве находятся исходники, конфигурация Docker, учебные seed-данные, тесты
и отчёты. Образы и volumes Docker не включены: база создаётся при первом запуске.
Архив не содержит Git-историю; после распаковки можно создать новый репозиторий.
Лог ODOO_TEST_RESULTS.log явно разрешён в .gitignore как отчёт проверки.
Независимый аудит и снимки интерфейса — в docs/validation; аудит описывает
состояние до исправления переносимости команды Ruff.

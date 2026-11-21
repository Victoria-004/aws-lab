# Емулятор датчиків

Емулює чотири датчики. Кожен надсилає вимірювання окремим HTTP `POST` на `<base_url>/ingest` зі своєю частотою.

| Датчик | Тип (`sensor_type`) | Параметр, одиниця | Частота |
|---|---|---|---|
| `temp-01` | `temperature` | температура, `C` | 50 мс |
| `hum-01` | `humidity` | вологість, `%` | 70 мс |
| `light-01` | `light` | освітленість, `lux` | 100 мс |
| `cam-01` | `camera` | знімок (бонус), розмір у `bytes` | кожні 15 с |

Частота кожного датчика задається в конфігурації: `interval_ms` від 20 до 100 мс (камера: `period_s` від 10 до 30 с). Значення поза діапазоном емулятор не приймає. Раз на 5 с у журнал пишеться кількість надісланих повідомлень і помилок по кожному датчику та разом; підсумок виводиться при зупинці.

Зрідка (≈ 0,5% вимірювань) датчик навмисно видає аномальне значення, щоб було що виявляти обробнику.

## Конфігурація

Файл JSON (за замовчуванням `config.json` поруч зі скриптом; шаблон — `config.example.json`) і змінні середовища, які його перекривають:

| Змінна | Призначення |
|---|---|
| `EMULATOR_CONFIG` | шлях до файлу конфігурації |
| `EMULATOR_BASE_URL` | адреса приймача (`terraform output api_url`) |
| `EMULATOR_API_KEY` | ключ доступу, заголовок `x-api-key` (`terraform output -raw api_key`) |
| `EMULATOR_DURATION_S` | скільки секунд працювати (0 — до Ctrl+C) |

`config.json` у `.gitignore`: ключ у репозиторій не потрапляє. Рекомендується передавати адресу й ключ змінними середовища.

## Запуск локально

```powershell
cd lab3/emulator
python -m pip install -r requirements.txt
copy config.example.json config.json    # за потреби змінити датчики й частоти

$env:EMULATOR_BASE_URL = "https://<id>.execute-api.eu-north-1.amazonaws.com"
$env:EMULATOR_API_KEY  = "<api_key>"
$env:EMULATOR_DURATION_S = "300"        # 5 хвилин
python emulator.py
```

Зупинка за `Ctrl+C` або після `EMULATOR_DURATION_S`.

## Запуск у контейнері

```powershell
docker build -t iot-emulator lab3/emulator
docker run --rm `
  -e EMULATOR_BASE_URL="https://<id>.execute-api.eu-north-1.amazonaws.com" `
  -e EMULATOR_API_KEY="<api_key>" `
  -e EMULATOR_DURATION_S=300 `
  -v ${PWD}/lab3/emulator/config.example.json:/app/config.json:ro `
  iot-emulator
```

Файл конфігурації монтується в `/app/config.json` (або вказується через `EMULATOR_CONFIG`).

## Перевірка без хмари

`mock_receiver.py` повторює контракт приймача (202/400/401, видача URL для знімків):

```powershell
python mock_receiver.py                 # перше вікно, http://localhost:8080, ключ local-key
$env:EMULATOR_BASE_URL = "http://127.0.0.1:8080"
$env:EMULATOR_API_KEY  = "local-key"
python emulator.py                      # друге вікно
```

На Windows у `EMULATOR_BASE_URL` використовуйте `127.0.0.1`, а не `localhost`: спроба з'єднання через IPv6 затримує кожен запит приблизно на секунду, і задана частота не витримується.

## Повідомлення

```json
{
  "sensor_id": "temp-01",
  "sensor_type": "temperature",
  "value": 21.37,
  "unit": "C",
  "location": {"lat": 49.8397, "lon": 24.0297},
  "measured_at": "2026-11-21T18:00:00.123Z"
}
```

Для камери додається `"object_key"` — ключ знімка, завантаженого в S3 за підписаним URL (див. [../docs/BLOB.md](../docs/BLOB.md)).

## Ліміти

Найшвидший датчик (50 мс) дає 20 повідомлень/с, усі три числові датчики разом — ≈ 45/с, тобто за 5 хвилин ≈ 13 500 повідомлень. Мінімальний інтервал, який дозволяє емулятор, 20 мс на датчик.

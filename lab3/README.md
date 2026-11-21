# Лабораторна робота 3. Опрацювання даних з IoT-сенсорів (serverless, AWS)

Конвеєр: емулятор датчиків → HTTP API → функція-приймач → черга SQS → функція-обробник → MySQL (RDS) і DynamoDB → функція читання історії. Знімки камери йдуть окремим шляхом: у S3 за підписаним URL.

Постійно запущених контейнерів немає: усе приймання, обробка і читання виконують Lambda-функції, які запускаються подіями. Єдиний процес, що працює «звичайно», — емулятор.

## Публічна адреса приймача

Адреса з'являється після розгортання:

```powershell
terraform -chdir=terraform output api_url
```

Формат: `https://<id>.execute-api.eu-north-1.amazonaws.com`. Приймач: `POST <api_url>/ingest`.

## Архітектура коротко

```
емулятор ──POST /ingest──► API Gateway ──► Lambda ingest ──► SQS ──► Lambda processor ──► MySQL (RDS)
   │                                                           │                      └──► DynamoDB (сирі дані)
   │                                                           └─(3 невдалі спроби)─► SQS DLQ
   ├─POST /camera/upload-url─► Lambda upload_url   (підписаний URL)
   └─PUT знімка за підписаним URL──────────────────────────────────────► S3
клієнт ──GET /sensors/{id}/history──► API Gateway ──► Lambda history ──► MySQL | DynamoDB | S3 (підписані URL)
```

Детальна схема з призначенням кожного компонента: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Структура

| Шлях | Вміст |
|---|---|
| `emulator/` | Емулятор датчиків (Python), `Dockerfile`, локальний приймач для перевірки, [інструкція](emulator/README.md) |
| `functions/` | Код Lambda-функцій (`ingest`, `processor`, `history`, `upload_url`), спільний код `common/`, тести, `build.py` |
| `terraform/` | Уся інфраструктура: мережа, RDS, SQS + DLQ, DynamoDB, S3, Lambda, API Gateway, IAM |
| `docs/` | Документація за завданнями, див. нижче |

## Документи

| Файл | Завдання |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Схема конвеєра і компоненти |
| [docs/INGEST.md](docs/INGEST.md) | 2. Приймання даних у чергу |
| [docs/PROCESSING.md](docs/PROCESSING.md) | 3. Обробка даних функціями |
| [docs/DATA.md](docs/DATA.md) | 4. Збереження і читання історії |
| [docs/DLQ.md](docs/DLQ.md) | 5. Черга недоставлених повідомлень (бонус) |
| [docs/NOSQL.md](docs/NOSQL.md) | 6. Нереляційна база для сирих даних (бонус) |
| [docs/BLOB.md](docs/BLOB.md) | 7. Бінарні дані в об'єктному сховищі (бонус) |

## Розгортання

Потрібні: Terraform ≥ 1.5, AWS CLI з налаштованим доступом, Python 3.13 (для збірки і емулятора).

```powershell
# 1. Тести і збірка архівів функцій
python -m pip install -r functions/requirements-dev.txt
python -m pytest functions/tests
python functions/build.py

# 2. Інфраструктура (≈ 10 хвилин, найдовше піднімається RDS)
cd terraform
terraform init
terraform apply

# 3. Адреса і ключ для емулятора
terraform output api_url
terraform output -raw api_key
```

Секрети (пароль бази, ключ API) генерує Terraform, у репозиторії їх немає. Вони лежать у локальному стані (`terraform.tfstate`, виключений з git) і в змінних середовища функцій.

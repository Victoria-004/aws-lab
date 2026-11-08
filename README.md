# AWS Cloud Lab

Контейнеризований REST API застосунок на Flask, розгорнутий у хмарі AWS з використанням Docker, Terraform та CI/CD.

## Public Address:
`http://labdatabase-alb-598287063.eu-north-1.elb.amazonaws.com`

## Project Structure:

```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD пайплайн
├── app/
│   ├── my_project/             # Логіка API
│   │   └── utils/              # Підключення до бази, Redis, кеш, ідемпотентність
│   └── data.sql                # Скрипт бази даних
├── docs/                       # Звіти лабораторної роботи 2
├── loadtest/                   # Сценарій Locust та інструкція із запуску
├── terraform/
│   ├── alb.tf                  # Load Balancer
│   ├── alerts.tf               # Аларм p95 і SNS-підписка
│   ├── autoscaling.tf          # Автомасштабування і розклад
│   ├── dashboard.tf            # Панель CloudWatch
│   ├── ecs.tf                  # ECS Fargate
│   ├── github.tf               # OIDC та IAM Ролі
│   ├── network.tf              # VPC та мережа
│   ├── rds.tf                  # База даних RDS
│   ├── redis.tf                # Redis для кешу
│   └── security.tf             # Security Groups
├── tests/                      # Тест ідемпотентності
├── Dockerfile                  # Збірка Docker-образу
├── compose.yaml                # Локальний запуск: застосунок, MySQL, Redis
├── init_db.py
├── main.py                     # Основний файл запуску сервера
├── requirements.txt
├── requirements-dev.txt        # Locust і pytest
├── run.bat
└── README.md
```

## Лабораторна робота 2

| Завдання | Звіт |
|---|---|
| 1. Автоматичне масштабування | [docs/AUTOSCALING.md](docs/AUTOSCALING.md) |
| 2. Навантажувальний тест | [docs/LOADTEST.md](docs/LOADTEST.md), [loadtest/README.md](loadtest/README.md) |
| 3. Панель моніторингу | [docs/AUTOSCALING.md](docs/AUTOSCALING.md) |
| 4. Сповіщення | [docs/ALERTS.md](docs/ALERTS.md) |
| 5. Кешування | [docs/CACHE.md](docs/CACHE.md) |
| 7. Ідемпотентність (бонус) | [docs/IDEMPOTENCY.md](docs/IDEMPOTENCY.md) |
| 8. Масштабування за розкладом (бонус) | [docs/SCHEDULE.md](docs/SCHEDULE.md) |

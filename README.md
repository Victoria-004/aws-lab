# AWS Cloud Lab

Контейнеризований REST API застосунок на Flask, розгорнутий у хмарі AWS з використанням Docker, Terraform та CI/CD.

## Public Address:
`http://labdatabase-alb-1534427856.eu-north-1.elb.amazonaws.com`

## Project Structure:
.
|-- .github/
|   `-- workflows/
|       `-- deploy.yml          # CI/CD пайплайн
|-- app/
|   |-- my_project/             # Логіка API
|   `-- data.sql                # Скрипт бази даних
|-- terraform/
|   |-- alb.tf                  # Load Balancer
|   |-- ecs.tf                  # ECS Fargate
|   |-- github.tf               # OIDC та IAM Ролі
|   |-- network.tf              # VPC та мережа
|   |-- rds.tf                  # База даних RDS
|   |-- security.tf             # Security Groups
|   `-- versions.tf             # Версії провайдерів
|-- Dockerfile                  # Збірка Docker-образу
|-- main.py                     # Основний файл запуску сервера
`-- README.md                  
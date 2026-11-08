# Навантажувальний тест

## Встановлення

```powershell
pip install -r requirements-dev.txt
```

## Запуск

Одна команда з кореня репозиторію:

```powershell
locust --config loadtest/locust.conf --csv docs/loadtest_<назва_прогону>
```

- `loadtest/locust.conf` задає сценарій, адресу сервісу і режим без інтерфейсу.
- `--csv` зберігає результати у файли `docs/loadtest_<назва_прогону>_stats.csv` та `_stats_history.csv`.
- Тест сам завершується через 10 хвилин (фази описані в класі `StagesShape`).

Щоб запустити тест проти локального сервісу (`docker compose up`), додайте `--host http://localhost:5000`.

## Що відбувається перед тестом і після нього

- **Перед тестом** скрипт видаляє райони, які створили попередні прогони, і скидає лічильники кешу. Так кожен прогін стартує з однакової бази, і результати можна порівнювати.
- **Після тесту** скрипт виводить статистику кешу з `GET /cache/stats`: кількість влучань, промахів і частку влучань.

## Після тесту

Переконатися, що кількість задач повернулася до мінімальної (через 10–15 хвилин після завершення):

```powershell
aws ecs describe-services --cluster labdatabase-cluster --services labdatabase-service --query "services[0].[desiredCount,runningCount]"
```

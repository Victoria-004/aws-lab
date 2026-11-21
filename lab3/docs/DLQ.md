# Черга недоставлених повідомлень (DLQ)

## Налаштування

Опис у `terraform/sqs.tf`:

| Параметр | Значення | Пояснення |
|---|---|---|
| Основна черга | `iot-lab3-measurements` | сюди пише приймач |
| Черга DLQ | `iot-lab3-measurements-dlq` | зберігає повідомлення 14 діб (максимум) |
| `maxReceiveCount` | **3** | після 3 невдалих отримань повідомлення переходить у DLQ |
| `visibility_timeout_seconds` | 90 | час, через який невдале повідомлення знову стає доступним; 6 × таймаут функції (15 с) |
| `redrive_allow_policy` | лише основна черга | інші черги не можуть використовувати цю DLQ |

Обробник повертає `batchItemFailures` лише для невдалих повідомлень, тому одне «погане» повідомлення не блокує і не повторює решту пакета.

```hcl
redrive_policy = jsonencode({
  deadLetterTargetArn = aws_sqs_queue.dlq.arn
  maxReceiveCount     = 3
})
```

## Що вважається невдалою обробкою

Повідомлення, яке проходить валідацію приймача, зазвичай обробляється. Невдача можлива, якщо в тілі, що минуло приймач (наприклад, записане в чергу напряму), немає обов'язкових полів, воно не є JSON, має невідомий тип датчика або одиницю виміру, чи тимчасово недоступна база (тоді повтор зазвичай допомагає).

## Демонстрація

Нижче команди PowerShell. Приймач навмисно відсікає некоректні дані (`400`), тому «отруйне» повідомлення надсилається **напряму в чергу**. Змінні: `$Q` — `terraform output -raw queue_url`, `$DLQ` — `terraform output -raw dlq_url`.

```powershell
$Q   = terraform -chdir=terraform output -raw queue_url
$DLQ = terraform -chdir=terraform output -raw dlq_url

# 0. Скільки повідомлень у DLQ зараз (очікується 0)
aws sqs get-queue-attributes --queue-url $DLQ --attribute-names ApproximateNumberOfMessages --region eu-north-1

# 1. Запустити емулятор, щоб обробка йшла паралельно (інше вікно)

# 2. Надіслати отруйні повідомлення напряму в чергу
aws sqs send-message --queue-url $Q --message-body "це не JSON" --region eu-north-1
aws sqs send-message --queue-url $Q --region eu-north-1 --message-body '{\"sensor_id\":\"temp-01\",\"sensor_type\":\"pressure\",\"value\":1,\"unit\":\"Pa\",\"location\":{\"lat\":1,\"lon\":1},\"measured_at\":\"2026-11-21T18:00:00Z\",\"message_id\":\"11111111-1111-1111-1111-111111111111\",\"received_at\":\"2026-11-21T18:00:01Z\"}'

# 3. Стежити за журналом обробника: видно "status": "failed" із receive_count 1, 2, 3
aws logs tail /aws/lambda/iot-lab3-processor --follow --region eu-north-1 --filter-pattern failed

# 4. Приблизно через 5 хвилин повідомлення в DLQ (3 отримання з паузою 90 с, перенесення при наступному читанні)
aws sqs get-queue-attributes --queue-url $DLQ --attribute-names ApproximateNumberOfMessages --region eu-north-1
aws sqs receive-message --queue-url $DLQ --max-number-of-messages 5 --attribute-names All --region eu-north-1
```

**Що має бути видно:**

- у журналі обробника рядки `"status": "failed"` з `"receive_count": "1"`, потім `"2"` і `"3"` та текстом помилки;
- через ≈ 5 хвилин `ApproximateNumberOfMessages` у DLQ дорівнює 2, а в `receive-message` повертаються обидва повідомлення з вихідним тілом;
- водночас у журналі йдуть рядки `"status": "stored"` для нормальних повідомлень, а `GET /stats` показує, що кількість записів у базі продовжує зростати: **обробка решти не зупиняється**.

Результат прогону: після запуску вставити сюди вивід кроків 3-4 (журнал із `receive_count` і значення `ApproximateNumberOfMessages` у DLQ).

## Хто і як має розбирати DLQ

DLQ — це не сміттєвий кошик, а черга робіт для оператора (інженера, що супроводжує систему). Повідомлення там означає, що якесь вимірювання не потрапило в базу.

1. **Дізнатися про проблему.** Налаштувати аларм CloudWatch на метрику `ApproximateNumberOfMessagesVisible` черги DLQ (поріг > 0) і сповіщення (наприклад, SNS на пошту). Без аларму повідомлення можна довго не помічати, а зберігаються вони лише 14 діб.
2. **Дослідити.** Переглянути повідомлення (`receive-message` без видалення, `--visibility-timeout 0`) і знайти причину в журналі обробника за `message_id`.
3. **Виправити причину.** Помилка в коді або даних датчика, відсутність підтримки нової одиниці, недоступна база тощо.
4. **Повернути в обробку:** після виправлення перемістити повідомлення назад в основну чергу (redrive):
   `aws sqs start-message-move-task --source-arn <arn DLQ> --destination-arn <arn основної черги>` або кнопка «Start DLQ redrive» у консолі SQS. Завдяки ідемпотентності повторна обробка не створить дублів.
5. **Або відкинути.** Якщо дані безнадійно пошкоджені, видалити повідомлення з DLQ (`purge` або `delete-message`) і зафіксувати це.

Правило: DLQ має бути порожньою. Накопичення повідомлень — сигнал, що конвеєр втрачає дані.

output "api_url" {
  value       = aws_apigatewayv2_api.main.api_endpoint
  description = "Публічна адреса приймача (base_url емулятора)"
}

output "api_key" {
  value       = random_password.api_key.result
  sensitive   = true
  description = "Ключ для заголовка x-api-key: terraform output -raw api_key"
}

output "queue_url" {
  value = aws_sqs_queue.measurements.url
}

output "dlq_url" {
  value = aws_sqs_queue.dlq.url
}

output "bucket" {
  value = aws_s3_bucket.images.bucket
}

output "raw_table" {
  value = aws_dynamodb_table.raw.name
}

output "db_endpoint" {
  value = aws_db_instance.main.address
}

resource "random_password" "api_key" {
  length  = 32
  special = false
}

locals {
  dist = "${path.module}/../functions/dist"

  db_env = {
    DB_HOST     = aws_db_instance.main.address
    DB_PORT     = "3306"
    DB_NAME     = aws_db_instance.main.db_name
    DB_USER     = aws_db_instance.main.username
    DB_PASSWORD = random_password.db.result
  }
}

resource "aws_cloudwatch_log_group" "ingest" {
  name              = "/aws/lambda/${var.project}-ingest"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "upload_url" {
  name              = "/aws/lambda/${var.project}-upload-url"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "processor" {
  name              = "/aws/lambda/${var.project}-processor"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "history" {
  name              = "/aws/lambda/${var.project}-history"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "ingest" {
  function_name    = "${var.project}-ingest"
  role             = aws_iam_role.ingest.arn
  runtime          = "python3.13"
  handler          = "handler.handler"
  filename         = "${local.dist}/ingest.zip"
  source_code_hash = filebase64sha256("${local.dist}/ingest.zip")
  timeout          = 5
  memory_size      = 128

  environment {
    variables = {
      API_KEY   = random_password.api_key.result
      QUEUE_URL = aws_sqs_queue.measurements.url
    }
  }

  depends_on = [aws_cloudwatch_log_group.ingest, aws_iam_role_policy_attachment.ingest_logs]
}

resource "aws_lambda_function" "upload_url" {
  function_name    = "${var.project}-upload-url"
  role             = aws_iam_role.upload_url.arn
  runtime          = "python3.13"
  handler          = "handler.handler"
  filename         = "${local.dist}/upload_url.zip"
  source_code_hash = filebase64sha256("${local.dist}/upload_url.zip")
  timeout          = 5
  memory_size      = 128

  environment {
    variables = {
      API_KEY = random_password.api_key.result
      BUCKET  = aws_s3_bucket.images.bucket
    }
  }

  depends_on = [aws_cloudwatch_log_group.upload_url, aws_iam_role_policy_attachment.upload_url_logs]
}

resource "aws_lambda_function" "processor" {
  function_name    = "${var.project}-processor"
  role             = aws_iam_role.processor.arn
  runtime          = "python3.13"
  handler          = "handler.handler"
  filename         = "${local.dist}/processor.zip"
  source_code_hash = filebase64sha256("${local.dist}/processor.zip")
  timeout          = 15
  memory_size      = 256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = merge(local.db_env, {
      RAW_TABLE = aws_dynamodb_table.raw.name
      BUCKET    = aws_s3_bucket.images.bucket
    })
  }

  depends_on = [
    aws_cloudwatch_log_group.processor,
    aws_iam_role_policy_attachment.processor_vpc,
    aws_vpc_endpoint.dynamodb,
    aws_vpc_endpoint.s3,
  ]
}

resource "aws_lambda_function" "history" {
  function_name    = "${var.project}-history"
  role             = aws_iam_role.history.arn
  runtime          = "python3.13"
  handler          = "handler.handler"
  filename         = "${local.dist}/history.zip"
  source_code_hash = filebase64sha256("${local.dist}/history.zip")
  timeout          = 15
  memory_size      = 256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = merge(local.db_env, {
      API_KEY   = random_password.api_key.result
      RAW_TABLE = aws_dynamodb_table.raw.name
      BUCKET    = aws_s3_bucket.images.bucket
    })
  }

  depends_on = [
    aws_cloudwatch_log_group.history,
    aws_iam_role_policy_attachment.history_vpc,
    aws_vpc_endpoint.dynamodb,
    aws_vpc_endpoint.s3,
  ]
}

resource "aws_lambda_event_source_mapping" "processor" {
  event_source_arn                   = aws_sqs_queue.measurements.arn
  function_name                      = aws_lambda_function.processor.arn
  batch_size                         = 10
  maximum_batching_window_in_seconds = 1
  function_response_types            = ["ReportBatchItemFailures"]

  scaling_config {
    maximum_concurrency = var.processor_max_concurrency
  }
}

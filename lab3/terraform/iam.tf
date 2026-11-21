data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

locals {
  basic_logs = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  vpc_access = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role" "ingest" {
  name               = "${var.project}-ingest"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "ingest_logs" {
  role       = aws_iam_role.ingest.name
  policy_arn = local.basic_logs
}

resource "aws_iam_role_policy" "ingest" {
  name = "send-to-queue"
  role = aws_iam_role.ingest.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["sqs:SendMessage"]
      Resource = aws_sqs_queue.measurements.arn
    }]
  })
}

resource "aws_iam_role" "upload_url" {
  name               = "${var.project}-upload-url"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "upload_url_logs" {
  role       = aws_iam_role.upload_url.name
  policy_arn = local.basic_logs
}

resource "aws_iam_role_policy" "upload_url" {
  name = "put-camera-images"
  role = aws_iam_role.upload_url.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.images.arn}/camera/*"
    }]
  })
}

resource "aws_iam_role" "processor" {
  name               = "${var.project}-processor"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "processor_vpc" {
  role       = aws_iam_role.processor.name
  policy_arn = local.vpc_access
}

resource "aws_iam_role_policy" "processor" {
  name = "queue-dynamodb-s3"
  role = aws_iam_role.processor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = aws_sqs_queue.measurements.arn
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem"]
        Resource = aws_dynamodb_table.raw.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.images.arn}/camera/*"
      }
    ]
  })
}

resource "aws_iam_role" "history" {
  name               = "${var.project}-history"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "history_vpc" {
  role       = aws_iam_role.history.name
  policy_arn = local.vpc_access
}

resource "aws_iam_role_policy" "history" {
  name = "dynamodb-s3-read"
  role = aws_iam_role.history.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["dynamodb:Query"]
        Resource = aws_dynamodb_table.raw.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.images.arn}/camera/*"
      }
    ]
  })
}

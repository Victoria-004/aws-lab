resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project}-measurements-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "measurements" {
  name = "${var.project}-measurements"

  visibility_timeout_seconds = 90
  message_retention_seconds  = 345600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue_redrive_allow_policy" "dlq" {
  queue_url = aws_sqs_queue.dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.measurements.arn]
  })
}

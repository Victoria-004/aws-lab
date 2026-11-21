resource "aws_appautoscaling_target" "app" {
  service_namespace  = "ecs"
  scalable_dimension = "ecs:service:DesiredCount"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  min_capacity       = var.min_count
  max_capacity       = var.max_count

  # Мінімум і максимум змінюють scheduled actions (день/ніч). Без ignore_changes
  # кожен terraform apply скидав би їх до значень зі змінних.
  lifecycle {
    ignore_changes = [min_capacity, max_capacity]
  }
}

# Step scaling замість target tracking. Target tracking створює аларм, який чекає 3 хвилини
# поспіль над порогом, і це відчутно затримувало появу нових задач. Тут аларм на збільшення
# дивиться на одну хвилину, тож реакція настає за 1-2 хвилини (мінімум задає затримка метрики).
locals {
  requests_dimensions = {
    TargetGroup  = aws_lb_target_group.app.arn_suffix
    LoadBalancer = aws_lb.main.arn_suffix
  }
}

resource "aws_appautoscaling_policy" "scale_out" {
  name               = "${var.project}-scale-out"
  policy_type        = "StepScaling"
  service_namespace  = aws_appautoscaling_target.app.service_namespace
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  resource_id        = aws_appautoscaling_target.app.resource_id

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = var.scale_out_cooldown
    metric_aggregation_type = "Maximum"

    # Перевищення порогу до 2x: +1 задача; більше, ніж у 2 рази: +2 задачі
    step_adjustment {
      scaling_adjustment          = 1
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = var.request_target
    }
    step_adjustment {
      scaling_adjustment          = 2
      metric_interval_lower_bound = var.request_target
    }
  }
}

resource "aws_appautoscaling_policy" "scale_in" {
  name               = "${var.project}-scale-in"
  policy_type        = "StepScaling"
  service_namespace  = aws_appautoscaling_target.app.service_namespace
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  resource_id        = aws_appautoscaling_target.app.resource_id

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = var.scale_in_cooldown
    metric_aggregation_type = "Maximum"

    step_adjustment {
      scaling_adjustment          = -1
      metric_interval_upper_bound = 0
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "scale_out" {
  alarm_name          = "${var.project}-scale-out"
  alarm_description   = "Запитів на задачу за хвилину вище порогу: додати задачі"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "RequestCountPerTarget"
  dimensions          = local.requests_dimensions
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = var.request_target
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_appautoscaling_policy.scale_out.arn]
}

# Зменшення повільне навмисно: 10 хвилин поспіль нижче половини порогу
resource "aws_cloudwatch_metric_alarm" "scale_in" {
  alarm_name          = "${var.project}-scale-in"
  alarm_description   = "Запитів на задачу мало протягом 10 хвилин: прибрати задачу"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "RequestCountPerTarget"
  dimensions          = local.requests_dimensions
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 10
  datapoints_to_alarm = 10
  threshold           = var.request_target / 2
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "breaching"
  alarm_actions       = [aws_appautoscaling_policy.scale_in.arn]
}

# Масштабування за розкладом: удень мінімум 2 задачі, уночі 1.
# Політики step scaling вище працюють у межах нового мінімуму і максимуму.
resource "aws_appautoscaling_scheduled_action" "day" {
  count              = var.schedule_enabled ? 1 : 0
  name               = "${var.project}-day"
  service_namespace  = aws_appautoscaling_target.app.service_namespace
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  resource_id        = aws_appautoscaling_target.app.resource_id
  schedule           = "cron(0 8 * * ? *)"
  timezone           = var.schedule_timezone

  scalable_target_action {
    min_capacity = var.day_min_count
    max_capacity = var.max_count
  }
}

resource "aws_appautoscaling_scheduled_action" "night" {
  count              = var.schedule_enabled ? 1 : 0
  name               = "${var.project}-night"
  service_namespace  = aws_appautoscaling_target.app.service_namespace
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  resource_id        = aws_appautoscaling_target.app.resource_id
  schedule           = "cron(0 22 * * ? *)"
  timezone           = var.schedule_timezone

  scalable_target_action {
    min_capacity = var.night_min_count
    max_capacity = var.max_count
  }

  # AWS не дозволяє одночасно змінювати дві дії для однієї цілі
  depends_on = [aws_appautoscaling_scheduled_action.day]
}

resource "aws_appautoscaling_target" "app" {
  service_namespace  = "ecs"
  scalable_dimension = "ecs:service:DesiredCount"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  min_capacity       = var.min_count
  max_capacity       = var.max_count
}

resource "aws_appautoscaling_policy" "requests" {
  name               = "${var.project}-request-target-tracking"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.app.service_namespace
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  resource_id        = aws_appautoscaling_target.app.resource_id

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.app.arn_suffix}"
    }
    target_value       = var.request_target
    scale_out_cooldown = var.scale_out_cooldown
    scale_in_cooldown  = var.scale_in_cooldown
  }
}

# Масштабування за розкладом: удень мінімум 2 задачі, уночі 1.
# Цільова політика вище продовжує працювати в межах нового мінімуму і максимуму.
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

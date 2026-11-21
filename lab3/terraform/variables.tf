variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "project" {
  type    = string
  default = "iot-lab3"
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "processor_max_concurrency" {
  type        = number
  default     = 5
  description = "Скільки екземплярів обробника можуть працювати одночасно (обмежує кількість з'єднань до бази)"
}

variable "log_retention_days" {
  type    = number
  default = 7
}

variable "api_rate_limit" {
  type        = number
  default     = 300
  description = "Середня кількість запитів за секунду, яку API Gateway пропускає на одну адресу"
}

variable "api_burst_limit" {
  type    = number
  default = 600
}

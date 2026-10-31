variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "project" {
  type    = string
  default = "labdatabase"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "image_tag" {
  type = string
}

variable "app_count" {
  type    = number
  default = 1
}

variable "min_count" {
  type    = number
  default = 1
}

variable "max_count" {
  type    = number
  default = 4
}

variable "cpu_target" {
  type    = number
  default = 60
}

variable "scale_out_cooldown" {
  type    = number
  default = 60
}

variable "scale_in_cooldown" {
  type    = number
  default = 300
}

variable "request_target" {
  type    = number
  default = 50
}

variable "alert_email" {
  type = string
}
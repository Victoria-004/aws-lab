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
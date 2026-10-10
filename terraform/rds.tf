resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-db-subnets"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "main" {
  identifier        = "${var.project}-db"
  engine            = "mysql"
  engine_version    = "8.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "lab3_db"
  username = "admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false
  multi_az               = false

  backup_retention_period = 1
  skip_final_snapshot     = true
  deletion_protection     = false
  apply_immediately       = true
}

output "db_endpoint" {
  value = aws_db_instance.main.address
}
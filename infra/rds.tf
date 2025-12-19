# RDS PostgreSQL (Free Tier)
resource "aws_db_instance" "postgres" {
  identifier     = "orbital-parcel-ops-db"
  engine         = "postgres"
  engine_version = "15.8"

  # Free tier: db.t3.micro (750 hours/month free for 12 months)
  instance_class    = "db.t3.micro"
  allocated_storage = 20 # 20 GB free tier

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password # Use Secrets Manager in production

  # Security
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.public.name
  publicly_accessible    = false

  # Backups (free tier includes automated backups)
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # Performance
  storage_encrypted = true
  multi_az          = false # Single AZ for free tier

  skip_final_snapshot = true # Change to false in production

  tags = {
    Name        = "orbital-parcel-ops-db"
    Environment = var.environment
  }
}

# Security group for RDS
resource "aws_security_group" "rds" {
  name        = "orbital-parcel-ops-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from Lambda"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }



  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "orbital-parcel-ops-rds-sg"
  }
}

# DB subnet group
resource "aws_db_subnet_group" "public" {
  name       = "orbital-parcel-ops-db-subnet-public"
  subnet_ids = aws_subnet.public[*].id

  tags = {
    Name = "orbital-parcel-ops-db-subnet-public"
  }
}

# Store DB credentials in Secrets Manager (recommended)
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "orbital-parcel-ops/db-credentials"
  description = "RDS PostgreSQL credentials"

  tags = {
    Name = "orbital-parcel-ops-db-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = var.db_name
  })
}

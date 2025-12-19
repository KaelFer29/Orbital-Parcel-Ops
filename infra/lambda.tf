# Lambda function
resource "aws_lambda_function" "api" {
  filename         = "${path.module}/../backend/build/lambda.zip"
  function_name    = "orbital-parcel-ops-api"
  role             = aws_iam_role.lambda.arn
  handler          = "app.main.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/../backend/build/lambda.zip")
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${var.db_name}"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_vpc,
    aws_cloudwatch_log_group.lambda
  ]

  tags = {
    Name        = "orbital-parcel-ops-api"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/orbital-parcel-ops-api"
  retention_in_days = 7

  tags = {
    Name = "orbital-parcel-ops-lambda-logs"
  }
}

# Lambda security group
resource "aws_security_group" "lambda" {
  name        = "orbital-parcel-ops-lambda-sg"
  description = "Security group for Lambda function"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "orbital-parcel-ops-lambda-sg"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "orbital-parcel-ops-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "orbital-parcel-ops-lambda-role"
  }
}

# IAM Policy attachments
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Policy for Secrets Manager access
resource "aws_iam_role_policy" "lambda_secrets" {
  name = "lambda-secrets-access"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })
}

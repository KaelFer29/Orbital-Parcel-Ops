# API Gateway URL
output "api_url" {
  description = "API Gateway endpoint URL"
  value       = aws_api_gateway_stage.main.invoke_url
}

# RDS endpoint
output "db_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

# Lambda function name
output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api.function_name
}
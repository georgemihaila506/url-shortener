# CloudWatch alarm: any error on the redirect Lambda within a 1-minute window
# trips it. Easy to demo — invoke the function with a bad event and watch the
# alarm flip from OK to ALARM. No SNS action wired (this is a learning demo); the
# state change is visible in the console and via `describe-alarms`.
resource "aws_cloudwatch_metric_alarm" "redirect_errors" {
  alarm_name          = "${var.project}-redirect-errors"
  alarm_description   = "The redirect Lambda returned an error in the last minute."
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  dimensions          = { FunctionName = aws_lambda_function.redirect.function_name }
  statistic           = "Sum"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  threshold           = 1
  period              = 60
  evaluation_periods  = 1
  treat_missing_data  = "notBreaching" # no data = healthy, not an alarm
}

# One dashboard: Lambda health, API Gateway traffic/latency, DynamoDB usage.
# dashboard_body is CloudWatch's widget JSON, built with jsonencode.
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = var.project

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Lambda — invocations & errors"
          region = var.region
          view   = "timeSeries"
          period = 60
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.shorten.function_name, { stat = "Sum", label = "shorten invocations" }],
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.redirect.function_name, { stat = "Sum", label = "redirect invocations" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.redirect.function_name, { stat = "Sum", label = "redirect errors" }],
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "API Gateway — traffic & latency"
          region = var.region
          view   = "timeSeries"
          period = 60
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiId", aws_apigatewayv2_api.http.id, { stat = "Sum", label = "requests" }],
            ["AWS/ApiGateway", "4xx", "ApiId", aws_apigatewayv2_api.http.id, { stat = "Sum", label = "4xx" }],
            ["AWS/ApiGateway", "5xx", "ApiId", aws_apigatewayv2_api.http.id, { stat = "Sum", label = "5xx" }],
            ["AWS/ApiGateway", "Latency", "ApiId", aws_apigatewayv2_api.http.id, { stat = "Average", label = "latency (ms)" }],
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "DynamoDB — consumed capacity"
          region = var.region
          view   = "timeSeries"
          period = 60
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.urls.name, { stat = "Sum", label = "read units" }],
            ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", "TableName", aws_dynamodb_table.urls.name, { stat = "Sum", label = "write units" }],
          ]
        }
      },
    ]
  })
}

output "dashboard_url" {
  description = "CloudWatch dashboard for the fleet of Lambdas + API + table."
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards/dashboard/${aws_cloudwatch_dashboard.main.dashboard_name}"
}

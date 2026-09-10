# Package the Python source into a zip. Deps are stdlib + boto3 (boto3 is in the
# Lambda runtime), so there is no pip/build step — just zip src/ as-is. The zip
# root ends up containing `urlshortener/`, so the handler path is dotted from there.
data "archive_file" "app" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/build/app.zip"
}

# The role the Lambda runs as: it may be assumed by the Lambda service...
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.project}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

# ...and it may write to CloudWatch Logs (the AWS-managed basic-execution policy).
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "hello" {
  function_name    = "${var.project}-hello"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "urlshortener.handlers.hello.handler"
  filename         = data.archive_file.app.output_path
  source_code_hash = data.archive_file.app.output_base64sha256
}

resource "aws_lambda_function" "shorten" {
  function_name    = "${var.project}-shorten"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "urlshortener.handlers.shorten.handler"
  filename         = data.archive_file.app.output_path
  source_code_hash = data.archive_file.app.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.urls.name
    }
  }
}

resource "aws_lambda_function" "redirect" {
  function_name    = "${var.project}-redirect"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "urlshortener.handlers.redirect.handler"
  filename         = data.archive_file.app.output_path
  source_code_hash = data.archive_file.app.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.urls.name
    }
  }
}

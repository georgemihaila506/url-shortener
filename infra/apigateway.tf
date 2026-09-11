# HTTP API (API Gateway v2) — the managed front door that routes HTTP to Lambda.
resource "aws_apigatewayv2_api" "http" {
  name          = "${var.project}-api"
  protocol_type = "HTTP"
}

# AWS_PROXY: pass the raw request to Lambda and return its response verbatim.
resource "aws_apigatewayv2_integration" "hello" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.hello.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "hello" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /hello"
  target    = "integrations/${aws_apigatewayv2_integration.hello.id}"
}

# $default stage with auto-deploy: serve at the API's root URL, no manual deploys.
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  # Stage-wide throttle (a token bucket): burst = bucket size, rate = refill/sec.
  # Requests over the limit get a 429. Generous enough for normal use; a
  # concurrent burst will still trip it. (The book's rate-limiter, as config.)
  default_route_settings {
    throttling_burst_limit = 20
    throttling_rate_limit  = 10
  }
}

# Let this specific API invoke the Lambda (Lambda denies by default).
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hello.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

# --- POST /shorten -----------------------------------------------------------
resource "aws_apigatewayv2_integration" "shorten" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.shorten.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "shorten" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "POST /shorten"
  target    = "integrations/${aws_apigatewayv2_integration.shorten.id}"
}

resource "aws_lambda_permission" "shorten_apigw" {
  statement_id  = "AllowAPIGatewayInvokeShorten"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.shorten.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

# --- GET /{code} (the redirect) ----------------------------------------------
# A greedy path param. Literal routes like "GET /hello" still win over this, so
# only unmatched GETs fall through to the redirect.
resource "aws_apigatewayv2_integration" "redirect" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.redirect.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "redirect" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /{code}"
  target    = "integrations/${aws_apigatewayv2_integration.redirect.id}"
}

resource "aws_lambda_permission" "redirect_apigw" {
  statement_id  = "AllowAPIGatewayInvokeRedirect"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.redirect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

# --- GET /stats/{code} -------------------------------------------------------
# Two-segment literal prefix, so it wins over the greedy "GET /{code}" redirect.
resource "aws_apigatewayv2_integration" "stats" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.stats.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "stats" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /stats/{code}"
  target    = "integrations/${aws_apigatewayv2_integration.stats.id}"
}

resource "aws_lambda_permission" "stats_apigw" {
  statement_id  = "AllowAPIGatewayInvokeStats"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stats.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

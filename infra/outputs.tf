output "hello_url" {
  description = "Invoke URL for the hello endpoint (curl this to verify M0)."
  value       = "${aws_apigatewayv2_api.http.api_endpoint}/hello"
}

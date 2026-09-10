output "hello_url" {
  description = "Invoke URL for the hello endpoint (curl this to verify M0)."
  value       = "${aws_apigatewayv2_api.http.api_endpoint}/hello"
}

output "shorten_url" {
  description = "POST here to mint a short link (M2)."
  value       = "${aws_apigatewayv2_api.http.api_endpoint}/shorten"
}

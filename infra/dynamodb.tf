# The one table: short code (pk) -> long_url + created_at + clicks.
# On-demand billing (PAY_PER_REQUEST): no capacity planning, scales with use,
# generous free tier — right for a personal-scale, spiky workload.
resource "aws_dynamodb_table" "urls" {
  name         = "${var.project}-urls"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }
}

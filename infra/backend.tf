# Store this stack's state in the S3 bucket created by ./bootstrap — versioned and
# private, so state survives a lost laptop and is safe to share across machines.
# Locking is S3-native (use_lockfile), the modern replacement for a DynamoDB lock
# table. Backend config must be literal values — no variables/interpolation here.
terraform {
  backend "s3" {
    bucket       = "url-shortener-tfstate-944921954001"
    key          = "url-shortener/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true
  }
}

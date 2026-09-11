# Bootstrap — creates the S3 bucket that stores the MAIN stack's Terraform state.
#
# This config keeps its OWN state locally and is applied once, rarely touched. It
# lives apart from the app on purpose: `terraform destroy` on the app must never
# try to delete the bucket that holds its state. Chicken-and-egg, solved by
# separation.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "project" {
  type    = string
  default = "url-shortener"
}

# Account id makes the bucket name globally unique (S3 names are global).
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "tfstate" {
  bucket = "${var.project}-tfstate-${data.aws_caller_identity.current.account_id}"
}

# Versioning keeps every state write, so a bad apply/migration is recoverable.
resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Terraform state can contain sensitive values — lock the bucket down completely.
resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "state_bucket" {
  value = aws_s3_bucket.tfstate.bucket
}

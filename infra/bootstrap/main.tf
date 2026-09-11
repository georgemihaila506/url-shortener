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

# --- GitHub Actions OIDC (M7) ------------------------------------------------
# Let CI assume a role via OpenID Connect — no long-lived AWS keys stored in
# GitHub. Actions presents a short-lived OIDC token; AWS trusts it if it comes
# from this repo.
variable "github_repo" {
  type = string
  # Immutable-subject form: owner@<owner-id>/repo@<repo-id>. This account's GitHub
  # OIDC embeds numeric ids in the `sub` claim (protection against owner/repo
  # rename or re-creation), so the trust condition must match those ids, not the
  # plain owner/repo path. Ids are unforgeable, so this is the more secure form.
  default = "georgemihaila506@37144843/url-shortener@1363127508"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"] # AWS validates via its own CA store
}

data "aws_iam_policy_document" "github_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    # Only tokens minted for THIS repo may assume the role.
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:*"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.project}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_assume.json
}

# A deploy role legitimately needs broad access (it manages IAM roles, Lambda,
# API Gateway, DynamoDB, state, alarms). Scoped to the services this project
# uses — not full AdministratorAccess. In production you'd tighten resources too.
data "aws_iam_policy_document" "github_deploy" {
  statement {
    actions = [
      "lambda:*",
      "apigateway:*",
      "dynamodb:*",
      "s3:*",
      "iam:*",
      "cloudwatch:*",
      "logs:*",
      "sts:GetCallerIdentity",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "github_deploy" {
  name   = "${var.project}-github-deploy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_deploy.json
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}

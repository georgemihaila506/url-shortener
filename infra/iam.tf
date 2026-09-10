# Least privilege: the Lambda role may do ONLY these three actions, and ONLY on
# our one table (not "dynamodb:*", not "*"). This is the security lesson of M2 —
# grant the minimum the code actually uses (put/get for now, update for M4 clicks).
data "aws_iam_policy_document" "dynamo_access" {
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
    ]
    resources = [aws_dynamodb_table.urls.arn]
  }
}

resource "aws_iam_role_policy" "dynamo_access" {
  name   = "${var.project}-dynamo-access"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.dynamo_access.json
}

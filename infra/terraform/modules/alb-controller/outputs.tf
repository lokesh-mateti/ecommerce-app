output "iam_role_arn" {
  description = "ARN of the IRSA role used by the Load Balancer Controller"
  value       = aws_iam_role.lbc.arn
}

output "iam_role_name" {
  description = "Name of the IRSA role"
  value       = aws_iam_role.lbc.name
}

output "helm_release_status" {
  description = "Status of the Helm release"
  value       = helm_release.lbc.status
}

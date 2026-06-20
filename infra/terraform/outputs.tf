output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "oidc_provider_arn" {
  description = "Used when configuring IRSA roles for service accounts (e.g. ArgoCD, External Secrets)"
  value       = module.eks.oidc_provider_arn
}

output "ecr_repository_urls" {
  description = "ECR repo URLs — used in the Jenkinsfile to push images"
  value       = module.ecr.repository_urls
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "configure_kubectl" {
  description = "Run this command to update your local kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
output "jenkins_url" {
  description = "Jenkins UI URL"
  value       = module.jenkins.jenkins_url
}

output "jenkins_public_ip" {
  description = "Jenkins server public IP"
  value       = module.jenkins.jenkins_public_ip
}

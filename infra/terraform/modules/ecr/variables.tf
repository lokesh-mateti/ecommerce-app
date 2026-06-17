variable "repository_names" {
  description = "List of ECR repository names to create, one per microservice"
  type        = list(string)
  default     = ["product-service", "order-service", "api-gateway"]
}

variable "environment" {
  type = string
}

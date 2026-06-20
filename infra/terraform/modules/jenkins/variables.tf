variable "vpc_id" {
  description = "VPC ID to launch Jenkins in"
  type        = string
}

variable "subnet_id" {
  description = "Public subnet ID for Jenkins EC2"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "SSH key pair name (must exist in AWS already)"
  type        = string
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "dev"
}

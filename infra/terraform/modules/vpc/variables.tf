variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Availability zones to spread subnets across"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (used by EKS worker nodes)"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (used by load balancers / NAT gateways)"
  type        = list(string)
}

variable "cluster_name" {
  description = "EKS cluster name, used for required subnet tags"
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod) for tagging"
  type        = string
}

module "vpc" {
  source = "./modules/vpc"

  vpc_cidr             = var.vpc_cidr
  azs                  = var.azs
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs
  cluster_name         = var.cluster_name
  environment          = var.environment
}

module "eks" {
  source = "./modules/eks"

  cluster_name        = var.cluster_name
  cluster_version     = var.cluster_version
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  node_instance_types = var.node_instance_types
  node_desired_size   = var.node_desired_size
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
  environment         = var.environment
}

module "ecr" {
  source = "./modules/ecr"

  repository_names = ["product-service", "order-service", "api-gateway"]
  environment      = var.environment
}

module "jenkins" {
  source = "./modules/jenkins"

  vpc_id        = module.vpc.vpc_id
  subnet_id     = module.vpc.public_subnet_ids[0]
  instance_type = var.jenkins_instance_type
  key_name      = var.jenkins_key_name
  environment   = var.environment
}

module "alb_controller" {
  source = "./modules/alb-controller"

  cluster_name      = var.cluster_name
  vpc_id            = module.vpc.vpc_id
  aws_region        = var.aws_region
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url
  environment       = var.environment

  depends_on = [module.eks]
}

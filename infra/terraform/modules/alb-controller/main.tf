# ---------------------------------------------------------------------------
# IAM Policy — grants the controller permissions to manage ALB/NLB resources
# ---------------------------------------------------------------------------
resource "aws_iam_policy" "lbc" {
  name        = "${var.cluster_name}-AWSLoadBalancerControllerIAMPolicy"
  description = "IAM policy for AWS Load Balancer Controller on ${var.cluster_name}"
  policy      = file("${path.module}/iam-policy.json")

  tags = {
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# IRSA — IAM Role for Service Account
# The LBC pod assumes this role via the OIDC trust. No node-level permissions
# needed; the pod gets exactly the permissions it needs and nothing more.
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "lbc_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }

    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lbc" {
  name               = "${var.cluster_name}-aws-load-balancer-controller"
  assume_role_policy = data.aws_iam_policy_document.lbc_assume_role.json

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "lbc" {
  role       = aws_iam_role.lbc.name
  policy_arn = aws_iam_policy.lbc.arn
}

# ---------------------------------------------------------------------------
# Helm release — installs the controller into kube-system
# serviceAccount.create=true so Helm creates the SA and annotates it with
# the IAM role ARN — that's what makes IRSA work.
# ---------------------------------------------------------------------------
resource "helm_release" "lbc" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = var.chart_version
  namespace  = "kube-system"

  wait    = true
  timeout = 300

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "serviceAccount.create"
    value = "true"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.lbc.arn
  }

  set {
    name  = "region"
    value = var.aws_region
  }

  set {
    name  = "vpcId"
    value = var.vpc_id
  }

  set {
    name  = "replicaCount"
    value = "2"
  }

  depends_on = [aws_iam_role_policy_attachment.lbc]
}

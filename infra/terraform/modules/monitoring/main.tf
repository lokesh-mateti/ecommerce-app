resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = var.namespace
    labels = {
      environment = var.environment
    }
  }
}

resource "null_resource" "prometheus_helm_repo" {
  provisioner "local-exec" {
    command = "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update prometheus-community"
  }

  triggers = {
    repo_url = "https://prometheus-community.github.io/helm-charts"
  }
}

resource "helm_release" "kube_prometheus_stack" {
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = var.chart_version
  namespace  = var.namespace

  wait    = true
  timeout = 600

  # Grafana config
  set {
    name  = "grafana.adminPassword"
    value = var.grafana_admin_password
  }

  set {
    name  = "grafana.service.type"
    value = "ClusterIP"
  }

  # Enable persistence for Grafana
  set {
    name  = "grafana.persistence.enabled"
    value = "false"
  }

  # Prometheus retention
  set {
    name  = "prometheus.prometheusSpec.retention"
    value = "7d"
  }

  # Scrape all namespaces
  set {
    name  = "prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  # Reduce resource usage for demo
  set {
    name  = "prometheus.prometheusSpec.resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "prometheus.prometheusSpec.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "grafana.resources.requests.memory"
    value = "128Mi"
  }

  set {
    name  = "grafana.resources.requests.cpu"
    value = "50m"
  }

  # Disable components not needed for demo
  set {
    name  = "alertmanager.enabled"
    value = "true"
  }

  set {
    name  = "nodeExporter.enabled"
    value = "true"
  }

  set {
    name  = "kubeStateMetrics.enabled"
    value = "true"
  }

  depends_on = [
    kubernetes_namespace.monitoring,
    null_resource.prometheus_helm_repo
  ]
}

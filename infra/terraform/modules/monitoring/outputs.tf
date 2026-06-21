output "grafana_namespace" {
  description = "Namespace where monitoring stack is deployed"
  value       = var.namespace
}

output "helm_release_status" {
  description = "Helm release status"
  value       = helm_release.kube_prometheus_stack.status
}

output "grafana_access_command" {
  description = "Command to access Grafana UI via port-forward"
  value       = "kubectl port-forward svc/kube-prometheus-stack-grafana 3000:80 -n ${var.namespace}"
}

output "prometheus_access_command" {
  description = "Command to access Prometheus UI via port-forward"
  value       = "kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n ${var.namespace}"
}

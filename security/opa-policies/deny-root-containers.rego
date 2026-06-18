# OPA/Conftest policy: deny containers running as root
# Apply with: conftest test <kubernetes-manifest.yaml> --policy security/opa-policies/
# Or enforce via OPA Gatekeeper installed in EKS cluster

package kubernetes.security

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf(
        "Deployment '%s' container '%s' must set securityContext.runAsNonRoot: true",
        [input.metadata.name, container.name]
    )
}

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.securityContext.runAsUser == 0
    msg := sprintf(
        "Deployment '%s' container '%s' must not run as root (runAsUser: 0)",
        [input.metadata.name, container.name]
    )
}

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation == true
    msg := sprintf(
        "Deployment '%s' container '%s' must set allowPrivilegeEscalation: false",
        [input.metadata.name, container.name]
    )
}

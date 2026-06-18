# OPA/Conftest policy: require resource requests and limits on all containers
# Prevents unbounded resource consumption that can destabilize the EKS cluster

package kubernetes.resources

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf(
        "Deployment '%s' container '%s' must specify resources.limits.cpu",
        [input.metadata.name, container.name]
    )
}

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf(
        "Deployment '%s' container '%s' must specify resources.limits.memory",
        [input.metadata.name, container.name]
    )
}

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.requests.cpu
    msg := sprintf(
        "Deployment '%s' container '%s' must specify resources.requests.cpu",
        [input.metadata.name, container.name]
    )
}

deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.requests.memory
    msg := sprintf(
        "Deployment '%s' container '%s' must specify resources.requests.memory",
        [input.metadata.name, container.name]
    )
}

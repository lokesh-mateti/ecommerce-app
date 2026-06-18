# 🛒 E-Commerce Microservices Platform

A production-grade microservices application deployed on AWS EKS using a full DevSecOps pipeline with GitOps delivery. Built to demonstrate real-world practices across containerization, CI/CD, security scanning, infrastructure-as-code, and GitOps.

---

## 🏗️ Architecture Overview

```
                        ┌─────────────────────────────────────────┐
                        │              AWS EKS Cluster             │
                        │                                          │
Internet ──► ALB ──►   │  api-gateway ──► product-service         │
                        │              └──► order-service          │
                        │                                          │
                        └─────────────────────────────────────────┘
                                         ▲
                                         │ ArgoCD syncs
                              ┌──────────┴──────────┐
                              │   ecommerce-gitops   │
                              │   (Helm charts)      │
                              └──────────▲───────────┘
                                         │ Jenkins updates image tag
                              ┌──────────┴──────────┐
                              │   ecommerce-app      │
                              │   (this repo)        │
                              └─────────────────────┘
```

---

## 📦 Microservices

| Service | Description | Port |
|---|---|---|
| `api-gateway` | Single entry point — JWT auth + request routing | 8000 |
| `product-service` | Product catalog CRUD API | 8000 |
| `order-service` | Order management, validates against product-service | 8000 |

All services are built with **Python FastAPI**, containerized with **multi-stage Docker builds**, and run as **non-root users**.

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| **Cloud** | AWS (EKS, ECR, VPC, IAM, ALB) |
| **Container Orchestration** | Kubernetes (EKS) |
| **Infrastructure as Code** | Terraform |
| **CI/CD** | Jenkins |
| **GitOps** | ArgoCD + Helm |
| **Security Scanning** | Trivy, Bandit, Safety, OPA |
| **Language** | Python 3.12 / FastAPI |

---

## 🔒 DevSecOps Pipeline

Every commit to this repo triggers a Jenkins pipeline with the following stages:

```
Checkout → Install Deps → Unit Tests → SAST (Bandit) → SCA (Safety) → Docker Build → Container Scan (Trivy) → Push to ECR → Update GitOps Repo
```

- **SAST**: Bandit scans Python source for insecure code patterns
- **SCA**: Safety checks `requirements.txt` for known CVEs in dependencies
- **Container Scan**: Trivy scans the built image for HIGH/CRITICAL vulnerabilities, secrets, and misconfigurations
- **GitOps Update**: On success, Jenkins commits the new image tag to `ecommerce-gitops` — ArgoCD detects the change and auto-deploys to EKS

---

## 📁 Repository Structure

```
ecommerce-app/
├── services/
│   ├── api-gateway/        # JWT auth + reverse proxy to backend services
│   ├── order-service/      # Order management microservice
│   └── product-service/    # Product catalog microservice
├── infra/
│   └── terraform/
│       ├── modules/
│       │   ├── vpc/        # VPC, subnets, NAT gateway
│       │   ├── eks/        # EKS cluster, node group, OIDC provider
│       │   └── ecr/        # ECR repositories with scan-on-push
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── backend.tf
├── ci/
│   └── Jenkinsfile         # Multi-stage DevSecOps pipeline
└── security/
    ├── trivy-config.yaml   # Trivy scan configuration
    └── opa-policies/       # OPA policies enforcing security standards
```

---

## 🚀 Getting Started

### Prerequisites
- AWS CLI configured with appropriate IAM permissions
- Terraform >= 1.7
- kubectl
- Docker
- Python 3.12

### 1. Provision Infrastructure
```bash
cd infra/terraform

# Create S3 bucket and DynamoDB table for remote state first
# Then:
terraform init
terraform plan
terraform apply
```

### 2. Configure kubectl
```bash
# Output from terraform apply gives this command:
aws eks update-kubeconfig --region us-east-1 --name ecommerce-cluster
```

### 3. Run Services Locally
```bash
cd services/product-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

cd services/order-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

cd services/api-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Run Tests
```bash
cd services/product-service
pytest tests/ -v
```

---

## 🔐 Security Highlights

- All containers run as **non-root users** (UID 1000)
- Multi-stage Docker builds minimize final image attack surface
- JWT authentication centralized at the API Gateway
- Trivy blocks HIGH/CRITICAL CVEs from reaching ECR
- OPA policies enforce `runAsNonRoot` and resource limits across all deployments
- Secrets injected via **Kubernetes Secrets** (never in code or Helm values)
- Terraform remote state encrypted in S3 with DynamoDB locking

---

## 📊 GitOps Flow

```
Developer pushes code
        │
        ▼
Jenkins pipeline runs (build → test → scan → push to ECR)
        │
        ▼
Jenkins updates image tag in ecommerce-gitops repo
        │
        ▼
ArgoCD detects git change → auto-syncs to EKS
        │
        ▼
New version running in cluster (zero manual kubectl apply)
```

See the [ecommerce-gitops](https://github.com/lokesh-mateti/ecommerce-gitops) repo for Helm charts and ArgoCD manifests.

---

## 👤 Author

**Lokesh Mateti**
- GitHub: [@lokesh-mateti](https://github.com/lokesh-mateti)
- LinkedIn: [linkedin.com/in/lokesh-mateti](https://linkedin.com/in/lokesh-mateti)

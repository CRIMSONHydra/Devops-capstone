## GIT
![alt text](image.png)

## Application
![alt text](image-1.png)

AN ecommerce admin dashboard.
Backend: Fastapi + alembic. UV instead of vanilla python
Frontend: Vite + React
DB: psql + sqlite(test/dev)

## Tests
![alt text](image-2.png)

## Commit history

TODO

## Docker

Frontend listens on port 3000, nginx proxies /api to backend container port 8000. All 3 containers are on their own networks where FE <-> BE and BE <-> DB only. psql container has a persistent docker volume

![alt text](image-3.png)

![alt text](image-4.png)

## CI/CD

Frontend and backend build and tests, docker build and push to GHCR
![alt text](image-5.png)

Backend image: ghcr.io/crimsonhydra/devops-capstone/backend:6c5134ca865e00b7a7572c6beac4bf94e3113946
![alt text](image-6.png)

Frontend image: ghcr.io/crimsonhydra/devops-capstone/frontend:6c5134ca865e00b7a7572c6beac4bf94e3113946
![alt text](image-7.png)

## Trivy

### Frontend

capstone-frontend (Alpine 3.21.3): 41 findings, 2 CRITICAL and 39 HIGH. All of them have a fix available.

The packages involved are OpenSSL (libcrypto3/libssl3, 18 findings including the CRITICAL CVE-2026-31789), libexpat, libpng, libxml2 and c-ares.

The cause is the base image: nginx-unprivileged:1.27-alpine is built on an old Alpine release.

A newer nginx tag on a current Alpine release would likely clear most of them.

### Backend

![alt text](image-8.png)
capstone-backend: 47 HIGH, no CRITICAL.

44 are OS packages on Debian 13.7 with no fix available. They're util-linux libraries such as bsdutils, libblkid1, libmount1 and libuuid1. 

Fixed these by changing the image from ubuntu to ubuntu-alpine which doesnt contain a lot of the unnecessary system libraries

3 are in the Python package starlette, and they're fixable. Starlette is pulled in by FastAPI 0.115.6. 
Upgrading FastAPI should fix them.

![alt text](image-9.png)

## Terraform

1 EKS control plane
2 t3.micro EC2
1 20 gb node disk EBS
VPC, subnet, IGW, route table, IAM, NAT

### Plan
![alt text](image-10.png)
![alt text](image-11.png)

### Apply
![alt text](image-12.png)

### Console

VPC
![alt text](image-13.png)

EKS
![alt text](image-14.png)

Subnets
![alt text](image-15.png)

Route tables
![alt text](image-16.png)

IGW
![alt text](image-17.png)

EC2
![alt text](image-18.png)

### Destroy

![alt text](image-19.png)
![alt text](image-20.png)

![alt text](image-21.png)

## Helm

![alt text](image-22.png)

Running via minikube tunnel from kubernetes applied via helm
![alt text](image-23.png)

## GitOps

### Prometheus

![alt text](image-25.png)
![alt text](image-26.png)

### Grafana

![alt text](image-24.png)

### /metrics
![alt text](image-27.png)
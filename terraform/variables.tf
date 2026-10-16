variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "Name of the EKS cluster (also used to name the VPC and IAM roles)"
  type        = string
  default     = "ecommerce-admin"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "node_instance_type" {
  description = "Free-tier eligible size. t3.micro fits ~4 pods per node; use t3.small for ~11"
  type        = string
  default     = "t3.micro"
}

variable "node_desired_size" {
  type    = number
  default = 2
}

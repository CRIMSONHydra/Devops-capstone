terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Credentials are never stored here: use `aws configure`, AWS_PROFILE or AWS_* env vars.
provider "aws" {
  region = var.region
}

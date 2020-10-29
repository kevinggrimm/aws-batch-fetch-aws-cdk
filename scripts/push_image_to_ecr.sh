#!/usr/bin/env bash

# TODO: Pass in repository, image name (hardcoded for now)
# Make sure ECR repository/image match with those you configured
PROFILE=$1
REGION=$2
ACCOUNT_ID=$(aws sts get-caller-identity \
  --profile $PROFILE \
  --query Account \
  --output text)

# Build the image with tag awsbatch/fetch_and_run
docker build -t awsbatch/fetch_and_run ../fetch-and-run/

# Login to ECR 
aws ecr get-login-password --region $REGION \
--profile $PROFILE | docker login --username AWS \
--password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Tag image
docker tag awsbatch/fetch_and_run:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/fetch-and-run:latest

# Push image to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/fetch-and-run:latest
#!/usr/bin/env bash

PROFILE=$1
REGION=$2
REPOSITORY_NAME=$3

aws ecr create-repository \
  --repository-name $REPOSITORY_NAME \
  --profile $PROFILE --region $REGION
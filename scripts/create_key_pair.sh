#!/usr/bin/env bash

PROFILE=$1
REGION=$2
KEY_NAME=$3

# Create key pair
aws ec2 create-key-pair \
  --key-name $3 \
  --query KeyMaterial \
  --output text \
  --profile $PROFILE \
  --region $REGION > $KEY_NAME.pem

# Set permissions
chmod +x $KEY_NAME.pem
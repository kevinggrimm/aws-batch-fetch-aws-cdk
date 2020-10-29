#!/usr/bin/env bash

# General Params
PROFILE=$1
REGION=$2

# Batch Params
JOB_NAME=$3

# Get job definitions that start with `fetchandrun`
JOB_DEFINITION=$(aws batch describe-job-definitions \
  --query 'jobDefinitions[?starts_with(jobDefinitionName, `fetchandrun`) == `true`]|[*].[jobDefinitionName]' \
  --output text --profile $PROFILE --region $REGION)

# Get job queue named 'fetch-and-run-queue'
JOB_QUEUE=$(aws batch describe-job-queues \
  --query 'jobQueues[?jobQueueName==`fetch-and-run-queue`]|[*].[jobQueueArn]' \
  --output text --profile $PROFILE --region $REGION)

# Submit job 
# Replace value of BATCH_FILE_S3_URL with your bucket name
aws batch submit-job \
  --job-name $JOB_NAME \
  --job-queue $JOB_QUEUE \
  --job-definition $JOB_DEFINITION \
  --container-overrides '{
    "command": ["myjob.sh","60"], "environment": [ {"name": "BATCH_FILE_TYPE", "value": "script"}, {"name": "BATCH_FILE_S3_URL", "value": "s3://kg-fetch-and-run/myjob.sh"} ] }' \
  --profile $PROFILE \
  --region $REGION
#!/usr/bin/env bash

PROFILE=$1
REGION=$2
BUCKET=$3

aws s3 cp myjob.sh s3://$BUCKET/$FILE --profile $PROFILE
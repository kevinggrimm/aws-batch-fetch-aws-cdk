# Overview
Simple "Fetch & Run" AWS Bach Job using the AWS CDK. Follows the steps outlined in the **AWS Compute Blog** [here](https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/)

# Steps
- Run `scripts/create_key_pair.sh` to generate an EC2 Key Pair
- Run `scripts/create_ecr_repository.sh` to create the ECR repository
- Run `scripts/push_image_to_ecr.sh` to push build, tag and push the image to ECR
- Run `scripts/push_job_to_s3.sh` to push the Batch job to S3
- Deploy the app with `cdk synth`
- Run `scripts/submit_batch_job.sh` to submit a Batch Job


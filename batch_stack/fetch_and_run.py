from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_batch as batch,
    aws_ecr_assets as ecr_assets,
    aws_secretsmanager as secrets,
)

ACCOUNT_ID="YOUR_ACCOUNT_ID"

# VPC 
IP_ADDRESS="YOUR_IP_ADDRESS"
PORTS=[80, 22]

# IAM Roles
BATCH_SERVICE_ROLE_ARN=f"arn:aws:iam::{ACCOUNT_ID}:role/service-role/AWSBatchServiceRole"
ECS_INSTANCE_ROLE_ARN=f"arn:aws:iam::{ACCOUNT_ID}:role/ecsInstanceRole"
BATCH_JOB_ROLE_ARN=f"arn:aws:iam::{ACCOUNT_ID}:role/batchJobRole"

# ECR / BATCH
ECR_REPOSITORY_NAME="fetch-and-run"
KEY_PAIR='fetch-and-run-kp'


class FetchAndRunStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ========================
        # VPC
        # ========================
        
        # VPC
        vpc = ec2.Vpc(
            self, 'fetch-and-run-vpc',
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='public-subnet',
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            ],
            nat_gateways=0
        )

        # Security Group
        sg = ec2.SecurityGroup(
            self, 'fetch-and-run-sg',
            vpc=vpc,
            description='SG for fetch and run',
            security_group_name='fetch-and-run-sg'
        )

        # Ingress from IP address via HTTP, SSH
        for port in PORTS:
            sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(IP_ADDRESS),
                connection=ec2.Port.tcp(port)   
            )

        # ========================
        # IAM
        # ========================

        '''
        I. Batch Instance Role
        - Makes calls to other AWS services on your behalf to
        manage the resources that you use with the service
        '''

        batch_service_role = iam.Role.from_role_arn(
            self, 'batch-service-role',
            role_arn=BATCH_SERVICE_ROLE_ARN
        )

        '''
        II. ECS Instance Role
        - Batch compute environmens are populated with ECS container instances,
        which run the ECS container agent locally
        - ECS container agent makes calls to AWS APIs on your behalf
        - Container instances that run the agent require a policy and role for
        these services to know that the agent belongs to you

        - Instance Profile uses the batch instance role name
        - This is fed into the compute environment    
        '''

        batch_instance_role = iam.Role.from_role_arn(
            self, 'batch-instance-role',
            role_arn=ECS_INSTANCE_ROLE_ARN
        )

        instance_profile = iam.CfnInstanceProfile(
            self, 'instance-profile',
            roles=[batch_instance_role.role_name]
        )

        '''
        Job Role
        - Used in the job definition
        - IAM role that the container can assume for AWS permissions
        
        When the fetch_and_run image runs as an AWS Batch job, it fetches the job
        script from Amazon S3. You need an IAM role that the AWS Batch job can use
        to access S3

        Trusted Entity --> AWS service --> Elastic Container Service --> Elastic
        Container Service Task 
        - In the Role's trust relationship, this will be displayed as follows:
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "ecs-tasks.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
                }
            ]
        }

        Default is for a role to be created
        '''
        batch_job_role = iam.Role.from_role_arn(
            self, 'batch-job-role',
            role_arn=BATCH_JOB_ROLE_ARN
        )

        # ========================
        # ECR
        # ========================
        '''
        Repository

        TODO: Evaluate integrating repository into CDK (in this stack or another)
        '''
        ecr_repository = ecr.Repository.from_repository_name(
            self, 'ecr-repository',
            repository_name=ECR_REPOSITORY_NAME
        )
        
        '''
        Container Image
        
        NOTE: We are pulling the image directly from ECR. Pushed before stack is created.
        - Can alternatively create the image from files in the stack (commented out)
        
        TODO: Evaluate ability to programatically update the tag.
        - Manually updating the tag follows approach of pushing image before stack creation/updates
        - Review adding alphanumeric tag as opposed to simply 'latest' --> more detail for auditing
        '''
        # image_asset = ecr_assets.DockerImageAsset(
        #     self, 'docker-image',
        #     directory='./fetch-and-run',
        #     file='./Dockerfile'
        # )
        # image = ecs.ContainerImage.from_docker_image_asset(image_asset)

        image = ecs.ContainerImage.from_ecr_repository(
            repository=ecr_repository,
            tag='latest'
        )

        # ========================
        # BATCH
        # ========================

        '''
        I. Compute Environment
        - Execution runtime of submitted batch jobs 
        '''
        compute_environment = batch.ComputeEnvironment(
            self, 'batch-compute-environment',
            compute_environment_name='batch-compute-environment',
            compute_resources=batch.ComputeResources(
                vpc=vpc,
                # BEST_FIT_PROGRESSIVE will select an additional instance type that is large enough to meet the requirements of the jobs in the queue, with a preference for an instance type with a lower cost.
                allocation_strategy=batch.AllocationStrategy.BEST_FIT_PROGRESSIVE,
                compute_resources_tags={
                    "name": "fetch-and-run"
                },
                ec2_key_pair=KEY_PAIR,
                instance_role=instance_profile.attr_arn,
                security_groups=[sg],
                type=batch.ComputeResourceType.ON_DEMAND,
                vpc_subnets=ec2.SubnetSelection(
                        subnet_type=ec2.SubnetType.PUBLIC)
            ),
            service_role=batch_service_role,
        )

        '''
        II. Job Queue
        - Queue where batch jobs can be submitted
        '''

        job_queue = batch.JobQueue(
            self, 'fetch-and-run-queue',
            compute_environments=[
                batch.JobQueueComputeEnvironment(
                    compute_environment=compute_environment,
                    order=1
                )],
            job_queue_name='fetch-and-run-queue'
        )

        '''
        III. Job Definition
        - Group various job properties (image, resource requirements, env variables)
        into a single definition. Definitionns are used to job submission time
        
        TODO: Build out functionality for the following:
        - `command` => The command that is passed to the container. If you provide a shell command as a single string, you have to quote command-line arguments
        - `environment` => The environment variables to pass to the container
        - `mount_points` => The mount points for data volumes in your container
        - `volumes` => A list of data volumes used in a job.
        
        NOTE: Can optionally add command, environment variables directly in code
        - Alternatively can reference them in `fetch_and_run.sh`
        '''

        job_definition = batch.JobDefinition(
            self, 'fetch-and-run-job-definition',
            container=batch.JobDefinitionContainer(
                image=image,
                job_role=batch_job_role,
                # The hard limit (in MiB) of memory to present to the container
                memory_limit_mib=500,

                # The number of vCPUs reserved for the container. Each vCPU is equivalent to 1,024 CPU
                vcpus=1,
                user="nobody"
            )
        )
# Wild Rydes - DevOps Infrastructure as Code

Complete AWS infrastructure stack for Wild Rydes application using CloudFormation, featuring ECS Fargate, Application Load Balancer, and fully automated CI/CD pipeline.

## Architecture Overview

This solution deploys a highly scalable, highly redundant containerized application with the following components:

### Infrastructure Components
- **VPC**: Custom VPC with 2 public subnets across different Availability Zones
- **ECS Fargate**: Serverless container orchestration running Python Flask application
- **Application Load Balancer**: Distributes traffic across ECS tasks
- **Auto Scaling**: Automatically scales ECS tasks based on CPU utilization (70% target)
- **ECR**: Private Docker container registry
- **CI/CD Pipeline**: Automated deployment via CodePipeline and CodeBuild
- **SNS Notifications**: Email alerts for pipeline events and infrastructure health
- **CloudWatch**: Comprehensive monitoring and logging

### Application
- **Framework**: Python Flask
- **Port**: 3000
- **Endpoints**:
  - `/` - Welcome page with service info
  - `/health` - Health check endpoint
  - `/about` - Company information

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Git** installed
4. **GitHub Repository**: https://github.com/Nanaesi2020/devopsfinal.git
5. **CodeStar Connection**: Already created and configured
   - ARN: `arn:aws:codeconnections:us-east-1:276713243373:connection/94af2dd6-d42c-4213-9b72-f4b67b3c8d4a`

## Project Structure

```
devops-final/
├── app/
│   ├── app.py              # Flask application
│   └── requirements.txt    # Python dependencies
├── cloudformation.yaml     # Complete infrastructure stack
├── buildspec.yml          # CodeBuild build specification
├── Dockerfile             # Container image definition
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Deployment Instructions

### Step 1: Initial Docker Image Build

Before deploying the CloudFormation stack, you need to create an initial Docker image in ECR:

```powershell
# Set variables
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = "276713243373"
$REPO_NAME = "wild-rydes-app"

# Create ECR repository manually (if not using CloudFormation first)
aws ecr create-repository --repository-name $REPO_NAME --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Build Docker image
docker build -t $REPO_NAME .

# Tag the image
docker tag "${REPO_NAME}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest"

# Push to ECR
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest"
```

### Step 2: Deploy CloudFormation Stack

#### Option A: Using AWS Console

1. Navigate to AWS CloudFormation Console
2. Click **Create Stack** → **With new resources**
3. Upload `cloudformation.yaml`
4. Provide stack name: `wild-rydes-stack`
5. Review parameters (defaults are pre-configured):
   - **NotificationEmail**: hinsonnanaesi@gmail.com
   - **GitHubRepo**: Nanaesi2020/devopsfinal
   - **CodeStarConnectionArn**: (pre-filled)
6. Acknowledge IAM resource creation
7. Click **Create Stack**

#### Option B: Using AWS CLI

```powershell
aws cloudformation create-stack `
  --stack-name wild-rydes-stack `
  --template-body file://cloudformation.yaml `
  --capabilities CAPABILITY_NAMED_IAM `
  --region us-east-1 `
  --parameters `
    ParameterKey=NotificationEmail,ParameterValue=hinsonnanaesi@gmail.com `
    ParameterKey=GitHubRepo,ParameterValue=Nanaesi2020/devopsfinal `
    ParameterKey=CodeStarConnectionArn,ParameterValue=arn:aws:codeconnections:us-east-1:276713243373:connection/94af2dd6-d42c-4213-9b72-f4b67b3c8d4a
```

#### Monitor Stack Creation

```powershell
# Check stack status
aws cloudformation describe-stacks --stack-name wild-rydes-stack --region us-east-1 --query "Stacks[0].StackStatus"

# Watch stack events
aws cloudformation describe-stack-events --stack-name wild-rydes-stack --region us-east-1 --max-items 10
```

### Step 3: Confirm SNS Subscription

1. Check email inbox for **AWS Notification - Subscription Confirmation**
2. Click **Confirm subscription** link
3. You'll receive notifications for:
   - Pipeline execution success/failure
   - Build failures
   - ECS high CPU utilization
   - Unhealthy ALB targets

### Step 4: Verify Deployment

```powershell
# Get Load Balancer URL
$ALB_URL = aws cloudformation describe-stacks `
  --stack-name wild-rydes-stack `
  --region us-east-1 `
  --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" `
  --output text

Write-Host "Application URL: $ALB_URL"

# Test the application
curl $ALB_URL
curl "$ALB_URL/health"
curl "$ALB_URL/about"
```

### Step 5: Trigger CI/CD Pipeline

The pipeline automatically triggers on git push:

```powershell
# Make a code change
echo "# Update" >> app/app.py

# Commit and push
git add .
git commit -m "Trigger pipeline"
git push origin main
```

Monitor pipeline in AWS Console → CodePipeline

## Stack Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| EnvironmentName | wild-rydes | Environment prefix for resources |
| VpcCIDR | 10.0.0.0/16 | VPC CIDR block |
| PublicSubnet1CIDR | 10.0.1.0/24 | Public subnet 1 CIDR |
| PublicSubnet2CIDR | 10.0.2.0/24 | Public subnet 2 CIDR |
| ContainerPort | 3000 | Application port |
| ContainerCpu | 256 | CPU units (0.25 vCPU) |
| ContainerMemory | 512 | Memory in MB |
| DesiredCount | 2 | Initial task count |
| MinCapacity | 2 | Minimum tasks |
| MaxCapacity | 6 | Maximum tasks |
| GitHubRepo | Nanaesi2020/devopsfinal | GitHub repository |
| GitHubBranch | main | Branch to track |
| CodeStarConnectionArn | (provided) | CodeStar connection |
| NotificationEmail | hinsonnanaesi@gmail.com | SNS notification email |

## Stack Outputs

After deployment, the stack provides these outputs:

- **LoadBalancerURL**: Public URL to access the application
- **ECRRepositoryURI**: Docker image repository URI
- **ECSClusterName**: ECS cluster name
- **ECSServiceName**: ECS service name
- **CodePipelineName**: CI/CD pipeline name
- **SNSTopicArn**: Notification topic ARN

## Auto Scaling Configuration

- **Metric**: CPU Utilization
- **Target**: 70%
- **Scale Out**: 60 seconds cooldown
- **Scale In**: 300 seconds cooldown
- **Range**: 2-6 tasks

## Monitoring & Alarms

CloudWatch alarms configured for:

1. **Pipeline Success** - Notification on successful deployment
2. **Pipeline Failure** - Alert on pipeline failures
3. **Build Failure** - Alert on CodeBuild failures
4. **ECS High CPU** - Alert when CPU > 85% for 10 minutes
5. **Unhealthy Targets** - Alert when ALB has unhealthy targets

## CI/CD Pipeline Stages

1. **Source**: Pull code from GitHub via CodeStar Connection
2. **Build**: 
   - Build Docker image
   - Tag with commit hash
   - Push to ECR
   - Generate imagedefinitions.json
3. **Deploy**: Update ECS service with new image

## Troubleshooting

### Stack Creation Fails

```powershell
# Get failure reason
aws cloudformation describe-stack-events `
  --stack-name wild-rydes-stack `
  --region us-east-1 `
  --query "StackEvents[?ResourceStatus=='CREATE_FAILED']"
```

### Pipeline Fails at Build Stage

```powershell
# Check CodeBuild logs
aws logs tail /codebuild/wild-rydes --follow --region us-east-1
```

### ECS Tasks Not Starting

```powershell
# Check ECS service events
aws ecs describe-services `
  --cluster wild-rydes-cluster `
  --services wild-rydes-service `
  --region us-east-1 `
  --query "services[0].events[0:5]"
```

### Check ECS Task Logs

```powershell
# View application logs
aws logs tail /ecs/wild-rydes --follow --region us-east-1
```

## Updating the Stack

```powershell
aws cloudformation update-stack `
  --stack-name wild-rydes-stack `
  --template-body file://cloudformation.yaml `
  --capabilities CAPABILITY_NAMED_IAM `
  --region us-east-1
```

## Deleting the Stack

**Warning**: This will delete all resources including the ECR repository and images.

```powershell
# Empty S3 bucket first
$BUCKET_NAME = aws cloudformation describe-stack-resources `
  --stack-name wild-rydes-stack `
  --region us-east-1 `
  --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId" `
  --output text

aws s3 rm "s3://$BUCKET_NAME" --recursive --region us-east-1

# Delete ECR images
$REPO_NAME = "wild-rydes-app"
aws ecr batch-delete-image `
  --repository-name $REPO_NAME `
  --region us-east-1 `
  --image-ids imageTag=latest

# Delete stack
aws cloudformation delete-stack --stack-name wild-rydes-stack --region us-east-1

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name wild-rydes-stack --region us-east-1
```

## Cost Optimization

- **Fargate**: ~$30-60/month for 2-6 tasks
- **ALB**: ~$20/month
- **NAT Gateway**: Not used (using public subnets)
- **ECR**: First 50GB free
- **CodePipeline**: $1/active pipeline/month
- **CloudWatch**: Free tier covers most usage

## Security Features

- **VPC Isolation**: Resources in private network
- **Security Groups**: Minimal required access
- **IAM Roles**: Least privilege principle
- **ECR Image Scanning**: Automatic vulnerability scanning
- **S3 Encryption**: AES256 encryption at rest
- **Public Access Block**: S3 buckets not publicly accessible

## Contact

- **Email**: hinsonnanaesi@gmail.com
- **Repository**: https://github.com/Nanaesi2020/devopsfinal.git

## License

This project is created for educational purposes as part of DevOps coursework.

---

**Developed by**: Wild Rydes DevOps Team  
**Last Updated**: December 4, 2025  
**Region**: us-east-1

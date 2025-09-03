"""
Test stack management commands
"""
import click
import subprocess
import os
import time
from ai_lls_lib.cli.aws_client import AWSClient

@click.group(name="test-stack")
def test_stack_group():
    """Test stack management"""
    pass

@test_stack_group.command(name="deploy")
@click.option("--stack-name", default="ai-lls-lib-test", help="Test stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def deploy_test_stack(stack_name, profile, region):
    """Deploy the test stack"""
    template_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "template.yaml"
    )

    if not os.path.exists(template_path):
        click.echo(f"Test stack template not found at {template_path}")
        click.echo("Creating minimal test stack template...")

        # Create a minimal test stack
        template_content = """AWSTemplateFormatVersion: '2010-09-09'
Description: Minimal test stack for ai-lls-lib integration testing

Resources:
  TestPhoneCache:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-phone-cache"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: phone_number
          AttributeType: S
      KeySchema:
        - AttributeName: phone_number
          KeyType: HASH
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  TestUploadBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-uploads-${AWS::AccountId}"
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldTestFiles
            Status: Enabled
            ExpirationInDays: 1

  TestQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-test-queue"
      MessageRetentionPeriod: 3600  # 1 hour for test

Outputs:
  CacheTableName:
    Value: !Ref TestPhoneCache
  BucketName:
    Value: !Ref TestUploadBucket
  QueueUrl:
    Value: !Ref TestQueue
"""

        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, 'w') as f:
            f.write(template_content)
        click.echo(f"Created {template_path}")

    # Deploy using AWS CLI
    cmd = [
        "aws", "cloudformation", "deploy",
        "--template-file", template_path,
        "--stack-name", stack_name,
        "--capabilities", "CAPABILITY_IAM"
    ]

    if profile:
        cmd.extend(["--profile", profile])
    if region:
        cmd.extend(["--region", region])

    click.echo(f"Deploying test stack '{stack_name}'...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("Test stack deployed successfully!")

            # Show outputs
            aws = AWSClient(region=region, profile=profile)
            outputs = aws.get_stack_outputs(stack_name)
            if outputs:
                click.echo("\nStack Outputs:")
                for key, value in outputs.items():
                    click.echo(f"  {key}: {value}")
        else:
            click.echo(f"Deployment failed: {result.stderr}", err=True)
    except Exception as e:
        click.echo(f"Error deploying test stack: {e}", err=True)

@test_stack_group.command(name="delete")
@click.option("--stack-name", default="ai-lls-lib-test", help="Test stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
@click.confirmation_option(prompt="Delete test stack and all resources?")
def delete_test_stack(stack_name, profile, region):
    """Delete the test stack"""
    aws = AWSClient(region=region, profile=profile)

    try:
        # Empty S3 bucket first
        outputs = aws.get_stack_outputs(stack_name)
        if 'BucketName' in outputs:
            bucket_name = outputs['BucketName']
            click.echo(f"Emptying bucket {bucket_name}...")

            # List and delete all objects
            try:
                objects = aws.s3.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects:
                    for obj in objects['Contents']:
                        aws.s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            except:
                pass  # Bucket might not exist

        # Delete stack
        click.echo(f"Deleting stack '{stack_name}'...")
        aws.cloudformation.delete_stack(StackName=stack_name)

        # Wait for deletion
        click.echo("Waiting for stack deletion...")
        waiter = aws.cloudformation.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)

        click.echo("Test stack deleted successfully!")

    except Exception as e:
        click.echo(f"Error deleting test stack: {e}", err=True)

@test_stack_group.command(name="status")
@click.option("--stack-name", default="ai-lls-lib-test", help="Test stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def test_stack_status(stack_name, profile, region):
    """Show test stack status"""
    aws = AWSClient(region=region, profile=profile)

    try:
        response = aws.cloudformation.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]

        click.echo(f"\nTest Stack: {stack_name}")
        click.echo("=" * 50)
        click.echo(f"Status: {stack['StackStatus']}")
        click.echo(f"Created: {stack.get('CreationTime', 'N/A')}")

        if 'Outputs' in stack:
            click.echo("\nOutputs:")
            for output in stack['Outputs']:
                click.echo(f"  {output['OutputKey']}: {output['OutputValue']}")

    except aws.cloudformation.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            click.echo(f"Test stack '{stack_name}' does not exist")
        else:
            click.echo(f"Error: {e}", err=True)

@test_stack_group.command(name="test")
@click.option("--stack-name", default="ai-lls-lib-test", help="Test stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def run_integration_tests(stack_name, profile, region):
    """Run integration tests against test stack"""
    aws = AWSClient(region=region, profile=profile)

    try:
        # Check stack exists
        outputs = aws.get_stack_outputs(stack_name)
        if not outputs:
            click.echo(f"Test stack '{stack_name}' not found. Deploy it first.")
            return

        # Set environment variables for tests
        os.environ['TEST_STACK_NAME'] = stack_name
        os.environ['TEST_CACHE_TABLE'] = outputs.get('CacheTableName', '')
        os.environ['TEST_BUCKET'] = outputs.get('BucketName', '')
        os.environ['TEST_QUEUE_URL'] = outputs.get('QueueUrl', '')

        if profile:
            os.environ['AWS_PROFILE'] = profile
        if region:
            os.environ['AWS_REGION'] = region

        click.echo(f"Running integration tests against '{stack_name}'...")

        # Run pytest
        cmd = ["pytest", "tests/integration", "-v"]
        result = subprocess.run(cmd, cwd=os.path.dirname(template_path))

        if result.returncode == 0:
            click.echo("\nIntegration tests passed!")
        else:
            click.echo("\nSome tests failed", err=True)

    except Exception as e:
        click.echo(f"Error running tests: {e}", err=True)

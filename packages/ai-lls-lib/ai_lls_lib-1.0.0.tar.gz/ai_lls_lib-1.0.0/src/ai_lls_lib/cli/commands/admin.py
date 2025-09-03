"""
Administrative commands for user and credit management
"""
import click
import json
from datetime import datetime
from ai_lls_lib.cli.aws_client import AWSClient

@click.group(name="admin")
def admin_group():
    """Administrative commands"""
    pass

@admin_group.command(name="user-credits")
@click.argument("user_id")
@click.option("--add", type=int, help="Add credits")
@click.option("--set", "set_credits", type=int, help="Set credits to specific value")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def user_credits(user_id, add, set_credits, stack, profile, region):
    """Manage user credits"""
    aws = AWSClient(region=region, profile=profile)
    credits_table = aws.get_table_name(stack, "CreditsTable")

    try:
        table = aws.dynamodb.Table(credits_table)

        # Get current credits
        response = table.get_item(Key={"user_id": user_id})
        current = response.get('Item', {}).get('credits', 0)

        click.echo(f"User {user_id} - Current credits: {current}")

        if add:
            new_credits = current + add
            table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET credits = :val, updated_at = :now",
                ExpressionAttributeValues={
                    ":val": new_credits,
                    ":now": datetime.utcnow().isoformat()
                }
            )
            click.echo(f"Added {add} credits. New balance: {new_credits}")

        elif set_credits is not None:
            table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET credits = :val, updated_at = :now",
                ExpressionAttributeValues={
                    ":val": set_credits,
                    ":now": datetime.utcnow().isoformat()
                }
            )
            click.echo(f"Set credits to {set_credits}")

    except Exception as e:
        click.echo(f"Error managing credits: {e}", err=True)

@admin_group.command(name="api-keys")
@click.option("--user", help="Filter by user ID")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def list_api_keys(user, stack, profile, region):
    """List API keys"""
    aws = AWSClient(region=region, profile=profile)
    keys_table = aws.get_table_name(stack, "ApiKeysTable")

    try:
        if user:
            # Query by user using GSI
            table = aws.dynamodb.Table(keys_table)
            response = table.query(
                IndexName='gsi_user',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user}
            )
            items = response.get('Items', [])
        else:
            # Scan all
            items = aws.scan_table(keys_table)

        if not items:
            click.echo("No API keys found")
            return

        click.echo(f"\nAPI Keys ({len(items)} total):")
        click.echo("=" * 60)

        for item in items:
            click.echo(f"Key ID: {item.get('api_key_id', 'N/A')}")
            click.echo(f"User: {item.get('user_id', 'N/A')}")
            click.echo(f"Created: {item.get('created_at', 'N/A')}")
            click.echo(f"Last Used: {item.get('last_used', 'Never')}")
            click.echo("-" * 60)

    except Exception as e:
        click.echo(f"Error listing API keys: {e}", err=True)

@admin_group.command(name="queue-stats")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def queue_stats(stack, profile, region):
    """Show SQS queue statistics"""
    aws = AWSClient(region=region, profile=profile)

    try:
        # Get queue URLs from stack
        outputs = aws.get_stack_outputs(stack)

        # Find queue URLs or construct them
        queue_name = f"{stack}-bulk-processing"
        dlq_name = f"{stack}-bulk-processing-dlq"

        # Get queue attributes
        queues = [
            ("Processing Queue", queue_name),
            ("Dead Letter Queue", dlq_name)
        ]

        for display_name, queue in queues:
            try:
                response = aws.sqs.get_queue_url(QueueName=queue)
                queue_url = response['QueueUrl']

                attrs = aws.sqs.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['All']
                )['Attributes']

                click.echo(f"\n{display_name}:")
                click.echo(f"  Messages Available: {attrs.get('ApproximateNumberOfMessages', 0)}")
                click.echo(f"  Messages In Flight: {attrs.get('ApproximateNumberOfMessagesNotVisible', 0)}")
                click.echo(f"  Messages Delayed: {attrs.get('ApproximateNumberOfMessagesDelayed', 0)}")

            except aws.sqs.exceptions.QueueDoesNotExist:
                click.echo(f"\n{display_name}: Not found")

    except Exception as e:
        click.echo(f"Error getting queue stats: {e}", err=True)

@admin_group.command(name="secrets")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--show", is_flag=True, help="Show secret values (CAREFUL!)")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def manage_secrets(stack, show, profile, region):
    """Manage secrets"""
    aws = AWSClient(region=region, profile=profile)
    secret_name = f"{stack}-secrets"

    try:
        response = aws.secretsmanager.describe_secret(SecretId=secret_name)
        click.echo(f"\nSecret: {secret_name}")
        click.echo(f"ARN: {response['ARN']}")
        click.echo(f"Last Updated: {response.get('LastChangedDate', 'N/A')}")

        if show and click.confirm("Show secret values? This will display sensitive data!"):
            secret_value = aws.secretsmanager.get_secret_value(SecretId=secret_name)
            secrets = json.loads(secret_value['SecretString'])

            click.echo("\nSecret Values:")
            for key, value in secrets.items():
                # Mask most of the value
                masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
                click.echo(f"  {key}: {masked}")

    except aws.secretsmanager.exceptions.ResourceNotFoundException:
        click.echo(f"Secret '{secret_name}' not found")
    except Exception as e:
        click.echo(f"Error managing secrets: {e}", err=True)

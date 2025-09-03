"""
Cache management commands
"""
import click
import json
from datetime import datetime, timedelta
from ai_lls_lib.cli.aws_client import AWSClient

@click.group(name="cache")
def cache_group():
    """Cache management commands"""
    pass

@cache_group.command(name="stats")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def cache_stats(stack, profile, region):
    """Show cache statistics"""
    aws = AWSClient(region=region, profile=profile)
    cache_table = aws.get_table_name(stack, "PhoneCacheTable")

    try:
        # Get table description for item count
        table = aws.dynamodb.Table(cache_table)
        desc = table.meta.client.describe_table(TableName=cache_table)

        click.echo(f"\nCache Table: {cache_table}")
        click.echo("=" * 50)
        click.echo(f"Item Count: {desc['Table']['ItemCount']:,}")
        click.echo(f"Table Size: {desc['Table']['TableSizeBytes']:,} bytes")
        click.echo(f"Status: {desc['Table']['TableStatus']}")

        # Sample some items to show age distribution
        items = aws.scan_table(cache_table, limit=100)
        if items:
            now = datetime.utcnow()
            ages = []
            for item in items:
                if 'verified_at' in item:
                    verified = datetime.fromisoformat(item['verified_at'].replace('Z', '+00:00'))
                    age = (now - verified.replace(tzinfo=None)).days
                    ages.append(age)

            if ages:
                click.echo(f"\nCache Age (sample of {len(ages)} items):")
                click.echo(f"  Newest: {min(ages)} days")
                click.echo(f"  Oldest: {max(ages)} days")
                click.echo(f"  Average: {sum(ages)/len(ages):.1f} days")

    except Exception as e:
        click.echo(f"Error getting cache stats: {e}", err=True)

@cache_group.command(name="get")
@click.argument("phone_number")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
def cache_get(phone_number, stack, profile, region):
    """Get cached entry for a phone number"""
    from ai_lls_lib.core.verifier import PhoneVerifier
    from ai_lls_lib.core.cache import DynamoDBCache

    aws = AWSClient(region=region, profile=profile)
    cache_table = aws.get_table_name(stack, "PhoneCacheTable")

    # Normalize phone first
    verifier = PhoneVerifier(cache=DynamoDBCache(table_name=cache_table))
    try:
        normalized = verifier.normalize_phone(phone_number)
    except ValueError as e:
        click.echo(f"Invalid phone: {e}", err=True)
        return

    # Get from cache
    cache = DynamoDBCache(table_name=cache_table)
    result = cache.get(normalized)

    if result:
        click.echo(f"\nCached entry for {normalized}:")
        click.echo(json.dumps(result.dict() if hasattr(result, 'dict') else result, indent=2, default=str))
    else:
        click.echo(f"No cache entry found for {normalized}")

@cache_group.command(name="invalidate")
@click.argument("phone_number")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
@click.confirmation_option(prompt="Are you sure you want to invalidate this cache entry?")
def cache_invalidate(phone_number, stack, profile, region):
    """Invalidate cached entry for a phone number"""
    from ai_lls_lib.core.verifier import PhoneVerifier
    from ai_lls_lib.core.cache import DynamoDBCache

    aws = AWSClient(region=region, profile=profile)
    cache_table = aws.get_table_name(stack, "PhoneCacheTable")

    # Normalize phone
    verifier = PhoneVerifier(cache=DynamoDBCache(table_name=cache_table))
    try:
        normalized = verifier.normalize_phone(phone_number)
    except ValueError as e:
        click.echo(f"Invalid phone: {e}", err=True)
        return

    # Delete from cache
    try:
        aws.delete_item(cache_table, {"phone_number": normalized})
        click.echo(f"Cache entry invalidated for {normalized}")
    except Exception as e:
        click.echo(f"Error invalidating cache: {e}", err=True)

@cache_group.command(name="clear")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--older-than", type=int, help="Clear entries older than N days")
@click.option("--profile", help="AWS profile")
@click.option("--region", help="AWS region")
@click.confirmation_option(prompt="This will clear cache entries. Continue?")
def cache_clear(stack, older_than, profile, region):
    """Clear cache entries"""
    aws = AWSClient(region=region, profile=profile)
    cache_table = aws.get_table_name(stack, "PhoneCacheTable")

    if older_than:
        click.echo(f"Clearing entries older than {older_than} days...")
        cutoff = datetime.utcnow() - timedelta(days=older_than)

        # Scan and delete old entries
        items = aws.scan_table(cache_table, limit=1000)
        deleted = 0

        for item in items:
            if 'verified_at' in item:
                verified = datetime.fromisoformat(item['verified_at'].replace('Z', '+00:00'))
                if verified.replace(tzinfo=None) < cutoff:
                    aws.delete_item(cache_table, {"phone_number": item['phone_number']})
                    deleted += 1

        click.echo(f"Deleted {deleted} entries older than {older_than} days")
    else:
        click.echo("Full cache clear not implemented for safety. Use --older-than option.")

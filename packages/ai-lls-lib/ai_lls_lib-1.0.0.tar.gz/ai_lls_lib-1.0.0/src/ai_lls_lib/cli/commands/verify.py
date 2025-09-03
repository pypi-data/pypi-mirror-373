"""
Verification commands - direct phone verification bypassing API
"""
import click
import json
from datetime import datetime
from ai_lls_lib.core.verifier import PhoneVerifier
from ai_lls_lib.core.cache import DynamoDBCache
from ai_lls_lib.cli.aws_client import AWSClient

@click.group(name="verify")
def verify_group():
    """Phone verification commands"""
    pass

@verify_group.command(name="phone")
@click.argument("phone_number")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--skip-cache", is_flag=True, help="Skip cache lookup")
@click.option("--profile", help="AWS profile to use")
@click.option("--region", help="AWS region")
def verify_phone(phone_number, stack, skip_cache, profile, region):
    """Verify a single phone number"""
    aws = AWSClient(region=region, profile=profile)

    # Get cache table name from stack
    cache_table = aws.get_table_name(stack, "PhoneCacheTable")
    click.echo(f"Using cache table: {cache_table}")

    # Initialize cache and verifier
    cache = DynamoDBCache(table_name=cache_table)
    verifier = PhoneVerifier(cache=cache)

    try:
        if skip_cache:
            # Force fresh lookup
            normalized = verifier.normalize_phone(phone_number)
            line_type = verifier._check_line_type_sync(normalized)
            dnc = verifier._check_dnc_sync(normalized)
            result = {
                "phone_number": normalized,
                "line_type": line_type,
                "dnc": dnc,
                "cached": False,
                "verified_at": datetime.utcnow().isoformat(),
                "source": "cli-direct"
            }
        else:
            result = verifier.verify_sync(phone_number)
            result = result.dict() if hasattr(result, 'dict') else result

        # Display results
        click.echo("\n" + "=" * 40)
        click.echo(f"Phone: {result['phone_number']}")
        click.echo(f"Line Type: {result['line_type']}")
        click.echo(f"DNC Status: {'Yes' if result['dnc'] else 'No'}")
        click.echo(f"From Cache: {'Yes' if result.get('cached') else 'No'}")
        click.echo(f"Verified: {result.get('verified_at', 'Unknown')}")
        click.echo("=" * 40)

        if click.confirm("\nShow JSON output?"):
            click.echo(json.dumps(result, indent=2, default=str))

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Verification failed: {e}", err=True)

@verify_group.command(name="bulk")
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output CSV file")
@click.option("--stack", default="landline-api", help="CloudFormation stack name")
@click.option("--profile", help="AWS profile to use")
@click.option("--region", help="AWS region")
def verify_bulk(csv_file, output, stack, profile, region):
    """Process a CSV file for bulk verification"""
    from ai_lls_lib.core.processor import BulkProcessor

    aws = AWSClient(region=region, profile=profile)
    cache_table = aws.get_table_name(stack, "PhoneCacheTable")

    cache = DynamoDBCache(table_name=cache_table)
    verifier = PhoneVerifier(cache=cache)
    processor = BulkProcessor(verifier=verifier)

    click.echo(f"Processing {csv_file}...")

    try:
        # Process CSV
        results = processor.process_csv_sync(csv_file)
        click.echo(f"\nProcessed {len(results)} phone numbers")

        # Show summary
        mobile_count = sum(1 for r in results if r.line_type == "mobile")
        landline_count = sum(1 for r in results if r.line_type == "landline")
        dnc_count = sum(1 for r in results if r.dnc)
        cached_count = sum(1 for r in results if r.cached)

        click.echo("\nSummary:")
        click.echo(f"  Mobile: {mobile_count}")
        click.echo(f"  Landline: {landline_count}")
        click.echo(f"  On DNC: {dnc_count}")
        click.echo(f"  From Cache: {cached_count}")

        # Generate output if requested
        if output:
            processor.generate_results_csv(csv_file, results, output)
            click.echo(f"\nResults saved to: {output}")

    except Exception as e:
        click.echo(f"Bulk processing failed: {e}", err=True)

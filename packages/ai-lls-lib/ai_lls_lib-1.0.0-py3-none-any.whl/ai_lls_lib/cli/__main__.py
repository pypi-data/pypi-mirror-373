"""
Landline Scrubber CLI entry point
"""
import click
import sys
from ai_lls_lib.cli.commands import verify, cache, admin, test_stack

@click.group()
@click.version_option(version="0.1.0", prog_name="ai-lls")
def cli():
    """Landline Scrubber CLI - Administrative and debugging tools"""
    pass

# Register command groups
cli.add_command(verify.verify_group)
cli.add_command(cache.cache_group)
cli.add_command(admin.admin_group)
cli.add_command(test_stack.test_stack_group)

def main():
    """Main entry point"""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

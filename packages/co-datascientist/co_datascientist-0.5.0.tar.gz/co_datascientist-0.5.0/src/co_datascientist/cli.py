import asyncio
import logging
import sys
from pathlib import Path

import click
from yaspin import yaspin
import yaml
from . import co_datascientist_api, mcp_local_server
from .settings import settings
from .workflow_runner import workflow_runner
from .cloud_utils.databricks_utils import get_code_from_databricks_config

def ensure_keyring_works():
    """
    Ensure that keyring backend works; fall back to plaintext file if not.
    """
    try:
        import keyring
        test_service = "test_service"
        test_username = "test_user"
        test_password = "test_password"
        keyring.set_password(test_service, test_username, test_password)
        retrieved = keyring.get_password(test_service, test_username)
        keyring.delete_password(test_service, test_username)
        if retrieved == test_password:
            return
    except Exception:
        pass
    try:
        import keyring
        import keyrings.alt.file
        keyring.set_keyring(keyrings.alt.file.PlaintextKeyring())
        click.echo("⚠️  Using file-based keyring for secure storage")
    except ImportError:
        click.echo("❌ Please install keyrings.alt: pip install keyrings.alt")
        sys.exit(1)


def print_section_header(title: str, emoji: str = ""):
    header = f"{emoji} {title}" if emoji else title
    click.echo(f"\n{header}")
    click.echo("─" * len(header))


def print_success(message: str):
    click.echo(f"✅ {message}")


def print_info(message: str):
    click.echo(f"ℹ️  {message}")


def print_warning(message: str):
    click.echo(f"⚠️ {message}")


def print_error(message: str):
    click.echo(f"❌ {message}")


@click.group()
@click.option('--reset-openai-key', is_flag=True, help='Reset the OpenAI API key')
@click.pass_context
def main(ctx, reset_openai_key: bool):
    # Initialize keyring and logging
    ensure_keyring_works()
    logging.basicConfig(level=settings.log_level)
    logging.info(f"settings: {settings.model_dump()}")

    print_section_header("Co-DataScientist CLI", "🚀")

    # Reset OpenAI key if requested
    if reset_openai_key:
        settings.delete_openai_key()
        print_success("OpenAI key removed. Using free tier.")

    # Ensure API key exists for all commands except token management
    if ctx.invoked_subcommand not in ('set-token', 'openai-key'):
        try:
            settings.get_api_key()
            if not settings.api_key or not settings.api_key.get_secret_value():
                print_error("No API key found. Please run 'set-token' to configure your API key.")
                sys.exit(1)
        except Exception as e:
            print_error(f"Error loading API key: {e}")
            sys.exit(1)


@main.command()
def mcp_server():
    """Start the local MCP server"""
    print_section_header("MCP Server", "🔌")
    print_info("Starting MCP server... Press Ctrl+C to exit.")
    asyncio.run(mcp_local_server.run_mcp_server())


@main.command()
@click.option('--token', required=False, help='Your API key (if not provided, you will be prompted)')
def set_token(token):
    """Set your Co-DataScientist API key"""
    from pydantic import SecretStr

    print_section_header("Set API Key", "🔐")
    if not token:
        token = click.prompt("Please enter your API key", hide_input=True)
    if not token:
        print_error("No API key provided. Aborting.")
        return

    settings.api_key = SecretStr(token)
    try:
        asyncio.run(co_datascientist_api.test_connection())
        print_success("Token validated successfully!")
    except Exception as e:
        print_error(f"Token validation failed: {e}")
        return

    try:
        import keyring
        keyring.set_password(settings.service_name, "user", token)
        print_success("API key saved and will be remembered between sessions!")
    except Exception as e:
        print_error(f"Failed to save API key: {e}")
        print_info("You can set the CO_DATASCIENTIST_API_KEY environment variable for persistence.")


@main.command()
@click.option('--script-path', required=False, type=click.Path(exists=True), help='Absolute path to the python code to improve')
@click.option('--cloud-config', required=False, type=click.Path(exists=True), help='Path to cloud config file (mutually exclusive with --script-path)')
@click.option('--python-path', required=False, type=click.Path(), default=sys.executable, show_default=True, help='Path to the python interpreter to use')
@click.option('--parallel', required=False, type=int, default=1, show_default=True, help='Number of code versions to run concurrently')
@click.option('--no-preflight', is_flag=True, help='Disable preflight Q&A (enabled by default)')
@click.option('--debug', is_flag=True, help='Show detailed logs')

# TODO: need a way to check we have a specific script path or cloud path...

def run(script_path, python_path, parallel, debug, cloud_config, no_preflight):
    """Run the workflow on your script"""
    try:
        # if databricks we need to grab the code from the databricks config to have as a string locally like the input local code.
        if cloud_config:
            #how to read a yaml file to an object? 
            with open(cloud_config, 'r') as file:
                config = yaml.safe_load(file)
            # TODO: find a way to get the baseline code from the cloud!
            baseline_code = get_code_from_databricks_config(config['databricks']['code_path']) #TODO: check over.
            project_path = config['databricks']['volume_uri'] #TODO:  check over. not needed for POC.
        elif script_path:
            baseline_code = Path(script_path).read_text()
            project_path = Path(script_path).parent
            # Set default config for local script runs (no cloud integration)
            config = {'databricks': False}
        else:
            print_error("No script path or cloud config provided. Aborting.")
            return
        
        if not debug:
            click.echo()
        with yaspin(text="Initializing workflow...", color="magenta") as spinner:
            asyncio.run(
                workflow_runner.run_workflow(
                    baseline_code, python_path, project_path, {**config, 'parallel': max(1, int(parallel or 1)), 'preflight': (not bool(no_preflight))}, spinner, debug
                )
            )
        click.echo()
    except Exception as e:
        msg = str(e)
        if "Unauthorized" in msg or "401" in msg:
            print_error("Authentication failed. Please run 'set-token' again.")
        else:
            print_error(f"Error running workflow: {e}")


def _costs_disabled():
    return None


@main.command()
def status():
    """Show current usage status"""
    try:
        with yaspin(text="Checking status...", color="yellow") as spinner:
            status = asyncio.run(co_datascientist_api.get_user_usage_status())
        print_section_header("Usage Status", "🔍")
        # TODO: display status bar, etc.
    except Exception as e:
        msg = str(e)
        if "Unauthorized" in msg or "401" in msg:
            print_error("Authentication failed. Please run 'set-token' again.")
        else:
            print_error(f"Error fetching status: {e}")


@main.command()
@click.option('--remove', is_flag=True, help='Remove stored OpenAI key')
def openai_key(remove):
    """Manage your OpenAI API key for unlimited usage"""
    print_section_header("OpenAI Key Management", "🔑")
    if remove:
        settings.delete_openai_key()
        print_success("OpenAI key removed. Using free tier.")
    else:
        current = settings.get_openai_key(prompt_if_missing=False)
        if current:
            print_success("OpenAI key is currently configured.")
            print_info("Your requests use your OpenAI account for unlimited usage.")
            print_info("Use '--remove' flag to switch back to free tier.")
        else:
            print_info("No OpenAI key configured. Using free tier.")
            settings.get_openai_key(prompt_if_missing=True)


if __name__ == '__main__':
    main()

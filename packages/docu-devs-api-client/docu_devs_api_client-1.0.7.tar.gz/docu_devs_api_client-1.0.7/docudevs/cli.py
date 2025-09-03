import asyncio
import json
from pathlib import Path

import click

from .docudevs_client import (
    DocuDevsClient,
    TemplateFillRequest,
    UploadCommand,
    UploadDocumentBody,
    UploadFilesBody,
    OcrCommand,
)


def async_command(f):
    """Decorator to run async click commands."""
    import functools

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--api-url", default="https://api.docudevs.ai", help="API URL")
@click.option("--token", help="Authentication token (or set DOCUDEVS_TOKEN env var)")
@click.pass_context
def cli(ctx, api_url: str, token: str):
    """DocuDevs CLI tool"""
    ctx.ensure_object(dict)
    
    # Get token from environment if not provided
    if not token:
        import os
        env_token = os.getenv('DOCUDEVS_TOKEN') or os.getenv('API_KEY')
        if env_token:
            token = env_token
    
    if not token:
        click.echo("Error: No authentication token provided. Use --token or set DOCUDEVS_TOKEN environment variable.", err=True)
        ctx.exit(1)
    
    ctx.obj["client"] = DocuDevsClient(api_url=api_url, token=token)


# High-level convenience commands
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--prompt", default="", help="Extraction prompt")
@click.option("--schema", default="", help="JSON schema for extraction")
@click.option("--ocr", type=click.Choice(["DEFAULT", "NONE", "PREMIUM", "AUTO"]), default="DEFAULT", help="OCR type")
@click.option("--llm", type=click.Choice(["DEFAULT", "MINI", "HIGH"]), default="DEFAULT", help="LLM type")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.option("--wait/--no-wait", default=True, help="Wait for processing to complete")
@click.pass_context
@async_command
async def process(ctx, file: str, prompt: str, schema: str, ocr: str, llm: str, timeout: int, wait: bool):
    """Upload and process a document in one command."""
    from io import BytesIO
    import mimetypes
    
    file_path = Path(file)
    mime_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
    
    with open(file_path, "rb") as f:
        document_bytes = BytesIO(f.read())
    
    try:
        guid = await ctx.obj["client"].submit_and_process_document(
            document=document_bytes,
            document_mime_type=mime_type,
            prompt=prompt,
            schema=schema,
            ocr=ocr,
            llm=llm
        )
        click.echo(f"Document uploaded and queued for processing. GUID: {guid}")
        
        if wait:
            click.echo("Waiting for processing to complete...")
            result = await ctx.obj["client"].wait_until_ready(guid, timeout=timeout)
            if hasattr(result, '__dict__'):
                click.echo(json.dumps(result.__dict__, indent=2))
            else:
                click.echo(str(result))
        else:
            click.echo("Use 'status' and 'result' commands to check progress and get results.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--ocr", type=click.Choice(["DEFAULT", "NONE", "PREMIUM", "AUTO"]), default="DEFAULT", help="OCR type")
@click.option("--format", "ocr_format", type=click.Choice(["plain", "markdown"]), default="plain", help="OCR output format")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.option("--wait/--no-wait", default=True, help="Wait for processing to complete")
@click.pass_context
@async_command
async def ocr_only(ctx, file: str, ocr: str, ocr_format: str, timeout: int, wait: bool):
    """Upload and process document with OCR-only mode."""
    from io import BytesIO
    import mimetypes
    
    file_path = Path(file)
    mime_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
    
    with open(file_path, "rb") as f:
        document_bytes = BytesIO(f.read())
    
    try:
        guid = await ctx.obj["client"].submit_and_ocr_document(
            document=document_bytes,
            document_mime_type=mime_type,
            ocr=ocr,
            ocr_format=ocr_format
        )
        click.echo(f"Document uploaded and queued for OCR processing. GUID: {guid}")
        
        if wait:
            click.echo("Waiting for processing to complete...")
            result = await ctx.obj["client"].wait_until_ready(guid, timeout=timeout)
            if hasattr(result, '__dict__'):
                click.echo(json.dumps(result.__dict__, indent=2))
            else:
                click.echo(str(result))
        else:
            click.echo("Use 'status' and 'result' commands to check progress and get results.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command()
@click.argument("guid")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.pass_context
@async_command
async def wait(ctx, guid: str, timeout: int):
    """Wait for a job to complete and return the result."""
    try:
        result = await ctx.obj["client"].wait_until_ready(guid, timeout=timeout)
        if hasattr(result, '__dict__'):
            click.echo(json.dumps(result.__dict__, indent=2))
        else:
            click.echo(str(result))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


# Low-level commands
@cli.command()
@click.argument("uuid")
@click.pass_context
@async_command
async def result(ctx, uuid: str):
    """Get job result."""
    result = await ctx.obj["client"].result(uuid)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("guid")
@click.pass_context
@async_command
async def status(ctx, guid: str):
    """Get job status."""
    result = await ctx.obj["client"].status(guid)
    click.echo(json.dumps(result.body, indent=2))


# Configuration commands
@cli.command()
@click.pass_context
@async_command
async def list_configurations(ctx):
    """List all named configurations."""
    result = await ctx.obj["client"].list_configurations()
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.pass_context
@async_command
async def get_configuration(ctx, name: str):
    """Get a named configuration."""
    result = await ctx.obj["client"].get_configuration(name)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.argument("command_file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def save_configuration(ctx, name: str, command_file: str):
    """Save a named configuration from a JSON file."""
    with open(command_file) as f:
        command_data = json.load(f)
    body = UploadCommand.from_dict(command_data)
    result = await ctx.obj["client"].save_configuration(name, body)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.pass_context
@async_command
async def delete_configuration(ctx, name: str):
    """Delete a named configuration."""
    result = await ctx.obj["client"].delete_configuration(name)
    click.echo(json.dumps(result.body, indent=2))


# Template commands
@cli.command()
@click.pass_context
@async_command
async def list_templates(ctx):
    """List all templates."""
    result = await ctx.obj["client"].list_templates()
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.argument("request_file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def fill(ctx, name: str, request_file: str):
    """Fill a template with data from JSON file."""
    with open(request_file) as f:
        request_data = json.load(f)
    body = TemplateFillRequest.from_dict(request_data)
    result = await ctx.obj["client"].fill(name, body)
    click.echo(json.dumps(result.body, indent=2))


if __name__ == "__main__":
    cli()

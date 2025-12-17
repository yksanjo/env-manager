#!/usr/bin/env python3
"""CLI entry point for env-manager."""

import click
from pathlib import Path
from src.manager import (
    generate_env_file,
    validate_env_file,
    encrypt_env_file,
    decrypt_env_file,
)


@click.group()
def main():
    """Env Manager - Manage .env files with validation and encryption."""
    pass


@main.command()
@click.option('--template', '-t', default='.env.example', help='Template file path')
@click.option('--output', '-o', default='.env', help='Output file path')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def generate(template, output, interactive):
    """Generate .env file from template."""
    template_path = Path(template)
    output_path = Path(output)
    
    if not template_path.exists():
        click.echo(f"Error: Template file '{template}' not found.", err=True)
        return
    
    try:
        generate_env_file(template_path, output_path, interactive)
        click.echo(f"✅ Generated .env file: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.option('--file', '-f', default='.env', help='Environment file to validate')
@click.option('--template', '-t', default='.env.example', help='Template file for validation')
def validate(file, template):
    """Validate environment variables."""
    env_path = Path(file)
    template_path = Path(template)
    
    if not env_path.exists():
        click.echo(f"Error: Environment file '{file}' not found.", err=True)
        return
    
    try:
        errors = validate_env_file(env_path, template_path)
        if errors:
            click.echo("❌ Validation failed:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            exit(1)
        else:
            click.echo("✅ All environment variables are valid!")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--file', '-f', default='.env', help='Environment file to encrypt')
@click.option('--key', '-k', required=True, help='Encryption key')
def encrypt(file, key):
    """Encrypt sensitive values in .env file."""
    env_path = Path(file)
    
    if not env_path.exists():
        click.echo(f"Error: Environment file '{file}' not found.", err=True)
        return
    
    try:
        encrypt_env_file(env_path, key)
        click.echo(f"✅ Encrypted values in {file}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.option('--file', '-f', default='.env', help='Environment file to decrypt')
@click.option('--key', '-k', required=True, help='Decryption key')
def decrypt(file, key):
    """Decrypt values in .env file."""
    env_path = Path(file)
    
    if not env_path.exists():
        click.echo(f"Error: Environment file '{file}' not found.", err=True)
        return
    
    try:
        decrypt_env_file(env_path, key)
        click.echo(f"✅ Decrypted values in {file}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    main()



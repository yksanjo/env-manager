"""Environment file management functions."""

import re
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dotenv import dotenv_values
import validators
from cryptography.fernet import Fernet
import base64
import hashlib


def parse_template_line(line: str) -> Optional[Tuple[str, str, Dict[str, bool]]]:
    """Parse a line from .env.example template.
    
    Returns: (key, default_value, metadata) or None if not a variable line
    """
    line = line.strip()
    
    # Skip comments and empty lines
    if not line or line.startswith('#'):
        return None
    
    # Parse: KEY=value  # type, required, encrypted
    match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*?)(?:\s*#\s*(.*))?$', line)
    if not match:
        return None
    
    key = match.group(1)
    default_value = match.group(2).strip()
    comment = match.group(3) or ''
    
    # Parse metadata from comment
    metadata = {
        'required': 'required' in comment.lower(),
        'optional': 'optional' in comment.lower(),
        'encrypted': 'encrypted' in comment.lower(),
    }
    
    # Detect type from comment
    type_hint = None
    for t in ['string', 'int', 'bool', 'url', 'email']:
        if t in comment.lower():
            type_hint = t
            break
    
    metadata['type'] = type_hint or 'string'
    
    # Default to required if not specified
    if not metadata['optional']:
        metadata['required'] = True
    
    return (key, default_value, metadata)


def generate_env_file(template_path: Path, output_path: Path, interactive: bool = False):
    """Generate .env file from template."""
    template_lines = template_path.read_text().split('\n')
    env_vars = {}
    
    for line in template_lines:
        parsed = parse_template_line(line)
        if not parsed:
            continue
        
        key, default_value, metadata = parsed
        
        # Check if already exists in environment
        if key in os.environ:
            value = os.environ[key]
        elif interactive:
            prompt = f"{key}"
            if metadata['type'] != 'string':
                prompt += f" ({metadata['type']})"
            if not metadata['required']:
                prompt += " [optional]"
            prompt += f" [{default_value}]: "
            
            value = input(prompt).strip()
            if not value:
                value = default_value
        else:
            value = default_value
        
        env_vars[key] = value
    
    # Write .env file
    lines = []
    for key, value in env_vars.items():
        lines.append(f"{key}={value}")
    
    output_path.write_text('\n'.join(lines) + '\n')


def validate_env_file(env_path: Path, template_path: Optional[Path] = None) -> List[str]:
    """Validate environment file against template."""
    errors = []
    env_vars = dotenv_values(env_path)
    
    # If template provided, validate against it
    if template_path and template_path.exists():
        template_lines = template_path.read_text().split('\n')
        required_vars = {}
        
        for line in template_lines:
            parsed = parse_template_line(line)
            if not parsed:
                continue
            
            key, default_value, metadata = parsed
            if metadata['required']:
                required_vars[key] = metadata
        
        # Check required variables
        for key, metadata in required_vars.items():
            if key not in env_vars or not env_vars[key]:
                errors.append(f"Required variable '{key}' is missing")
                continue
            
            value = env_vars[key]
            
            # Type validation
            type_hint = metadata.get('type', 'string')
            if type_hint == 'int':
                try:
                    int(value)
                except ValueError:
                    errors.append(f"Variable '{key}' must be an integer")
            elif type_hint == 'bool':
                if value.lower() not in ['true', 'false', 'yes', 'no', '1', '0']:
                    errors.append(f"Variable '{key}' must be a boolean")
            elif type_hint == 'url':
                if not validators.url(value):
                    errors.append(f"Variable '{key}' must be a valid URL")
            elif type_hint == 'email':
                if not validators.email(value):
                    errors.append(f"Variable '{key}' must be a valid email")
    
    return errors


def get_encryption_key(password: str) -> bytes:
    """Generate encryption key from password."""
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_env_file(env_path: Path, key: str):
    """Encrypt sensitive values in .env file."""
    key_bytes = get_encryption_key(key)
    fernet = Fernet(key_bytes)
    
    lines = env_path.read_text().split('\n')
    encrypted_lines = []
    
    for line in lines:
        if '=' not in line or line.strip().startswith('#'):
            encrypted_lines.append(line)
            continue
        
        key_part, value_part = line.split('=', 1)
        value_part = value_part.strip()
        
        # Check if this should be encrypted (would need template to know)
        # For now, encrypt if value doesn't look like it's already encrypted
        if not value_part.startswith('gAAAAAB'):  # Fernet encrypted prefix
            try:
                encrypted_value = fernet.encrypt(value_part.encode()).decode()
                encrypted_lines.append(f"{key_part}={encrypted_value}")
            except Exception:
                encrypted_lines.append(line)
        else:
            encrypted_lines.append(line)
    
    env_path.write_text('\n'.join(encrypted_lines) + '\n')


def decrypt_env_file(env_path: Path, key: str):
    """Decrypt values in .env file."""
    key_bytes = get_encryption_key(key)
    fernet = Fernet(key_bytes)
    
    lines = env_path.read_text().split('\n')
    decrypted_lines = []
    
    for line in lines:
        if '=' not in line or line.strip().startswith('#'):
            decrypted_lines.append(line)
            continue
        
        key_part, value_part = line.split('=', 1)
        value_part = value_part.strip()
        
        # Try to decrypt if it looks encrypted
        if value_part.startswith('gAAAAAB'):  # Fernet encrypted prefix
            try:
                decrypted_value = fernet.decrypt(value_part.encode()).decode()
                decrypted_lines.append(f"{key_part}={decrypted_value}")
            except Exception:
                decrypted_lines.append(line)
        else:
            decrypted_lines.append(line)
    
    env_path.write_text('\n'.join(decrypted_lines) + '\n')



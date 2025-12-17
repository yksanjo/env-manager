"""Tests for env manager."""

import pytest
import tempfile
from pathlib import Path
from src.manager import (
    parse_template_line,
    validate_env_file,
    generate_env_file,
)


def test_parse_template_line():
    """Test parsing template lines."""
    # Simple line
    result = parse_template_line("DATABASE_URL=postgresql://localhost/db")
    assert result is not None
    key, value, metadata = result
    assert key == "DATABASE_URL"
    assert value == "postgresql://localhost/db"
    
    # With type annotation
    result = parse_template_line("PORT=8000  # int, required")
    assert result is not None
    key, value, metadata = result
    assert metadata['type'] == 'int'
    assert metadata['required'] is True
    
    # Optional
    result = parse_template_line("OPTIONAL_VAR=default  # optional")
    assert result is not None
    key, value, metadata = result
    assert metadata['optional'] is True


def test_generate_env_file():
    """Test generating .env file from template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / ".env.example"
        output_path = Path(tmpdir) / ".env"
        
        template_content = """# Database
DATABASE_URL=postgresql://localhost/db  # url, required
PORT=8000  # int, required

# Optional
DEBUG=false  # bool, optional
"""
        template_path.write_text(template_content)
        
        generate_env_file(template_path, output_path, interactive=False)
        
        assert output_path.exists()
        content = output_path.read_text()
        assert "DATABASE_URL=" in content
        assert "PORT=" in content


def test_validate_env_file():
    """Test validating .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"
        template_path = Path(tmpdir) / ".env.example"
        
        # Create template
        template_content = """DATABASE_URL=postgresql://localhost/db  # url, required
PORT=8000  # int, required
"""
        template_path.write_text(template_content)
        
        # Valid .env
        env_content = """DATABASE_URL=postgresql://localhost/mydb
PORT=5432
"""
        env_path.write_text(env_content)
        
        errors = validate_env_file(env_path, template_path)
        assert len(errors) == 0
        
        # Missing required variable
        env_content = """PORT=5432
"""
        env_path.write_text(env_content)
        
        errors = validate_env_file(env_path, template_path)
        assert len(errors) > 0
        assert any("DATABASE_URL" in error for error in errors)
        
        # Invalid type
        env_content = """DATABASE_URL=not-a-url
PORT=5432
"""
        env_path.write_text(env_content)
        
        errors = validate_env_file(env_path, template_path)
        assert len(errors) > 0



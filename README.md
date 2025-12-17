# env-manager

Manage .env files across projects with validation, type checking, and secure encryption. Never miss a required environment variable again!

## Features

- 🔧 Generate .env files from templates (.env.example)
- ✅ Validate required environment variables
- 🔒 Encrypt/decrypt sensitive values
- 📝 Type checking (string, int, bool, url, email)
- 🚀 Pre-start validation to catch errors early
- 🔄 Sync .env files across team members

## Installation

```bash
pip install -e .
```

Or install globally:
```bash
pip install .
```

## Usage

### Generate .env from Template

```bash
env-manager generate --template .env.example
```

### Validate Environment Variables

```bash
env-manager validate
```

### Encrypt Sensitive Values

```bash
env-manager encrypt --key my-secret-key
```

### Decrypt Values

```bash
env-manager decrypt --key my-secret-key
```

## Template Format

Create a `.env.example` file with type annotations:

```bash
# Database
DATABASE_URL=postgresql://localhost/dbname  # url, required
DB_PORT=5432  # int, required

# API Keys
API_KEY=your-api-key-here  # string, required
SECRET_KEY=your-secret-key  # string, required, encrypted

# Features
DEBUG=false  # bool
ENABLE_FEATURE_X=true  # bool

# Optional
OPTIONAL_VAR=default-value  # string, optional
```

## Type Annotations

Supported types:
- `string` - String value (default)
- `int` - Integer
- `bool` - Boolean (true/false, yes/no, 1/0)
- `url` - Valid URL
- `email` - Valid email address
- `required` - Variable must be set
- `optional` - Variable can be omitted
- `encrypted` - Value should be encrypted

## Examples

### Generate .env File

```bash
# Interactive mode
env-manager generate

# From specific template
env-manager generate --template .env.example --output .env
```

### Validate Before Starting App

Add to your app startup:

```python
import subprocess
subprocess.run(["env-manager", "validate"], check=True)
```

Or use as a pre-start hook:

```bash
env-manager validate && python app.py
```

### Encrypt Sensitive Values

```bash
env-manager encrypt --file .env --key my-secret-key
```

This will encrypt values marked with `encrypted` in the template.

## Integration

### Pre-start Validation

Add to your startup script:

```bash
#!/bin/bash
env-manager validate || exit 1
python app.py
```

### CI/CD

Validate environment in CI:

```yaml
- name: Validate environment
  run: env-manager validate
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.



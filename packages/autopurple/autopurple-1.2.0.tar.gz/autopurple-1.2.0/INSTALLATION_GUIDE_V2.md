# 🟣 AutoPurple v1.1.0 - Complete Installation Guide

## 🚀 New in v1.1.0

**AutoPurple v1.1.0 fixes all the major issues from v1.0.0:**

✅ **Interactive Setup Wizard** - `autopurple setup`  
✅ **Automatic MCP Server Installation** - No manual configuration needed  
✅ **Improved Claude Integration** - Better error handling and JSON parsing  
✅ **Dependency Management** - UV and all tools installed automatically  
✅ **Configuration Management** - Proper config file creation and validation

## 📦 Quick Installation

```bash
# Install the latest version
pip install autopurple==1.1.0

# Run the interactive setup wizard (NEW!)
autopurple setup

# Test your installation
autopurple health

# Run a security scan
autopurple run --region us-east-1
```

## 🔧 Interactive Setup Process

AutoPurple v1.1.0 includes a comprehensive setup wizard:

```bash
autopurple setup
```

This will:

1. **Install UV package manager** automatically
2. **Install MCP servers** (CCAPI, AWS Docs) via uvx
3. **Configure Claude API key** with validation
4. **Set up AWS credentials** guidance
5. **Create configuration file** at `~/.autopurple/config.yaml`
6. **Test the setup** to ensure everything works

## 🧠 Claude API Configuration

During setup, you'll be prompted for your Claude API key:

1. Visit https://console.anthropic.com/
2. Create an account and generate an API key
3. The key starts with `sk-ant-api...`
4. AutoPurple will validate the key works

## ☁️ AWS Configuration

AutoPurple supports multiple AWS credential methods:

### Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### AWS CLI Configuration
```bash
aws configure
```

### IAM Roles (for EC2/ECS/Lambda)
No configuration needed - AutoPurple will use the instance role.

## 🔧 Manual Configuration

If you prefer manual setup, create `~/.autopurple/config.yaml`:

```yaml
version: "1.0"

claude:
  api_key: "sk-ant-api-your-key-here"
  model: "claude-3-5-haiku-20241022"
  max_tokens: 4000

aws:
  profile: "default"
  region: "us-east-1"

mcp:
  ccapi:
    command: ["uvx", "awslabs.ccapi-mcp-server@latest"]
    enabled: true
  docs:
    command: ["uvx", "awslabs.aws-documentation-mcp-server@latest"]
    enabled: true

pipeline:
  max_concurrent_findings: 10
  dry_run_default: true

logging:
  level: "INFO"
  format: "json"
```

## ✅ Verification

Test your installation:

```bash
# Check all components
autopurple health

# Expected output:
# ✅ Database: OK
# ✅ ScoutSuite: OK  
# ✅ Pacu: OK
# ✅ CCAPI MCP: OK
# ✅ Docs MCP: OK
# ✅ Claude API: OK
```

## 🎯 Usage Examples

### Basic Security Scan
```bash
autopurple run --region us-east-1
```

### Production Scan with Remediation
```bash
autopurple run --region us-east-1 --no-dry-run --max-findings 20
```

### Discovery Only
```bash
autopurple discover --region us-east-1
```

### Validation Only
```bash
autopurple validate --finding-id sg-1234567890
```

## 🔧 Troubleshooting

### MCP Servers Not Starting

```bash
# Reinstall MCP servers
uvx install awslabs.ccapi-mcp-server@latest
uvx install awslabs.aws-documentation-mcp-server@latest

# Test manually
uvx run awslabs.ccapi-mcp-server@latest --help
```

### Claude API Issues

```bash
# Test your API key
python -c "
import anthropic
client = anthropic.Anthropic(api_key='your-key')
response = client.messages.create(
    model='claude-3-5-haiku-20241022',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print('API key works!')
"
```

### AWS Credential Issues

```bash
# Test AWS access
aws sts get-caller-identity

# Or check environment
echo $AWS_ACCESS_KEY_ID
```

## 🆘 Support

If you encounter issues:

1. **Run the setup wizard again**: `autopurple setup`
2. **Check health status**: `autopurple health --verbose`
3. **View logs**: Check `~/.autopurple/logs/`
4. **Reset configuration**: Delete `~/.autopurple/` and re-run setup

## 🔄 Upgrading from v1.0.0

```bash
# Uninstall old version
pip uninstall autopurple

# Install new version
pip install autopurple==1.1.0

# Re-run setup
autopurple setup
```

## 🎉 What's Fixed

**v1.1.0 addresses all the issues from v1.0.0:**

- ❌ ~~Claude responses not parsing~~ → ✅ **Fixed JSON parsing with fallbacks**
- ❌ ~~MCP servers not running~~ → ✅ **Automatic installation and management**
- ❌ ~~Complex manual setup~~ → ✅ **Interactive setup wizard**
- ❌ ~~Dependency issues~~ → ✅ **Automatic dependency management**
- ❌ ~~No configuration guidance~~ → ✅ **Step-by-step setup process**

**AutoPurple v1.1.0 is now truly production-ready with full automation!** 🚀

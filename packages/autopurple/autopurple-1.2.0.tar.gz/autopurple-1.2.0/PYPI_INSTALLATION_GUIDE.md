# 📦 AutoPurple PyPI Installation Guide

## 🚀 Quick Start

AutoPurple is now available on PyPI! Install it with a single command:

```bash
# Basic installation (without validation)
pip install autopurple

# Full installation with validation capabilities
pip install autopurple[validation]

# Complete installation with all features
pip install autopurple[validation,ai,aws,dev]
```

## 📋 Installation Options

### Basic Installation
```bash
pip install autopurple
```
**Includes:** Core functionality, ScoutSuite discovery, Claude AI integration, AWS MCP servers

### With Validation Support
```bash
pip install autopurple[validation]
```
**Adds:** Pacu for vulnerability validation

### Development Installation
```bash
pip install autopurple[dev]
```
**Adds:** Testing, linting, and development tools

### Complete Installation
```bash
pip install autopurple[all]
```
**Includes:** Everything - validation, AI, AWS tools, and development dependencies

## 🎯 Quick Usage

Once installed, use the `autopurple` command:

```bash
# Check installation
autopurple --help

# Health check
autopurple health

# Run full security scan
export CLAUDE_API_KEY="sk-ant-api-your-key-here"
autopurple run --region us-east-1

# Discovery only
autopurple discover --region us-east-1

# Check status
autopurple status
```

## 📚 Full CLI Documentation

### Global Options
- `--help`: Show help message
- `--verbose`: Enable verbose output
- `--config`: Path to config file

### Commands

#### `autopurple run`
Run the complete security automation pipeline
```bash
autopurple run --region us-east-1 [OPTIONS]

Options:
  --region TEXT               AWS region to scan
  --profile TEXT              AWS profile to use
  --claude-api-key TEXT       Claude API key (or set CLAUDE_API_KEY env var)
  --dry-run / --no-dry-run    Dry run mode (default: true)
  --max-findings INTEGER      Maximum findings to process
  --exclude-services TEXT     Services to exclude
  --include-services TEXT     Services to include only
  --output-format TEXT        Output format (json, table, csv)
  --save-report TEXT          Save report to file
```

#### `autopurple discover`
Run ScoutSuite discovery only
```bash
autopurple discover --region us-east-1 [OPTIONS]

Options:
  --region TEXT          AWS region to scan
  --profile TEXT         AWS profile to use
  --services TEXT        Comma-separated services to scan
  --skip-dashboard       Skip HTML dashboard generation
  --output-dir TEXT      Output directory for results
```

#### `autopurple validate`
Run Pacu validation on findings
```bash
autopurple validate [OPTIONS]

Options:
  --finding-id TEXT      Specific finding ID to validate
  --max-findings INTEGER Maximum findings to validate
  --timeout INTEGER      Validation timeout in seconds
```

#### `autopurple status`
Show status of recent runs
```bash
autopurple status [OPTIONS]

Options:
  --limit INTEGER        Number of recent runs to show
  --format TEXT          Output format (table, json)
  --filter TEXT          Filter by status (running, completed, failed)
```

#### `autopurple health`
Check health of all components
```bash
autopurple health [OPTIONS]

Options:
  --verbose              Show detailed health information
  --fix                  Attempt to fix issues automatically
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required for AI features
export CLAUDE_API_KEY="sk-ant-api-your-key-here"

# AWS Configuration
export AWS_PROFILE="your-profile"
export AWS_REGION="us-east-1"

# Optional: AutoPurple settings
export AUTOPURPLE_DB_PATH="~/.autopurple/db.sqlite"
export LOG_LEVEL="INFO"
export MAX_CONCURRENT_FINDINGS="10"
```

### Configuration File
Create `~/.autopurple/config.yaml`:
```yaml
aws:
  profile: "your-profile"
  region: "us-east-1"

ai:
  claude_api_key: "sk-ant-api-your-key-here"
  model: "claude-3-5-haiku-20241022"

pipeline:
  max_concurrent_findings: 10
  max_concurrent_validations: 5
  timeout_scoutsuite: 3600
  timeout_pacu: 1800

logging:
  level: "INFO"
  format: "json"
```

## 🔧 Dependencies Resolved

AutoPurple handles complex dependency conflicts automatically:

### SQLAlchemy Compatibility
- Core: Uses SQLAlchemy 1.4.x for compatibility with ScoutSuite
- Pacu: Made optional to avoid conflicts
- Install with `[validation]` extra for full validation support

### Optional Dependencies
- **Pacu** (validation): `pip install autopurple[validation]`
- **OpenAI** (alternative AI): `pip install autopurple[ai]`
- **AWS CDK** (infrastructure): `pip install autopurple[aws]`
- **Development tools**: `pip install autopurple[dev]`

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Fix: Ensure clean installation
pip uninstall autopurple
pip install --no-cache-dir autopurple
```

#### 2. Claude API Errors
```bash
# Check API key
echo $CLAUDE_API_KEY

# Test API key
python -c "
import anthropic
client = anthropic.Anthropic(api_key='your-key')
print('API key works!')
"
```

#### 3. AWS Credentials
```bash
# Check AWS configuration
aws configure list  # If AWS CLI installed
# Or check environment
echo $AWS_PROFILE $AWS_REGION
```

#### 4. Pacu Not Found
```bash
# Install validation support
pip install autopurple[validation]

# Or install Pacu separately
pip install pacu
```

#### 5. ScoutSuite Issues
```bash
# ScoutSuite is included automatically
# Check installation
python -m ScoutSuite --help
```

### Performance Issues
```bash
# Reduce concurrency
export MAX_CONCURRENT_FINDINGS=5

# Increase timeouts
export SCOUTSUITE_TIMEOUT=7200
export PACU_TIMEOUT=3600
```

### Permission Issues
```bash
# Ensure proper AWS permissions
autopurple health --verbose

# Check MCP server requirements
# AutoPurple requires network access for MCP servers
```

## 🏗️ Development Installation

For contributing or development:

```bash
# Clone repository
git clone https://github.com/autopurple/autopurple.git
cd autopurple

# Install in development mode
pip install -e .[all]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📝 Usage Examples

### Basic Security Scan
```bash
export CLAUDE_API_KEY="sk-ant-api-your-key"
autopurple run --region us-east-1 --no-dry-run
```

### Targeted Scan
```bash
autopurple run \
  --region us-east-1 \
  --include-services ec2,iam,s3 \
  --max-findings 50 \
  --save-report security-report.json
```

### Discovery Only
```bash
autopurple discover \
  --region us-east-1 \
  --services ec2,vpc \
  --output-dir ./scout-results/
```

### Validation Only
```bash
autopurple validate \
  --finding-id sg-052e9598dc193e67f \
  --timeout 600
```

### Programmatic Usage
```python
from autopurple import AutoPurplePipeline

# Initialize pipeline
pipeline = AutoPurplePipeline()

# Run full scan
results = await pipeline.run(
    region='us-east-1',
    max_findings=100,
    dry_run=False
)

# Access results
print(f"Found {len(results.findings)} issues")
for finding in results.findings:
    print(f"- {finding.title}: {finding.level}")
```

## 🎯 Success Indicators

After installation, you should see:

```bash
$ autopurple --help
✅ CLI loads successfully

$ autopurple health
✅ Database: OK
✅ ScoutSuite: OK
⚠️  Pacu: Install with [validation] extra
⚠️  Claude API: Set CLAUDE_API_KEY

$ autopurple run --region us-east-1
✅ Pipeline executes successfully
```

## 🆘 Getting Help

- **Documentation**: [autopurple.readthedocs.io](https://autopurple.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/autopurple/autopurple/issues)
- **Community**: [GitHub Discussions](https://github.com/autopurple/autopurple/discussions)

## 📊 Package Stats

- **PyPI**: https://pypi.org/project/autopurple/
- **Downloads**: ![PyPI - Downloads](https://img.shields.io/pypi/dm/autopurple)
- **Version**: ![PyPI](https://img.shields.io/pypi/v/autopurple)
- **Python**: ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/autopurple)

---

**🎉 You're now ready to automate AWS security with AutoPurple!**

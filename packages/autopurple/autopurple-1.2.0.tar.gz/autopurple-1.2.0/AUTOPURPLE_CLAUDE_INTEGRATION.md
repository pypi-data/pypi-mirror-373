# AutoPurple Claude Integration Guide

## Overview

AutoPurple is now fully integrated with Claude Haiku API for intelligent AWS security analysis and remediation planning. This document shows how to configure and run the complete end-to-end pipeline.

## 🧠 Claude Integration Features

### System Prompts for Claude Haiku

AutoPurple uses comprehensive system prompts that transform Claude into an expert AWS security analyst:

**Core Capabilities:**
- AWS security findings analysis from ScoutSuite scans
- Exploitability assessment and attack vector identification  
- Risk-aware remediation planning with operational impact consideration
- Precise AWS MCP server call generation for automated fixes
- Business impact and compliance-aware prioritization

**Security Analysis Principles:**
- Risk-based assessment focusing on actual exploitability
- Defense in depth strategies
- Blast radius analysis for both vulnerabilities and fixes
- Operational impact balancing with business continuity
- Compliance framework alignment

### Enhanced Analysis Prompts

The system includes sophisticated prompts for:

1. **Findings Analysis**: Clustering, deduplication, and prioritization
2. **Remediation Planning**: Production-ready fix strategies with rollback plans
3. **Risk Assessment**: Business impact and operational safety evaluation
4. **MCP Integration**: Precise AWS resource modification calls

## 🔧 Configuration

### 1. Claude API Key Setup

```bash
# Add to your .env file
echo "CLAUDE_API_KEY=your-actual-claude-api-key-here" >> .env

# Or export as environment variable
export CLAUDE_API_KEY="your-actual-claude-api-key-here"
```

### 2. Required Dependencies

```bash
# Install Anthropic SDK
pip install anthropic

# Verify installation
python3 -c "import anthropic; print('✅ Anthropic SDK installed')"
```

### 3. AWS MCP Server Integration

The system now properly follows the CCAPI MCP server mandatory workflow:

1. **check_environment_variables()** - ALWAYS FIRST
2. **get_aws_session_info(env_check_result)** - ALWAYS SECOND  
3. **Resource operations** - Only after session established

## 🚀 Running the Full Pipeline

### Method 1: Using the Test Script

```bash
# Run with Claude integration
python3 test_full_pipeline.py --claude-api-key "your-key" --aws-region us-east-1

# With specific AWS profile
python3 test_full_pipeline.py --claude-api-key "your-key" --aws-profile production --aws-region us-west-2

# Dry run mode (safe testing)
python3 test_full_pipeline.py --claude-api-key "your-key" --dry-run
```

### Method 2: Using the CLI

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run with Claude-powered analysis
python3 -m autopurple.cli.main run \
  --region us-east-1 \
  --max-findings 10 \
  --no-dry-run \
  --verbose
```

## 📊 Pipeline Workflow

### Phase 1: Discovery
- **ScoutSuite** scans AWS account for security findings
- Generates comprehensive security assessment
- Focuses on actual security group: `sg-052e9598dc193e67f`

### Phase 2: Claude Analysis  
- **Claude Haiku** analyzes findings with expert system prompts
- Performs clustering, deduplication, and risk prioritization
- Generates exploitability assessments and attack scenarios
- Creates remediation roadmap with business impact consideration

### Phase 3: Validation
- **Pacu** validates findings for actual exploitability
- Confirms attack vectors and potential impact
- Updates finding status based on validation results

### Phase 4: Remediation Planning
- **Claude** creates production-ready remediation plans
- Generates precise AWS MCP server calls
- Includes rollback strategies and success criteria
- Considers operational impact and compliance requirements

### Phase 5: Execution
- **AWS CCAPI MCP Server** executes remediation
- Follows mandatory CCAPI workflow for safety
- Applies security group rule modifications
- Logs all actions for audit trail

### Phase 6: Verification
- Post-remediation validation
- Confirms security improvements
- Updates finding status to "remediated"

## 🔒 Security Group Remediation Example

For the target security group `sg-052e9598dc193e67f`, the system will:

1. **Identify** unrestricted 0.0.0.0/0 access (critical vulnerability)
2. **Analyze** attack vectors and blast radius with Claude
3. **Validate** exploitability with Pacu testing
4. **Plan** remediation to restrict access to private networks only
5. **Execute** via CCAPI MCP server:
   - Revoke all 0.0.0.0/0 ingress rules
   - Add restricted rules for SSH (22), HTTP (80), HTTPS (443)
   - Limit access to 10.0.0.0/8 private network range
6. **Verify** successful remediation

## 📈 Enhanced Output

With Claude integration, you'll see:

```
Pipeline Results
┏━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric         ┃ Value ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Findings │ 1     │
│ Validated      │ 1     │ 
│ Exploitable    │ 1     │
│ Remediated     │ 1     │ ✅ FIXED!
│ Duration       │ 45.2s │
└────────────────┴───────┘

Findings Details:
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Service ┃ Title                          ┃ Severity ┃ Status     ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ec2     │ Security Group Opens All Ports │ critical │ remediated │ 
└─────────┴────────────────────────────────┴──────────┴────────────┘
```

## 🎯 Key Improvements

1. **Expert Analysis**: Claude provides AWS security expert-level analysis
2. **Production Ready**: Comprehensive remediation plans with rollback strategies
3. **Compliance Aware**: Considers SOC2, PCI, GDPR, and other frameworks
4. **Operational Safety**: Includes pre-checks and post-validation
5. **Audit Trail**: Full logging of all actions and decisions
6. **Risk-Based**: Prioritizes by actual exploitability, not just policy violations

## 🔍 System Prompts Summary

The Claude system prompts include:

- **AWS Expertise**: Deep knowledge across all AWS services
- **Security Principles**: Risk-based assessment, defense in depth
- **Remediation Planning**: Step-by-step fixes with safety considerations  
- **MCP Integration**: Precise resource modification commands
- **Business Impact**: Operational and compliance considerations
- **JSON Structured Output**: Consistent, parseable responses

## 🎉 Results

AutoPurple now provides:
- **Intelligent Analysis**: Claude-powered finding assessment
- **Production-Ready Plans**: Comprehensive remediation strategies
- **Automated Execution**: MCP-based resource modifications
- **Complete Audit Trail**: Full logging and verification
- **Risk-Aware Decisions**: Business impact and operational safety

The system successfully transforms raw ScoutSuite findings into actionable, intelligent remediation with Claude's expert analysis and AWS MCP servers' automation capabilities.

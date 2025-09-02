# Changelog

All notable changes to AutoPurple will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-01

### Added
- 🎉 **Initial release of AutoPurple**
- 🧠 **Claude Haiku API integration** with comprehensive system prompts
- 🔍 **ScoutSuite integration** for AWS security discovery
- 🛡️ **Pacu integration** for vulnerability validation
- 🔧 **AWS MCP server integration** for automated remediation
- 📊 **Rich CLI interface** with beautiful progress indicators
- 🎯 **End-to-end security automation pipeline**

### Core Features
- **Discovery**: ScoutSuite-based AWS security scanning
- **Analysis**: Claude-powered intelligent finding assessment
- **Validation**: Pacu-based exploitability confirmation  
- **Planning**: Production-ready remediation strategies
- **Execution**: Automated fixes via AWS CCAPI MCP server
- **Verification**: Post-remediation validation

### Security Focus
- **Risk-based prioritization**: Focus on actual exploitability
- **Business impact assessment**: Operational and compliance considerations
- **Defense in depth**: Comprehensive security strategies
- **Audit trail**: Complete logging and verification
- **Rollback capabilities**: Safe reversion for emergency scenarios

### Command Line Interface
- `autopurple run` - Execute full security automation pipeline
- `autopurple discover` - Run ScoutSuite discovery only
- `autopurple validate` - Run Pacu validation on findings
- `autopurple status` - Show pipeline execution status
- `autopurple health` - Check system component health

### AWS Services Supported
- **EC2 Security Groups**: Unrestricted access detection and remediation
- **IAM Policies**: Overpermissive access analysis
- **S3 Buckets**: Public access and policy validation
- **Extensible framework**: Ready for additional AWS services

### AI Integration
- **Claude Haiku system prompts**: Expert AWS security analyst persona
- **Intelligent analysis**: Risk assessment and attack vector identification
- **Production planning**: Comprehensive remediation with safety checks
- **Structured output**: JSON-based responses for automation

### Dependencies
- Python 3.11+
- ScoutSuite 5.14.0+
- Pacu 1.6.1+
- Anthropic Claude API
- AWS MCP servers
- Rich CLI framework

### Configuration
- Environment-based configuration via `.env` files
- AWS profile and region support
- Configurable concurrency limits
- Timeout and retry policies
- Dry-run mode for safe testing

### Documentation
- Complete installation guide
- Claude API integration documentation
- AWS MCP server setup instructions
- Command-line usage examples
- System architecture overview

---

## [Unreleased]

### Planned Features
- Support for additional AWS services (RDS, Lambda, KMS)
- Integration with AWS Config and CloudTrail
- Custom rule development framework
- Slack/Teams notifications
- Scheduled scanning capabilities
- Multi-account support
- Dashboard and reporting interface

---

## Contributing

See [CONTRIBUTING.md] for guidelines on how to contribute to AutoPurple.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

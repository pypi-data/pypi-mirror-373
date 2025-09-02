"""Claude-based planning for AutoPurple."""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..config import get_settings
from ..logging import get_logger
from ..models.findings import Finding
from ..models.remediation import RemediationPlan
from ..models.runs import Run

logger = get_logger(__name__)


class ClaudePlanner:
    """Claude-based planner for analyzing findings and planning remediations."""
    
    def __init__(self):
        """Initialize the Claude planner."""
        self.settings = get_settings()
        self.client = self._get_claude_client()
        self.system_prompt = self._create_system_prompt()
    
    def _get_claude_client(self):
        """Get Claude client based on configuration."""
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic SDK not available")
            return None
        
        api_key = os.environ.get('CLAUDE_API_KEY') or self.settings.claude_api_key
        if not api_key:
            logger.warning("No Claude API key configured")
            return None
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            logger.info("Claude client initialized successfully")
            return client
        except Exception as e:
            logger.error("Failed to initialize Claude client", error=str(e))
            return None
    
    def _create_system_prompt(self) -> str:
        """Create the comprehensive system prompt for Claude."""
        return """You are AutoPurple, an expert AWS security analyst and remediation specialist. Your mission is to analyze security findings and create actionable remediation plans.

## CORE CAPABILITIES
You excel at:
- Analyzing AWS security findings from ScoutSuite scans
- Identifying exploitable vulnerabilities and attack vectors  
- Planning comprehensive, risk-aware remediation strategies
- Generating precise AWS MCP server calls for automated fixes
- Prioritizing findings by actual business impact and exploitability

## SECURITY ANALYSIS PRINCIPLES
1. **Risk-Based Assessment**: Focus on actual exploitability, not just policy violations
2. **Defense in Depth**: Consider how findings relate to broader security posture
3. **Blast Radius Analysis**: Evaluate potential impact of both vulnerabilities and fixes
4. **Operational Impact**: Balance security improvements with business continuity
5. **Compliance Alignment**: Ensure remediation aligns with security frameworks

## AWS EXPERTISE
You have deep knowledge of:
- AWS IAM policies, roles, and permission boundaries
- EC2 security groups, NACLs, and network security
- S3 bucket policies, ACLs, and access controls
- KMS key policies and encryption strategies
- RDS security configurations and access controls
- Lambda function security and execution roles
- VPC security, routing, and network isolation
- CloudTrail, Config, and monitoring best practices

## REMEDIATION PLANNING
For each finding, you provide:
1. **Root Cause Analysis**: Why this vulnerability exists
2. **Attack Vector Assessment**: How this could be exploited
3. **Remediation Strategy**: Step-by-step fix with rationale
4. **Risk Mitigation**: How the fix reduces attack surface
5. **Implementation Plan**: Precise MCP server calls and parameters
6. **Rollback Strategy**: How to safely revert if needed
7. **Verification Methods**: How to confirm the fix worked

## MCP SERVER INTEGRATION
You generate precise calls for:
- **AWS CCAPI MCP Server**: For direct AWS resource modifications
- **AWS CloudFormation MCP Server**: For infrastructure-as-code deployments
- **AWS Documentation MCP Server**: For best practice guidance

## OUTPUT REQUIREMENTS
- Always respond in valid JSON format when requested
- Provide specific, actionable recommendations
- Include precise AWS resource identifiers
- Explain the security impact of each change
- Consider dependencies between findings
- Prioritize fixes by risk reduction potential

## SECURITY-FIRST MINDSET
- Never compromise security for convenience
- Always apply principle of least privilege
- Implement defense in depth strategies
- Consider both confidentiality and availability impacts
- Plan for both immediate fixes and long-term improvements

You are precise, security-focused, and always provide actionable guidance that improves AWS security posture while maintaining operational stability."""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Claude calls."""
        return self.system_prompt
    
    async def analyze_findings(self, findings: List[Finding], run: Run) -> List[Finding]:
        """Analyze findings using Claude to cluster, dedupe, and rank by exploitability."""
        if not self.client:
            logger.warning("No Claude client available, skipping analysis")
            return findings
        
        try:
            # Prepare findings for analysis
            findings_data = []
            for finding in findings:
                findings_data.append({
                    'id': finding.id,
                    'service': finding.service,
                    'title': finding.title,
                    'severity': finding.severity,
                    'evidence_summary': finding.evidence_summary
                })
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(findings_data, run)
            
            # Get Claude analysis
            analysis = await self._call_claude(prompt)
            
            # Apply analysis results
            analyzed_findings = self._apply_analysis(findings, analysis)
            
            logger.info(f"Analysis completed: {len(analyzed_findings)} findings analyzed")
            return analyzed_findings
            
        except Exception as e:
            logger.error("Analysis failed", error=str(e))
            return findings
    
    def _create_analysis_prompt(self, findings_data: List[Dict[str, Any]], run: Run) -> str:
        """Create prompt for findings analysis."""
        return f"""Analyze the AWS security findings from this ScoutSuite scan and provide expert security assessment.

**SCAN CONTEXT:**
- AWS Account: {run.aws_account or 'default'}
- AWS Region: {run.aws_region}
- Total Findings: {len(findings_data)}
- Scan Timestamp: {datetime.utcnow().isoformat()}

**FINDINGS TO ANALYZE:**
{json.dumps(findings_data, indent=2)}

**ANALYSIS REQUIREMENTS:**

1. **EXPLOITABILITY ASSESSMENT**: For each finding, evaluate:
   - Attack vectors and exploitation difficulty
   - Required attacker capabilities and access level
   - Potential for privilege escalation or lateral movement
   - Network accessibility and exposure scope

2. **BUSINESS IMPACT EVALUATION**: Consider:
   - Data confidentiality, integrity, and availability risks
   - Compliance and regulatory implications
   - Operational disruption potential
   - Financial and reputational impact

3. **FINDING RELATIONSHIPS**: Identify:
   - Related findings that compound risk
   - Common root causes across findings
   - Attack chains that link multiple vulnerabilities
   - Shared remediation opportunities

4. **PRIORITIZATION LOGIC**: Rank by:
   - Actual exploitability (not just theoretical risk)
   - Blast radius and potential impact
   - Ease of remediation vs. risk reduction
   - Regulatory and compliance criticality

**REQUIRED JSON OUTPUT:**
{{
    "executive_summary": {{
        "total_findings": {len(findings_data)},
        "critical_issues": "number of findings requiring immediate attention",
        "key_risks": ["list of top 3 security risks identified"],
        "overall_security_posture": "assessment of current security state"
    }},
    "clusters": [
        {{
            "cluster_id": "descriptive_name",
            "findings": ["finding_id1", "finding_id2"],
            "common_theme": "shared vulnerability pattern or root cause",
            "risk_level": "low|medium|high|critical",
            "attack_scenario": "how these findings could be chained together",
            "remediation_approach": "coordinated fix strategy"
        }}
    ],
    "duplicates": [
        {{
            "primary_finding": "finding_id_to_keep",
            "duplicate_findings": ["finding_id1", "finding_id2"],
            "reason": "why these are considered duplicates"
        }}
    ],
    "prioritized_findings": [
        {{
            "finding_id": "string",
            "priority_score": "1-10 (10 being most critical)",
            "exploitability": "low|medium|high|critical",
            "business_impact": "low|medium|high|critical", 
            "attack_complexity": "low|medium|high",
            "remediation_effort": "low|medium|high",
            "compliance_impact": "relevant compliance frameworks affected",
            "recommendation": "specific next steps and rationale",
            "dependencies": ["other findings that should be fixed together"]
        }}
    ],
    "remediation_roadmap": {{
        "immediate_actions": ["findings requiring emergency response"],
        "short_term": ["findings to address within 1-7 days"],
        "medium_term": ["findings to address within 1-4 weeks"],
        "long_term": ["findings for ongoing security improvement"]
    }}
}}"""
    
    async def _call_claude(self, prompt: str) -> Dict[str, Any]:
        """Call Claude with the given prompt."""
        if not self.client:
            # Return mock analysis for testing
            return self._mock_analysis()
        
        try:
            logger.info("Making Claude API call")
            
            # Make the API call to Claude with system prompt
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=4000,
                system=self._get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the response content
            content = response.content[0].text
            
            # Try to parse as JSON
            try:
                result = json.loads(content)
                logger.info("Claude API call successful", response_length=len(content))
                return result
            except json.JSONDecodeError:
                logger.warning("Claude response was not valid JSON, using fallback")
                # If the response isn't JSON, create a fallback response
                return {
                    "analysis": content,
                    "error": "Response was not JSON",
                    "fallback": True
                }
                
        except Exception as e:
            logger.error("Claude API call failed", error=str(e))
            return self._mock_analysis()
    
    def _mock_analysis(self) -> Dict[str, Any]:
        """Return mock analysis for testing."""
        return {
            "clusters": [
                {
                    "cluster_id": "cluster_1",
                    "findings": ["finding_1", "finding_2"],
                    "common_theme": "IAM policy issues",
                    "risk_level": "high"
                }
            ],
            "duplicates": [],
            "prioritized_findings": [
                {
                    "finding_id": "finding_1",
                    "priority_score": 8,
                    "exploitability": "high",
                    "business_impact": "high",
                    "recommendation": "Immediate remediation required"
                }
            ]
        }
    
    def _apply_analysis(self, findings: List[Finding], analysis: Dict[str, Any]) -> List[Finding]:
        """Apply analysis results to findings."""
        # This would apply the analysis results to the findings
        # For now, return findings as-is
        return findings
    
    async def plan_remediation(
        self,
        finding: Finding,
        guidance: Dict[str, Any],
        run: Run
    ) -> RemediationPlan:
        """Plan remediation for a finding using Claude."""
        if not self.client:
            logger.warning("No Claude client available, using default remediation plan")
            return self._create_default_remediation_plan(finding)
        
        try:
            # Create remediation planning prompt
            prompt = self._create_remediation_prompt(finding, guidance, run)
            
            # Get Claude remediation plan
            plan_data = await self._call_claude(prompt)
            
            # Create remediation plan
            plan = self._create_remediation_plan(finding, plan_data)
            
            logger.info(f"Remediation plan created for finding {finding.id}")
            return plan
            
        except Exception as e:
            logger.error("Remediation planning failed", error=str(e))
            return self._create_default_remediation_plan(finding)
    
    def _create_remediation_prompt(
        self,
        finding: Finding,
        guidance: Dict[str, Any],
        run: Run
    ) -> str:
        """Create prompt for remediation planning."""
        return f"""Plan a comprehensive, production-ready remediation for this critical AWS security finding.

**FINDING DETAILS:**
- Title: {finding.title}
- Service: {finding.service}
- Resource ID: {finding.resource_id}
- Severity: {finding.severity}
- Status: {finding.status}

**DEPLOYMENT CONTEXT:**
- AWS Account: {run.aws_account or 'default'}
- AWS Region: {run.aws_region}
- Timestamp: {datetime.utcnow().isoformat()}

**EVIDENCE & VULNERABILITY DATA:**
{json.dumps(finding.evidence, indent=2)}

**AWS DOCUMENTATION GUIDANCE:**
{json.dumps(guidance, indent=2)}

**REMEDIATION REQUIREMENTS:**

1. **SECURITY ANALYSIS**: 
   - Identify the exact vulnerability and attack vectors
   - Assess blast radius and potential for lateral movement
   - Determine if this is part of a broader security pattern

2. **REMEDIATION STRATEGY**:
   - Apply principle of least privilege
   - Implement defense in depth where applicable
   - Ensure changes don't break legitimate functionality
   - Consider compliance requirements (SOC2, PCI, GDPR, etc.)

3. **IMPLEMENTATION PLAN**:
   - Generate precise AWS MCP server calls
   - Use CCAPI MCP server for direct resource modifications
   - Include all required parameters and resource identifiers
   - Plan for both immediate fix and long-term security posture

4. **OPERATIONAL SAFETY**:
   - Pre-flight checks to validate current state
   - Staged rollout plan for critical resources
   - Rollback procedures for emergency scenarios
   - Post-deployment verification methods

**REQUIRED JSON OUTPUT:**
{{
    "vulnerability_analysis": {{
        "attack_vectors": ["list of how this could be exploited"],
        "blast_radius": "scope of potential impact",
        "compliance_violations": ["relevant frameworks affected"],
        "business_criticality": "low|medium|high|critical"
    }},
    "remediation_strategy": {{
        "approach": "security-focused remediation approach",
        "principles_applied": ["least privilege", "defense in depth", etc.],
        "risk_mitigation": "how this fix reduces attack surface",
        "alternatives_considered": "other approaches evaluated"
    }},
    "pre_checks": [
        {{
            "check_id": "unique_identifier",
            "description": "what to verify before making changes",
            "method": "how to perform this check",
            "expected_result": "what indicates it's safe to proceed",
            "failure_action": "what to do if check fails"
        }}
    ],
    "remediation_steps": [
        {{
            "step_id": "unique_identifier", 
            "order": "execution order number",
            "description": "detailed description of this step",
            "mcp_server": "ccapi",
            "action": "exact MCP tool name",
            "parameters": {{
                "detailed": "parameters for MCP call"
            }},
            "expected_outcome": "what should happen when this succeeds",
            "validation": "how to verify this step worked",
            "rollback_step": "corresponding rollback action"
        }}
    ],
    "rollback_plan": [
        {{
            "trigger_conditions": ["when to execute rollback"],
            "steps": [
                {{
                    "description": "step to undo changes",
                    "mcp_server": "ccapi",
                    "action": "MCP tool name", 
                    "parameters": {{}},
                    "verification": "how to confirm rollback worked"
                }}
            ]
        }}
    ],
    "success_criteria": [
        {{
            "criterion": "specific measurable outcome",
            "verification_method": "how to test this",
            "tools_required": ["tools needed for verification"],
            "expected_result": "what success looks like"
        }}
    ],
    "risk_assessment": {{
        "implementation_risk": "risk of applying this fix",
        "downtime_impact": "expected service disruption",
        "data_impact": "effect on data access/integrity",
        "rollback_complexity": "difficulty of undoing changes",
        "business_impact": "effect on business operations"
    }},
    "long_term_recommendations": [
        {{
            "recommendation": "ongoing security improvement",
            "rationale": "why this matters long-term",
            "implementation_timeline": "when to implement",
            "dependencies": ["what needs to happen first"]
        }}
    ]
}}"""
    
    def _create_remediation_plan(
        self,
        finding: Finding,
        plan_data: Dict[str, Any]
    ) -> RemediationPlan:
        """Create a RemediationPlan from Claude's response."""
        # Extract the first remediation step for the MCP call
        remediation_steps = plan_data.get('remediation_steps', [])
        if not remediation_steps:
            return self._create_default_remediation_plan(finding)
        
        first_step = remediation_steps[0]
        
        return RemediationPlan(
            id=f"remediation_{uuid.uuid4().hex}",
            finding_id=finding.id,
            planned_change=plan_data,
            mcp_server=first_step.get('mcp_server', 'ccapi'),
            mcp_call={
                'action': first_step.get('action', ''),
                'payload': first_step.get('parameters', {})
            }
        )
    
    def _create_default_remediation_plan(self, finding: Finding) -> RemediationPlan:
        """Create a default remediation plan when Claude is not available."""
        # Create a basic plan based on the finding type
        if finding.service.lower() == 'iam':
            return RemediationPlan(
                id=f"remediation_{uuid.uuid4().hex}",
                finding_id=finding.id,
                planned_change={
                    'description': f'Default remediation for {finding.title}',
                    'method': 'manual_review_required'
                },
                mcp_server='ccapi',
                mcp_call={
                    'action': 'review_iam_policy',
                    'payload': {
                        'resource_id': finding.resource_id,
                        'finding_title': finding.title
                    }
                }
            )
        elif finding.service.lower() == 'ec2' and 'security group' in finding.title.lower():
            return RemediationPlan(
                id=f"remediation_{uuid.uuid4().hex}",
                finding_id=finding.id,
                planned_change={
                    'description': f'Restrict security group {finding.evidence.get("security_group_id")} to remove 0.0.0.0/0 access',
                    'method': 'security_group_rule_update'
                },
                mcp_server='ccapi',
                mcp_call={
                    'action': 'update_security_group_rules',
                    'payload': {
                        'securityGroupId': finding.evidence.get('security_group_id'),
                        'rules': {
                            'revoke_ingress': [
                                {
                                    'IpProtocol': '-1',
                                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                                }
                            ],
                            'authorize_ingress': [
                                {
                                    'IpProtocol': 'tcp',
                                    'FromPort': 22,
                                    'ToPort': 22,
                                    'IpRanges': [{'CidrIp': '10.0.0.0/8', 'Description': 'Restricted SSH access'}]
                                },
                                {
                                    'IpProtocol': 'tcp', 
                                    'FromPort': 80,
                                    'ToPort': 80,
                                    'IpRanges': [{'CidrIp': '10.0.0.0/8', 'Description': 'Restricted HTTP access'}]
                                },
                                {
                                    'IpProtocol': 'tcp',
                                    'FromPort': 443,
                                    'ToPort': 443,
                                    'IpRanges': [{'CidrIp': '10.0.0.0/8', 'Description': 'Restricted HTTPS access'}]
                                }
                            ]
                        }
                    }
                }
            )
        else:
            return RemediationPlan(
                id=f"remediation_{uuid.uuid4().hex}",
                finding_id=finding.id,
                planned_change={
                    'description': f'Default remediation for {finding.title}',
                    'method': 'manual_review_required'
                },
                mcp_server='ccapi',
                mcp_call={
                    'action': 'review_resource',
                    'payload': {
                        'service': finding.service,
                        'resource_id': finding.resource_id,
                        'finding_title': finding.title
                    }
                }
            )


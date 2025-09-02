#!/usr/bin/env python3
"""
Complete AutoPurple end-to-end test with actual Claude API integration.

This script demonstrates the full AutoPurple workflow:
1. ScoutSuite discovery 
2. Claude-powered analysis and planning
3. Pacu validation
4. MCP-based remediation execution

Usage: python3 test_full_pipeline.py --claude-api-key YOUR_KEY
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autopurple.cli.main import _run_pipeline
from autopurple.config import get_settings
from autopurple.models.runs import Run
from datetime import datetime
import uuid

async def main():
    """Run the complete AutoPurple pipeline with Claude integration."""
    parser = argparse.ArgumentParser(description="AutoPurple End-to-End Pipeline Test")
    parser.add_argument("--claude-api-key", required=True, help="Your Claude API key")
    parser.add_argument("--aws-profile", default="default", help="AWS profile to use")
    parser.add_argument("--aws-region", default="us-east-1", help="AWS region to scan")
    parser.add_argument("--max-findings", type=int, default=5, help="Maximum findings to process")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Run in dry-run mode")
    
    args = parser.parse_args()
    
    # Set Claude API key in environment
    os.environ['CLAUDE_API_KEY'] = args.claude_api_key
    
    print("🚀 AutoPurple Full Pipeline Test")
    print("=" * 50)
    print(f"AWS Profile: {args.aws_profile}")
    print(f"AWS Region: {args.aws_region}")
    print(f"Max Findings: {args.max_findings}")
    print(f"Dry Run: {args.dry_run}")
    print(f"Claude API: {'✅ Configured' if args.claude_api_key != 'your-actual-key' else '❌ Please set real key'}")
    print()
    
    if args.claude_api_key == 'your-actual-key':
        print("⚠️  Please provide a real Claude API key!")
        return
    
    # Update settings
    settings = get_settings()
    settings.aws_profile = args.aws_profile
    settings.aws_region = args.aws_region
    settings.dry_run_default = args.dry_run
    settings.claude_api_key = args.claude_api_key
    
    # Create a run
    run = Run(
        id=f"test_run_{uuid.uuid4().hex[:8]}",
        started_at=datetime.utcnow(),
        aws_account=args.aws_profile,
        aws_region=args.aws_region
    )
    
    print(f"🎯 Starting pipeline run: {run.id}")
    print()
    
    try:
        # Run the pipeline
        await _run_pipeline(settings, args.max_findings)
        print()
        print("✅ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

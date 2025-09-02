"""
Setup command for AutoPurple CLI
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()

def setup_command():
    """Interactive setup wizard for AutoPurple."""
    console.print(Panel.fit("🟣 AutoPurple Setup Wizard", style="bold blue"))
    
    # Check if already configured
    config_file = Path.home() / ".autopurple" / "config.yaml"
    if config_file.exists():
        if not Confirm.ask("AutoPurple is already configured. Reconfigure?"):
            return
    
    # Create config directory
    config_dir = Path.home() / ".autopurple"
    config_dir.mkdir(exist_ok=True)
    
    console.print("\n🔧 [bold]Setting up AutoPurple components...[/bold]")
    
    # Step 1: Install UV if not present
    install_uv()
    
    # Step 2: Install MCP servers
    install_mcp_servers()
    
    # Step 3: Configure Claude API
    claude_key = configure_claude()
    
    # Step 4: Configure AWS
    configure_aws()
    
    # Step 5: Create config file
    create_config(config_dir / "config.yaml", claude_key)
    
    console.print("\n🎉 [bold green]AutoPurple setup complete![/bold green]")
    console.print("You can now run: [bold cyan]autopurple run --region us-east-1[/bold cyan]")

def install_uv():
    """Install UV package manager if not present."""
    console.print("\n📦 [bold]Installing UV package manager...[/bold]")
    
    try:
        subprocess.run(["uvx", "--version"], check=True, capture_output=True)
        console.print("✅ UV is already installed")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    try:
        console.print("Installing UV...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
        console.print("✅ UV installed successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to install UV: {e}")

def install_mcp_servers():
    """Install MCP servers."""
    console.print("\n🔧 [bold]Installing MCP servers...[/bold]")
    
    servers = [
        "awslabs.ccapi-mcp-server@latest",
        "awslabs.aws-documentation-mcp-server@latest"
    ]
    
    for server in servers:
        try:
            console.print(f"Installing {server}...")
            subprocess.run(["uvx", "install", server], check=True, capture_output=True)
            console.print(f"✅ {server} installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(f"⚠️  Failed to install {server}")

def configure_claude():
    """Configure Claude API key."""
    console.print("\n🧠 [bold]Configuring Claude AI...[/bold]")
    
    existing_key = os.environ.get('CLAUDE_API_KEY')
    if existing_key and existing_key.startswith('sk-ant-api'):
        console.print("✅ Claude API key found in environment")
        return existing_key
    
    console.print("Get your Claude API key at: [link]https://console.anthropic.com/[/link]")
    
    claude_key = Prompt.ask("Enter your Claude API key (or press Enter to skip)", default="")
    
    if claude_key and claude_key.startswith('sk-ant-api'):
        console.print("✅ Claude API key configured")
        return claude_key
    else:
        console.print("⚠️  Skipping Claude configuration")
        return None

def configure_aws():
    """Configure AWS credentials."""
    console.print("\n☁️  [bold]AWS credentials...[/bold]")
    
    if os.environ.get('AWS_ACCESS_KEY_ID') or os.path.exists(Path.home() / '.aws' / 'credentials'):
        console.print("✅ AWS credentials found")
    else:
        console.print("⚠️  AWS credentials not found")
        console.print("Configure with environment variables or AWS CLI")

def create_config(config_path: Path, claude_key: Optional[str]):
    """Create configuration file."""
    console.print(f"\n📝 [bold]Creating config file...[/bold]")
    
    config_content = f"""# AutoPurple Configuration
claude:
  api_key: "{claude_key or 'your-claude-api-key-here'}"

aws:
  region: "us-east-1"

mcp:
  enabled: true
"""
    
    config_path.write_text(config_content)
    console.print("✅ Configuration saved")

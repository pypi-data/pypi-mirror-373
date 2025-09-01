"""Command-line interface utilities for Strands MCP Server."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

import click


def check_token_validity(token: str) -> bool:
    """Check if a GitHub token appears to be valid format."""
    if not token:
        return False
    
    # GitHub personal access tokens start with specific prefixes
    valid_prefixes = ['ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_']
    
    if not any(token.startswith(prefix) for prefix in valid_prefixes):
        return False
    
    # Basic length check (GitHub tokens are typically 40+ characters)
    if len(token) < 20:
        return False
    
    return True


def get_mcp_config_paths() -> Dict[str, Path]:
    """Get possible MCP configuration file paths."""
    home = Path.home()
    
    paths = {
        'kiro_user': home / '.kiro' / 'settings' / 'mcp.json',
        'kiro_workspace': Path('.kiro') / 'settings' / 'mcp.json',
        'claude_desktop': home / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json',
    }
    
    # Add Windows Claude path if on Windows
    if sys.platform == 'win32':
        paths['claude_desktop_windows'] = home / 'AppData' / 'Roaming' / 'Claude' / 'claude_desktop_config.json'
    
    return paths


def update_mcp_config(config_path: Path, token: str) -> bool:
    """Update MCP configuration file with GitHub token."""
    try:
        # Read existing config or create new one
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {'mcpServers': {}}
        
        # Ensure mcpServers exists
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        
        # Update or create strands-docs server config
        if 'strands-docs' not in config['mcpServers']:
            # Create new server config
            if 'kiro' in str(config_path):
                # Kiro configuration
                config['mcpServers']['strands-docs'] = {
                    'command': 'uvx',
                    'args': ['strands-mcp-server@latest'],
                    'env': {'GITHUB_TOKEN': token},
                    'disabled': False,
                    'autoApprove': ['search_documentation', 'list_documentation']
                }
            else:
                # Claude Desktop configuration
                config['mcpServers']['strands-docs'] = {
                    'command': 'python',
                    'args': ['-m', 'strands_mcp.main'],
                    'env': {'GITHUB_TOKEN': token}
                }
        else:
            # Update existing server config
            if 'env' not in config['mcpServers']['strands-docs']:
                config['mcpServers']['strands-docs']['env'] = {}
            config['mcpServers']['strands-docs']['env']['GITHUB_TOKEN'] = token
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    
    except Exception as e:
        click.echo(f"Error updating {config_path}: {e}")
        return False


def setup_environment_variable(token: str, shell: str = 'auto') -> str:
    """Generate shell commands to set up environment variable."""
    if shell == 'auto':
        shell = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell:
            shell = 'zsh'
        elif 'fish' in shell:
            shell = 'fish'
        else:
            shell = 'bash'
    
    if shell == 'fish':
        return f"set -Ux GITHUB_TOKEN {token}"
    else:
        profile_file = '~/.zshrc' if shell == 'zsh' else '~/.bashrc'
        return f"""# Add to your {profile_file}:
export GITHUB_TOKEN={token}

# Or run this command to add it automatically:
echo 'export GITHUB_TOKEN={token}' >> {profile_file}
source {profile_file}"""


@click.command()
@click.option('--token', help='GitHub personal access token')
@click.option('--env-only', is_flag=True, help='Only set up environment variable')
@click.option('--mcp-only', is_flag=True, help='Only update MCP configurations')
def setup_token(token: Optional[str], env_only: bool, mcp_only: bool) -> None:
    """Set up GitHub token for Strands MCP Server."""
    click.echo("🔧 Strands MCP Server - GitHub Token Setup")
    click.echo("=" * 50)
    click.echo()
    
    # Check if token is already set
    existing_token = os.environ.get('GITHUB_TOKEN')
    if existing_token and check_token_validity(existing_token):
        click.echo("✅ GitHub token is already configured in environment variables")
        click.echo(f"   Token: {existing_token[:8]}...{existing_token[-4:]}")
        click.echo()
    
    # Get token from user if not provided
    if not token:
        click.echo("Please enter your GitHub personal access token:")
        click.echo("(Create one at: https://github.com/settings/tokens)")
        click.echo("Required scopes: 'public_repo'")
        click.echo()
        
        token = click.prompt("GitHub Token", hide_input=True).strip()
    
    if not token:
        click.echo("❌ No token provided. Exiting.")
        return
    
    if not check_token_validity(token):
        click.echo("⚠️  Warning: Token format doesn't look like a valid GitHub token")
        click.echo("   GitHub tokens typically start with 'ghp_', 'gho_', 'ghu_', 'ghs_', or 'ghr_'")
        
        if not click.confirm("Continue anyway?"):
            return
    
    # Determine what to set up
    if env_only:
        setup_env = True
        setup_mcp = False
    elif mcp_only:
        setup_env = False
        setup_mcp = True
    else:
        click.echo()
        click.echo("🔍 Setup Options:")
        click.echo("1. Environment variable (recommended for development)")
        click.echo("2. MCP configuration files (recommended for MCP clients)")
        click.echo("3. Both")
        click.echo()
        
        choice = click.prompt("Choose option", type=click.Choice(['1', '2', '3']))
        setup_env = choice in ['1', '3']
        setup_mcp = choice in ['2', '3']
    
    if setup_env:
        click.echo()
        click.echo("📝 Environment Variable Setup:")
        click.echo("-" * 30)
        env_commands = setup_environment_variable(token)
        click.echo(env_commands)
        click.echo()
    
    if setup_mcp:
        click.echo()
        click.echo("📝 MCP Configuration Setup:")
        click.echo("-" * 30)
        
        config_paths = get_mcp_config_paths()
        updated_configs = []
        
        for name, path in config_paths.items():
            if name == 'kiro_workspace' and not path.parent.exists():
                continue  # Skip workspace config if not in a workspace
            
            if name.startswith('claude') and not path.parent.exists():
                continue  # Skip Claude config if Claude not installed
            
            click.echo(f"Updating {name} config: {path}")
            if update_mcp_config(path, token):
                updated_configs.append(name)
                click.echo(f"✅ Updated {name} configuration")
            else:
                click.echo(f"❌ Failed to update {name} configuration")
        
        if updated_configs:
            click.echo()
            click.echo("🔄 Next Steps:")
            click.echo("- Restart your MCP client (Claude Desktop, Kiro IDE, etc.)")
            click.echo("- The Strands MCP Server should now have access to GitHub API")
        else:
            click.echo("❌ No MCP configurations were updated")
    
    click.echo()
    click.echo("🧪 Testing Your Setup:")
    click.echo("-" * 20)
    click.echo("You can test your GitHub token setup by running:")
    click.echo("  python scripts/build_bundled_cache.py --force")
    click.echo()
    click.echo("If successful, you should see documentation being fetched without rate limit errors.")
    click.echo()
    click.echo("🔒 Security Notes:")
    click.echo("- Never commit your GitHub token to source control")
    click.echo("- Use repository secrets for CI/CD workflows")
    click.echo("- Regenerate tokens if they're accidentally exposed")
    click.echo()
    click.echo("✅ Setup complete! Your GitHub token is now configured.")


def build_cache_command(force: bool = False, check_only: bool = False, verbose: bool = False) -> None:
    """Build bundled documentation cache for the MCP server."""
    import asyncio
    import sys
    from pathlib import Path
    
    # Add project root to path to import build_hook
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from build_hook import BuildHook
        
        # Create and run build hook
        hook = BuildHook()
        
        # Set verbose logging if requested
        if verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Handle check-only mode
        if check_only:
            exists = hook._check_cache_exists()
            if exists:
                click.echo("✅ Bundled cache exists and has content")
                sys.exit(0)
            else:
                click.echo("❌ Bundled cache does not exist or is empty")
                sys.exit(1)
        
        # Run the build hook
        result = asyncio.run(hook.execute(force=force))
        sys.exit(result)
        
    except ImportError as e:
        click.echo(f"❌ Error: Could not import build hook: {e}")
        click.echo("Make sure you're running this from the project root directory")
        sys.exit(3)
    except Exception as e:
        click.echo(f"❌ Error: Build hook failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    setup_token()
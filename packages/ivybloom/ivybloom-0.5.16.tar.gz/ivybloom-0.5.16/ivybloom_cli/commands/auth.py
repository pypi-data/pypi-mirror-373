"""
Authentication commands for ivybloom CLI
"""

import click
import webbrowser
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info
from ..client.api_client import IvyBloomAPIClient
from ..utils.browser_auth import browser_login, device_flow_login

console = get_console()

@click.group()
def auth():
    """🔐 Authentication management commands
    
    Manage your IvyBloom CLI authentication credentials and account linking.
    
    QUICK START:
    
      • First time:        ivybloom auth login --browser
      • Headless/CI:       ivybloom auth login --api-key
      • Link CLI:          ivybloom auth link
      • Check status:      ivybloom auth status
    
    AUTHENTICATION METHODS:
    
      🌐 Browser OAuth (Recommended): Secure, user-friendly authentication
      🔑 API Key: For automation, CI/CD, and headless environments  
      🔗 CLI Linking: Link this CLI installation to your web account
      📱 Device Flow: For remote servers without browser access
    
    Get your API key at: https://ivybiosciences.com/settings/api-keys
    
    Run 'ivybloom auth <command> --help' for detailed help on each command.
    """
    pass

@auth.command()
@click.option('--api-key', help='Provide API key directly (non-interactive)')
@click.option('--browser', is_flag=True, help='Login using browser (OAuth flow)')
@click.option('--device', is_flag=True, help='Login using device flow (for headless environments)')
@click.option('--link', is_flag=True, help='Link this CLI installation to your account (no API key)')
@click.option('--frontend-url', help='Override frontend URL for link flow (e.g., https://app.example.com)')
@click.option('--no-verify', is_flag=True, help='Skip API key validation')
@click.option('--force', is_flag=True, help='Overwrite existing credentials')
@click.pass_context
def login(ctx, api_key, browser, device, link, frontend_url, no_verify, force):
    """🚀 Login to IvyBloom platform
    
    Choose your preferred authentication method:
    
    RECOMMENDED: Browser OAuth (most secure)
      ivybloom auth login --browser
    
    FOR AUTOMATION: API Key authentication  
      ivybloom auth login --api-key
    
    FOR HEADLESS SERVERS: Device flow
      ivybloom auth login --device
      
    FOR CLI LINKING: Connect this CLI to your web account
      ivybloom auth login --link
    
    💡 TIP: After login, run 'ivybloom auth status' to verify your connection.
    """
    """Login with API key or browser authentication"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if auth_manager.is_authenticated() and not force:
        print_info("You are already logged in.")
        console.print("Use 'ivybloom auth logout' to logout first, or use --force to overwrite.")
        return
    
    # Handle link-based pairing (client UUID + Clerk user)
    if link:
        api_url = config.get_api_url()
        resolved_frontend = (frontend_url or config.get_frontend_url())
        if not resolved_frontend:
            console.print("[red]Error: Frontend URL not configured.[/red]")
            console.print("Set IVY_FRONTEND_URL or run: ivybloom config set frontend_url https://your-frontend-host")
            return
        
        import socket
        from rich.prompt import Prompt
        client_id = config.get_or_create_client_id()
        # Prompt for a human-friendly name for this installation
        installation_name = Prompt.ask(
            "Enter a name for this CLI installation",
            default=socket.gethostname(),
            show_default=True
        )
        # Generate the CLI linking URL with proper URL encoding
        import urllib.parse
        encoded_installation_name = urllib.parse.quote(installation_name)
        pair_url = f"{resolved_frontend.rstrip('/')}/cli/link?client_id={client_id}&installation_name={encoded_installation_name}"
        
        console.print()
        console.print(f"🔗 [welcome.text]Link this CLI Installation to your Account[/welcome.text]")
        console.print(f"   Installation: [cli.accent]{installation_name}[/cli.accent]")
        console.print(f"   Client ID: [cli.accent]{client_id}[/cli.accent]")
        console.print(f"   Linking Page: [cli.bright]{pair_url}[/cli.bright]")
        console.print()
        
        # Open browser automatically
        try:
            webbrowser.open(pair_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            console.print(f"Please manually visit: {pair_url}")
        
        console.print()
        console.print("📋 [yellow]Next Steps:[/yellow]")
        console.print("   1. Sign in to your IvyBloom account in the browser")
        console.print("   2. Approve the CLI linking request")
        console.print("   3. Wait for automatic authentication to complete")
        console.print()
        console.print("🔄 [yellow]Waiting for you to complete linking in your browser...[/yellow]")
        console.print("   Press Ctrl+C to cancel")
        console.print()
        
        # Poll for linking completion
        success = _wait_for_cli_linking(config, auth_manager, client_id)
        
        if success:
            console.print()
            print_success("🎉 CLI successfully linked and authenticated!")
            console.print("✨ [green]Ready to go! Try these commands:[/green]")
            console.print("   [cli.accent]ivybloom tools list[/cli.accent]     - Browse available tools")
            console.print("   [cli.accent]ivybloom projects list[/cli.accent]  - View your projects") 
            console.print("   [cli.accent]ivybloom --help[/cli.accent]         - See all commands")
            console.print()
        else:
            print_error("CLI linking failed or was cancelled.")
            console.print("💡 [yellow]Troubleshooting tips:[/yellow]")
            console.print("   • Make sure you're logged in to the web app")
            console.print("   • Try the linking process again")
            console.print("   • Use 'ivybloom auth login --browser' as an alternative")
        
        return

    # Handle browser/device authentication
    if browser or device:
        api_url = config.get_api_url()
        
        if browser:
            console.print()
            console.print("🌐 [bold cyan]Browser Authentication[/bold cyan]")
            console.print("   Starting secure OAuth flow via your default browser...")
            console.print()
            auth_result = browser_login(api_url)
        else:  # device flow
            console.print()
            console.print("📱 [bold cyan]Device Authentication[/bold cyan]")
            console.print("   Starting device flow for headless environments...")
            console.print()
            auth_result = device_flow_login(api_url)
        
        if 'error' in auth_result:
            print_error(f"Authentication failed: {auth_result['error']}")
            console.print()
            console.print("💡 [yellow]Troubleshooting tips:[/yellow]")
            console.print("   • Check your internet connection")
            console.print("   • Try running the command again")
            console.print("   • Use --device flag if browser issues persist")
            console.print("   • Contact support if problems continue")
            return
        
        # Store tokens
        auth_manager.store_oauth_tokens(auth_result)
        console.print()
        print_success("🎉 Successfully authenticated with IvyBloom!")
        
        # Show user info
        try:
            with IvyBloomAPIClient(config, auth_manager) as client:
                user_info = client.get_account_info()
                console.print(f"   Logged in as: [cli.accent]{user_info.get('email', 'Unknown')}[/cli.accent]")
                console.print(f"   User ID: [cli.dim]{user_info.get('user_id', 'Unknown')}[/cli.dim]")
        except Exception as e:
            print_info("Authentication successful, but couldn't fetch user info")
        
        console.print()
        console.print("✨ [green]Ready to go! Try these commands:[/green]")
        console.print("   [cli.accent]ivybloom tools list[/cli.accent]     - Browse available tools")
        console.print("   [cli.accent]ivybloom projects list[/cli.accent]  - View your projects") 
        console.print("   [cli.accent]ivybloom --help[/cli.accent]         - See all commands")
        console.print()
        
        return
    
    # Handle API key authentication
    if not api_key:
        api_key = auth_manager.prompt_for_api_key()
    
    if not api_key:
        print_error("No API key provided. Login cancelled.")
        return
    
    # Store API key
    auth_manager.store_api_key(api_key)
    
    # Test the API key unless --no-verify is used
    if not no_verify:
        print_info("Validating API key...")
        
        try:
            # Test API connection
            with IvyBloomAPIClient(config, auth_manager) as client:
                account_info = client.get_account_info()
                
            console.print(f"[green]✅ Successfully logged in as {account_info.get('email', 'Unknown')}[/green]")
            
        except Exception as e:
            # Remove the invalid API key
            auth_manager.remove_api_key()
            console.print(f"[red]❌ Login failed: {e}[/red]")
            console.print("Please check your API key and try again.")
            return
    else:
        console.print("[green]✅ API key stored (validation skipped)[/green]")

@auth.command()
@click.option('--open', 'open_browser', is_flag=True, help='Open link in default browser (default: true)')
@click.option('--frontend-url', help='Override frontend URL for link flow (e.g., https://app.example.com)')
@click.option('--no-wait', is_flag=True, help='Don\'t wait for linking completion')
@click.pass_context
def link(ctx, open_browser, frontend_url, no_wait):
    """🔗 Link this CLI installation to your IvyBloom account
    
    This creates a secure connection between this CLI and your web account.
    An API key is automatically generated and configured for you!
    
    USAGE:
      ivybloom auth link                    # Auto-open browser and wait
      ivybloom auth link --no-wait          # Generate link only, don't wait
    
    PROCESS:
      1. CLI generates a unique installation identifier
      2. Browser opens to the CLI linking page
      3. Sign in to your IvyBloom account
      4. Approve the CLI linking request
      5. CLI automatically retrieves credentials and is ready to use!
    
    💡 TIP: This is the easiest way to set up CLI authentication - no manual API key copying!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if auth_manager.is_authenticated():
        print_info("You are already authenticated.")
        console.print("Use 'ivybloom auth logout' first if you want to re-link.")
        return
    
    resolved_frontend = (frontend_url or config.get_frontend_url())
    if not resolved_frontend:
        console.print("[red]Error: Frontend URL not configured.[/red]")
        console.print("Set IVY_FRONTEND_URL or run: ivybloom config set frontend_url https://your-frontend-host")
        return
    
    import socket
    from rich.prompt import Prompt
    client_id = config.get_or_create_client_id()
    installation_name = Prompt.ask(
        "Enter a name for this CLI installation",
        default=socket.gethostname(),
        show_default=True
    )
    # Generate the CLI linking URL with proper URL encoding
    import urllib.parse
    encoded_installation_name = urllib.parse.quote(installation_name)
    pair_url = f"{resolved_frontend.rstrip('/')}/cli/link?client_id={client_id}&installation_name={encoded_installation_name}"

    console.print()
    console.print(f"🔗 [welcome.text]Link this CLI Installation to your Account[/welcome.text]")
    console.print(f"   Installation: [cli.accent]{installation_name}[/cli.accent]")
    console.print(f"   Client ID: [cli.accent]{client_id}[/cli.accent]")
    console.print(f"   Linking Page: [cli.bright]{pair_url}[/cli.bright]")
    console.print()

    # Auto-open browser by default (unless explicitly disabled)
    if open_browser is not False:
        try:
            webbrowser.open(pair_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            console.print(f"Please manually visit: {pair_url}")
    
    if not no_wait:
        console.print()
        console.print("📋 [yellow]Next Steps:[/yellow]")
        console.print("   1. Sign in to your IvyBloom account in the browser")
        console.print("   2. Approve the CLI linking request")
        console.print("   3. Wait for automatic authentication to complete")
        console.print()
        console.print("🔄 [yellow]Waiting for you to complete linking in your browser...[/yellow]")
        console.print("   Press Ctrl+C to cancel")
        console.print()
        
        # Poll for linking completion
        success = _wait_for_cli_linking(config, auth_manager, client_id)
        
        if success:
            console.print()
            print_success("🎉 CLI successfully linked and authenticated!")
            console.print("✨ [green]Ready to go! Try these commands:[/green]")
            console.print("   [cli.accent]ivybloom tools list[/cli.accent]     - Browse available tools")
            console.print("   [cli.accent]ivybloom projects list[/cli.accent]  - View your projects") 
            console.print("   [cli.accent]ivybloom --help[/cli.accent]         - See all commands")
            console.print()
        else:
            print_error("CLI linking failed or was cancelled.")
            console.print("💡 [yellow]Troubleshooting tips:[/yellow]")
            console.print("   • Make sure you're logged in to the web app")
            console.print("   • Try the linking process again")
            console.print("   • Use 'ivybloom auth login --browser' as an alternative")
    else:
        console.print("🔄 [yellow]CLI linking URL created.[/yellow]")
        console.print("   Complete the linking process in your browser.")
        console.print("   Run 'ivybloom auth status' to check if linking was successful.")

@auth.command()
@click.argument('client_id', required=False)
@click.option('--frontend-url', help='Override frontend URL for testing')
def debug_link(client_id, frontend_url):
    """🔍 Debug CLI linking endpoints for troubleshooting
    
    Test the CLI linking endpoints to diagnose connection issues.
    If no client_id is provided, generates a test UUID.
    
    USAGE:
      ivybloom auth debug-link                    # Test with random client ID
      ivybloom auth debug-link YOUR_CLIENT_ID     # Test with specific client ID
    
    This command helps diagnose:
      • Domain redirect issues (308 responses)
      • WAF/Cloudflare blocking (403 responses)
      • Endpoint availability (404 responses)
      • Network connectivity issues
    """
    import httpx
    import uuid
    from rich.table import Table
    
    config = Config()
    
    # Use provided client_id or generate test one
    test_client_id = client_id or str(uuid.uuid4())
    resolved_frontend = frontend_url or config.get_frontend_url()
    
    console.print(f"\n🔍 [yellow]Testing CLI linking endpoints...[/yellow]")
    console.print(f"   Frontend URL: [cli.bright]{resolved_frontend}[/cli.bright]")
    console.print(f"   Test Client ID: [cli.accent]{test_client_id}[/cli.accent]")
    console.print()
    
    # Test table
    table = Table(title="🧪 CLI Linking Endpoint Tests")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Response", style="green")
    table.add_column("Notes", style="yellow")
    
    # Test link-status endpoint
    status_url = f"{resolved_frontend.rstrip('/')}/api/cli/link-status/{test_client_id}"
    try:
        with httpx.Client(follow_redirects=True, timeout=10.0) as client:
            response = client.get(status_url, headers={
                "User-Agent": "ivybloom-cli/0.3.4",
                "Accept": "application/json"
            })
            
            redirects = len(response.history) if hasattr(response, 'history') else 0
            redirect_note = f" ({redirects} redirects)" if redirects > 0 else ""
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    table.add_row("link-status", "✅ 200", str(data), f"Success{redirect_note}")
                except:
                    table.add_row("link-status", "✅ 200", "Non-JSON response", f"Unexpected format{redirect_note}")
            elif response.status_code == 401:
                table.add_row("link-status", "🔐 401", "Unauthorized", f"Endpoint exists, auth required{redirect_note}")
            elif response.status_code == 404:
                table.add_row("link-status", "❌ 404", "Not Found", f"Endpoint missing{redirect_note}")
            elif response.status_code == 403:
                table.add_row("link-status", "🚫 403", "Forbidden", f"WAF/Cloudflare blocking{redirect_note}")
            else:
                table.add_row("link-status", f"⚠️ {response.status_code}", response.reason_phrase or "Unknown", f"Unexpected response{redirect_note}")
                
    except Exception as e:
        table.add_row("link-status", "💥 ERROR", str(e), "Network/connection issue")
    
    # Test verify-link endpoint  
    verify_url = f"{resolved_frontend.rstrip('/')}/api/cli/verify-link/{test_client_id}"
    try:
        with httpx.Client(follow_redirects=True, timeout=10.0) as client:
            response = client.post(verify_url, headers={
                "User-Agent": "ivybloom-cli/0.3.4",
                "Accept": "application/json",
                "Content-Type": "application/json"
            })
            
            redirects = len(response.history) if hasattr(response, 'history') else 0
            redirect_note = f" ({redirects} redirects)" if redirects > 0 else ""
            
            if response.status_code == 200:
                table.add_row("verify-link", "✅ 200", "Success", f"Endpoint working{redirect_note}")
            elif response.status_code == 404:
                table.add_row("verify-link", "❌ 404", "Not Found", f"Client not linked{redirect_note}")
            elif response.status_code == 410:
                table.add_row("verify-link", "⏰ 410", "Gone", f"Temp key expired/missing{redirect_note}")
            elif response.status_code == 401:
                table.add_row("verify-link", "🔐 401", "Unauthorized", f"Endpoint exists, auth required{redirect_note}")
            elif response.status_code == 403:
                table.add_row("verify-link", "🚫 403", "Forbidden", f"WAF/Cloudflare blocking{redirect_note}")
            else:
                table.add_row("verify-link", f"⚠️ {response.status_code}", response.reason_phrase or "Unknown", f"Unexpected response{redirect_note}")
                
    except Exception as e:
        table.add_row("verify-link", "💥 ERROR", str(e), "Network/connection issue")
    
    console.print(table)
    console.print()
    
    # Recommendations
    console.print("💡 [yellow]Troubleshooting Tips:[/yellow]")
    console.print("   • 401/404 responses are normal for test client IDs")
    console.print("   • 403 responses suggest WAF/Cloudflare blocking")
    console.print("   • Multiple redirects may cause issues - check frontend URL")
    console.print("   • Network errors suggest connectivity issues")
    console.print()
    console.print("🔧 [yellow]For WAF issues, whitelist:[/yellow]")
    console.print("   • Path prefix: [cli.accent]/api/cli/*[/cli.accent]")
    console.print("   • User-Agent: [cli.accent]ivybloom-cli*[/cli.accent]")
    console.print()

@auth.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def logout(ctx, confirm):
    """🚪 Logout and clear authentication credentials
    
    This removes all stored authentication data from this device:
    • API keys • OAuth tokens • CLI linking • JWT tokens
    
    USAGE:
      ivybloom auth logout                  # Interactive confirmation
      ivybloom auth logout --confirm        # Skip confirmation
    
    💡 TIP: You can always login again with 'ivybloom auth login'
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[yellow]You are not logged in.[/yellow]")
        return
    
    # Confirm logout unless --confirm is used
    if not confirm:
        if not click.confirm("Are you sure you want to logout?"):
            console.print("Logout cancelled.")
            return
    
    # Remove credentials
    auth_manager.remove_api_key()
    auth_manager.remove_auth_token()
    
    console.print("[green]✅ Successfully logged out[/green]")

@auth.command()
@click.option('--check-connectivity', is_flag=True, help='Test API connectivity')
@click.option('--show-permissions', is_flag=True, help='Display API key permissions')
@click.pass_context
def status(ctx, check_connectivity, show_permissions):
    """📊 Check authentication status and connectivity
    
    Verify your CLI authentication and connection to IvyBloom services.
    
    USAGE:
      ivybloom auth status                        # Basic status
      ivybloom auth status --check-connectivity  # Test API connection  
      ivybloom auth status --show-permissions    # Show detailed permissions
    
    SHOWS:
      ✅ Authentication method • Account info • Connection status
      🔑 API key details • Token expiration • Rate limits
      🌐 API endpoint • Network connectivity • Service health
    
    💡 TIP: Run this if you're having connection issues.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Create status table
    table = Table(title="🔐 Authentication Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    if auth_manager.is_authenticated():
        # Get account info
        try:
            with IvyBloomAPIClient(config, auth_manager) as client:
                account_info = client.get_account_info()
            
            table.add_row("Status", "✅ Authenticated")
            table.add_row("Email", account_info.get('email', 'Unknown'))
            table.add_row("User ID", account_info.get('user_id', 'Unknown'))
            table.add_row("Plan", account_info.get('plan', 'Unknown'))
            table.add_row("API Keys", f"{account_info.get('api_keys_count', 0)}/{account_info.get('api_keys_limit', 'Unknown')}")
            
            # Show token expiration info if available
            oauth_tokens = auth_manager.get_oauth_tokens()
            if oauth_tokens and 'expires_at' in oauth_tokens:
                try:
                    from datetime import datetime
                    expires_at = datetime.fromisoformat(oauth_tokens['expires_at'])
                    time_left = expires_at - datetime.now()
                    
                    if time_left.total_seconds() > 0:
                        hours = int(time_left.total_seconds() // 3600)
                        minutes = int((time_left.total_seconds() % 3600) // 60)
                        table.add_row("Token Expires", f"In {hours}h {minutes}m")
                    else:
                        table.add_row("Token Status", "🔄 Auto-refreshing expired token")
                except Exception:
                    pass
            
        except Exception as e:
            table.add_row("Status", "❌ Authentication Error")
            table.add_row("Error", str(e))
    else:
        table.add_row("Status", "❌ Not authenticated")
        table.add_row("Action", "Run 'ivybloom auth login' to authenticate")
    
    console.print(table)

@auth.command()
@click.pass_context
def whoami(ctx):
    """👤 Show current user account information
    
    Display details about the currently authenticated user.
    
    SHOWS:
      • User ID and email address
      • Account type and status  
      • Organization/team info
      • Subscription details
      • Usage statistics
    
    💡 TIP: Use this to verify you're logged into the correct account.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated[/red]")
        console.print("Run 'ivybloom auth login' to authenticate")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            account_info = client.get_account_info()
        
        console.print(f"[bold cyan]👤 {account_info.get('email', 'Unknown')}[/bold cyan]")
        console.print(f"   User ID: {account_info.get('user_id', 'Unknown')}")
        console.print(f"   Plan: {account_info.get('plan', 'Unknown')}")
        
    except Exception as e:
        console.print(f"[red]❌ Error getting user info: {e}[/red]")

def _wait_for_cli_linking(config: Config, auth_manager: AuthManager, client_id: str, timeout: int = 300) -> bool:
    """Wait for CLI linking to complete with polling and loading indicator"""
    import time
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    
    # Create a loading indicator with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        TextColumn("• Timeout in {task.fields[remaining]:.0f}s"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task(
            "Waiting for linking completion...", 
            total=timeout,
            remaining=timeout
        )
        
        start_time = time.time()
        poll_interval = 2.5  # Poll every 2.5 seconds (within 2-3s range)
        
        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            
            # Update progress
            progress.update(task, completed=elapsed, remaining=remaining)
            
            try:
                # Check linking status via frontend (avoids backend SSL issues)
                import httpx
                frontend_url = config.get_frontend_url()
                status_url = f"{frontend_url.rstrip('/')}/api/cli/link-status/{client_id}"
                
                # Configure client with redirect following and timeout
                with httpx.Client(
                    follow_redirects=True,
                    timeout=30.0,
                    headers={
                        "User-Agent": "ivybloom-cli/0.3.4",
                        "Accept": "application/json"
                    }
                ) as client:
                    response = client.get(status_url)
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        
                        if status_data.get('linked', False):
                            # Check if ready flag is present (newer deployments)
                            ready_flag = status_data.get('ready')
                            
                            if ready_flag is not None:
                                # New behavior: only proceed when ready is true
                                if ready_flag:
                                    # Linking completed and ready! Now verify and get credentials
                                    progress.update(task, description="✅ Linking ready! Verifying...")
                                    time.sleep(0.5)
                                else:
                                    # Linked but not ready yet - continue polling
                                    progress.update(task, description="⏳ Linked, waiting for API key generation...")
                                    time.sleep(poll_interval)
                                    continue
                            else:
                                # Fallback behavior for older deployments without ready flag
                                progress.update(task, description="✅ Linking completed! Verifying...")
                                time.sleep(0.5)
                            
                            # Use frontend endpoint to verify and get auto-generated API key
                            try:
                                verify_url = f"{frontend_url.rstrip('/')}/api/cli/verify-link/{client_id}"
                                verify_headers = {
                                    "Content-Type": "application/json",
                                    "User-Agent": "ivybloom-cli/0.3.4",
                                    "x-ivybloom-client": client_id,
                                    "Accept": "application/json"
                                }
                                
                                # Use a separate client for verify request to ensure proper redirect handling
                                with httpx.Client(
                                    follow_redirects=True,
                                    timeout=30.0
                                ) as verify_client:
                                    verify_response = verify_client.post(verify_url, headers=verify_headers)
                                
                                if verify_response.status_code == 410:
                                    # Temp key expired/already retrieved - handle based on ready flag presence
                                    if ready_flag is not None:
                                        # New deployment: this shouldn't happen if we waited for ready=true
                                        # But if it does, it means the key was already consumed
                                        progress.update(task, description="❌ API key already retrieved or expired!")
                                        time.sleep(1)
                                        return False
                                    else:
                                        # Older deployment: fallback behavior - retry after short delay
                                        progress.update(task, description="⏳ API key not ready yet, retrying...")
                                        time.sleep(2)  # Wait a bit longer before retrying
                                        continue  # Go back to polling status
                                elif verify_response.status_code >= 400:
                                    try:
                                        error_data = verify_response.json()
                                        error_msg = error_data.get('error', error_data.get('detail', error_data.get('message', f'HTTP {verify_response.status_code}')))
                                    except:
                                        error_msg = f'HTTP {verify_response.status_code}'
                                    raise Exception(f"API error: {error_msg}")
                                
                                verify_result = verify_response.json()
                                
                                if verify_result.get('success'):
                                    # Store the auto-generated API key
                                    if 'api_key' in verify_result:
                                        auth_manager.store_api_key(verify_result['api_key'])
                                        progress.update(task, description="✅ API key retrieved and stored!")
                                        time.sleep(0.5)
                                    
                                    # If the frontend provides a Clerk session/JWT for CLI, store it as well
                                    try:
                                        clerk_session = verify_result.get('clerk_session')
                                        if isinstance(clerk_session, dict):
                                            # Store long-lived JWT if present
                                            jwt_token = clerk_session.get('jwt') or clerk_session.get('token')
                                            if isinstance(jwt_token, str) and jwt_token.strip():
                                                auth_manager.store_auth_token(jwt_token.strip())
                                            # Persist full Clerk session for potential future use/validation
                                            auth_manager.store_clerk_session(clerk_session)
                                    except Exception:
                                        # Non-fatal; proceed with API key auth only
                                        pass
                                    
                                    # Ready to proceed
                                    return True
                                else:
                                    progress.update(task, description="❌ Verification failed!")
                                    time.sleep(1)
                                    return False
                                        
                            except Exception as e:
                                progress.update(task, description=f"❌ Verification error: {e}")
                                time.sleep(1)
                                return False
                    elif response.status_code == 308:
                        # Permanent redirect - this shouldn't happen with follow_redirects=True
                        progress.update(task, description="⚠️  Redirect detected - retrying...")
                        time.sleep(1)
                        continue
                    elif response.status_code >= 400:
                        # HTTP error
                        if response.status_code == 404:
                            progress.update(task, description="❌ CLI linking endpoint not found!")
                        elif response.status_code == 403:
                            progress.update(task, description="⚠️  Access blocked - checking WAF/Cloudflare...")
                        else:
                            progress.update(task, description=f"⚠️  HTTP {response.status_code} error - retrying...")
                        
                        # Don't fail immediately on HTTP errors - might be temporary
                        time.sleep(2)
                        continue
                
            except KeyboardInterrupt:
                progress.update(task, description="❌ Cancelled by user!")
                time.sleep(0.5)
                return False
            except Exception as e:
                # Network error or other issue - continue polling
                # But provide some feedback for persistent errors
                error_str = str(e)
                if "525" in error_str or "SSL handshake failed" in error_str:
                    progress.update(task, description="⚠️  Backend SSL issue - retrying...")
                elif "timeout" in error_str.lower():
                    progress.update(task, description="⚠️  Network timeout - retrying...")
                else:
                    progress.update(task, description="⚠️  Network error - retrying...")
                # Continue polling despite errors
            
            # Wait before next poll
            time.sleep(poll_interval)
        
        # Timeout reached
        progress.update(task, description="⏰ Linking timeout!")
        time.sleep(0.5)
    
    return False
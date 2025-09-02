"""
Account and usage commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..client.api_client import IvyBloomAPIClient
from ..utils.printing import emit_json
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info

console = get_console()

@click.group()
def account():
    """👤 Account and usage management commands
    
    Monitor your IvyBloom account status, usage statistics, and billing information.
    
    ACCOUNT OVERVIEW:
      📊 View account details:     ivybloom account info
      📈 Usage statistics:         ivybloom account usage
      💳 Billing & plan info:      ivybloom account info --format json
      🔑 API key management:       Available at https://ivybiosciences.com/settings/api-keys
    
    MONITORING YOUR USAGE:
      • Track computational jobs per tool
      • Monitor API rate limits
      • View monthly usage against plan limits
      • Identify usage patterns and trends
    
    PLAN LIMITS:
      Each plan includes different limits for:
      • Jobs per month per tool (ESMFold, DiffDock, etc.)
      • API calls per minute/hour
      • Concurrent running jobs
      • Data storage and retention
    
    💡 TIP: Monitor your usage regularly to avoid hitting plan limits!
    
    Run 'ivybloom account <command> --help' for detailed help on each command.
    """
    pass

@account.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, format):
    """📋 Show comprehensive account information
    
    Display your account details including plan information, usage limits,
    and current month statistics.
    
    INFORMATION DISPLAYED:
      👤 Account Details:       Email, User ID, Account status
      💳 Plan Information:      Current plan type and features
      🔑 API Key Status:        Active keys and usage limits
      📊 Usage Overview:        Current month usage by tool
      📈 Usage Limits:          Monthly limits and remaining quotas
    
    USAGE:
      ivybloom account info                    # Formatted table view
      ivybloom account info --format json     # Raw JSON for scripting
    
    EXAMPLE OUTPUT:
      👤 Account Information
         Email: user@example.com
         Plan: Professional
         API Keys: 2/5
      
      📊 Current Month Usage
         esmfold: 15/1000
         diffdock: 8/500
      
      📈 Usage Limits
         esmfold: 15/1000 (1.5%)
         diffdock: 8/500 (1.6%)
    
    💡 TIP: Use --format json with tools like jq for custom processing!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            account_data = client.get_account_info()
        
        if format == 'json':
            emit_json(account_data)
        else:
            console.print(f"[bold cyan]👤 Account Information[/bold cyan]")
            console.print(f"   Email: {account_data.get('email', 'Unknown')}")
            console.print(f"   User ID: {account_data.get('user_id', 'Unknown')}")
            console.print(f"   Plan: {account_data.get('plan', 'Unknown')}")
            console.print(f"   API Keys: {account_data.get('api_keys_count', 0)}/{account_data.get('api_keys_limit', 'Unknown')}")
            
            usage = account_data.get('usage_current_month', {})
            if usage:
                console.print(f"\n[bold cyan]📊 Current Month Usage[/bold cyan]")
                for tool, count in usage.items():
                    console.print(f"   {tool}: {count}")
            
            limits = account_data.get('usage_limits', {})
            if limits:
                console.print(f"\n[bold cyan]📈 Usage Limits[/bold cyan]")
                for tool, limit in limits.items():
                    current = usage.get(tool, 0)
                    percentage = (current / limit * 100) if limit > 0 else 0
                    console.print(f"   {tool}: {current}/{limit} ({percentage:.1f}%)")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting account info: {e}[/red]")

@account.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.option('--tool', help='Filter usage statistics by specific tool')
@click.option('--period', default='month', type=click.Choice(['month', '30days', 'all']), help='Time period for statistics')
@click.pass_context
def usage(ctx, format, tool, period):
    """📈 Show detailed usage statistics and trends
    
    View comprehensive usage statistics across different time periods with
    breakdowns by tool, rate limits, and historical trends.
    
    STATISTICS INCLUDED:
      📅 Current Month:         Jobs run this billing period
      📊 Last 30 Days:          Rolling 30-day usage window
      🎯 Tool Breakdown:        Usage per computational tool
      ⚡ Rate Limits:          Current rate limiting status
      📈 Historical Summary:    Total lifetime usage stats
    
    TIME PERIODS:
      • month:    Current billing month (default)
      • 30days:   Rolling 30-day window
      • all:      Lifetime usage statistics
    
    USAGE:
      ivybloom account usage                           # Current month overview
      ivybloom account usage --tool esmfold          # ESMFold usage only
      ivybloom account usage --period 30days         # Rolling 30-day stats
      ivybloom account usage --format json           # Raw data for analysis
    
    EXAMPLE OUTPUT:
      📊 Usage Statistics
      
      Current Month:
      ┌─────────────┬──────┐
      │ Tool        │ Jobs │
      ├─────────────┼──────┤
      │ esmfold     │   15 │
      │ diffdock    │    8 │
      │ blast       │   42 │
      └─────────────┴──────┘
      
      Rate Limit Status:
         API calls: 1,250/10,000 per hour
         Concurrent jobs: 2/10
    
    💡 TIP: Track usage patterns to optimize your computational workflows!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Pass additional parameters to API if supported
            usage_data = client.get_usage_stats()
        
        # Filter by tool if specified
        if tool and format != 'json':
            # Filter usage data for specific tool
            filtered_data = {}
            for key, data_dict in usage_data.items():
                if isinstance(data_dict, dict) and tool in data_dict:
                    filtered_data[key] = {tool: data_dict[tool]}
                else:
                    filtered_data[key] = data_dict
            usage_data = filtered_data
        
        if format == 'json':
            emit_json(usage_data)
        else:
            console.print("[bold cyan]📊 Usage Statistics[/bold cyan]")
            
            if tool:
                console.print(f"[dim]Filtered for tool: [cyan]{tool}[/cyan][/dim]\n")
            
            # Show period-specific data
            period_data = None
            period_title = None
            
            if period == 'month':
                period_data = usage_data.get('current_month', {})
                period_title = "Current Month"
            elif period == '30days':
                period_data = usage_data.get('last_30_days', {})
                period_title = "Last 30 Days"
            elif period == 'all':
                period_data = usage_data.get('all_time', usage_data.get('current_month', {}))
                period_title = "All Time"
            
            if period_data:
                console.print(f"\n[bold]{period_title}:[/bold]")
                table = Table()
                table.add_column("Tool", style="cyan")
                table.add_column("Jobs", style="green", justify="right")
                
                # Sort tools by usage count (descending)
                sorted_tools = sorted(period_data.items(), key=lambda x: x[1], reverse=True)
                for tool_name, count in sorted_tools:
                    if not tool or tool == tool_name:
                        table.add_row(tool_name, str(count))
                
                console.print(table)
            
            # Always show additional periods unless filtered by tool
            if not tool:
                # Current month (if not already shown)
                if period != 'month':
                    current_month = usage_data.get('current_month', {})
                    if current_month:
                        console.print("\n[bold]Current Month:[/bold]")
                        table = Table()
                        table.add_column("Tool", style="cyan")
                        table.add_column("Jobs", style="green", justify="right")
                        
                        sorted_tools = sorted(current_month.items(), key=lambda x: x[1], reverse=True)
                        for tool_name, count in sorted_tools:
                            table.add_row(tool_name, str(count))
                        
                        console.print(table)
                
                # Last 30 days (if not already shown)
                if period != '30days':
                    last_30_days = usage_data.get('last_30_days', {})
                    if last_30_days:
                        console.print("\n[bold]Last 30 Days:[/bold]")
                        table = Table()
                        table.add_column("Tool", style="cyan")
                        table.add_column("Jobs", style="green", justify="right")
                        
                        sorted_tools = sorted(last_30_days.items(), key=lambda x: x[1], reverse=True)
                        for tool_name, count in sorted_tools:
                            table.add_row(tool_name, str(count))
                        
                        console.print(table)
            
            # Summary stats
            total_jobs = usage_data.get('total_jobs', 0)
            total_api_calls = usage_data.get('total_api_calls', 0)
            if total_jobs > 0 or total_api_calls > 0:
                console.print(f"\n[bold]📈 Summary:[/bold]")
                if total_jobs > 0:
                    console.print(f"   Total Jobs: [green]{total_jobs:,}[/green]")
                if total_api_calls > 0:
                    console.print(f"   Total API Calls: [blue]{total_api_calls:,}[/blue]")
            
            # Rate limit status
            rate_limit = usage_data.get('rate_limit_status', {})
            if rate_limit:
                console.print(f"\n[bold]⚡ Rate Limit Status:[/bold]")
                for limit_type, info in rate_limit.items():
                    console.print(f"   {limit_type}: [yellow]{info}[/yellow]")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting usage stats: {e}[/red]")
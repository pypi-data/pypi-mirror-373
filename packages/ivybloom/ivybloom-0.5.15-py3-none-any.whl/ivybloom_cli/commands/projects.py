"""
Project management commands for IvyBloom CLI
"""

import click
import json
from typing import Dict, Any
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..client.api_client import IvyBloomAPIClient
from ..utils.printing import emit_json
from ..utils.colors import get_console

console = get_console()

@click.group()
def projects():
    """📁 Project organization and management
    
    Organize your computational jobs into projects for better workflow management.
    
    PROJECT BENEFITS:
      🗂️  Organization: Group related jobs together
      👥 Collaboration: Share projects with team members
      📊 Analytics: Track project-level progress and usage
      🔒 Access Control: Manage permissions per project
    
    COMMON WORKFLOWS:
    
      📋 View projects:        ivybloom projects list
      ℹ️  Project details:     ivybloom projects info <project_id>
      📊 Project jobs:         ivybloom projects jobs <project_id>
      🚀 Run job in project:   ivybloom run esmfold --project-id <id> [params...]
    
    PROJECT ORGANIZATION:
      • Drug Discovery Pipeline → esmfold, diffdock, admetlab3 jobs
      • Protein Analysis Study → blast, esmfold, structural analysis jobs  
      • Compound Optimization → reinvent, protox3, deepsol jobs
    
    💡 TIP: Use projects to keep your computational workflows organized!
    
    Run 'ivybloom projects <command> --help' for detailed help on each command.
    """
    pass

@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode with project selection')
@click.pass_context
def list(ctx, format, interactive):
    """📋 List all your projects
    
    View all projects you have access to, including job counts and activity.
    
    USAGE:
      ivybloom projects list                # Table view (default)
      ivybloom projects list --format json # JSON for automation
      ivybloom projects list --interactive  # Interactive selection mode
    
    PROJECT INFO SHOWN:
      • Project ID and name
      • Description and purpose
      • Number of jobs in project
      • Creation date
      • Last activity timestamp
    
    NEXT STEPS:
      • View project details:  ivybloom projects info <project_id>
      • See project jobs:      ivybloom projects jobs <project_id>
      • Add job to project:    ivybloom run <tool> --project-id <id>
    
    INTERACTIVE MODE:
      --interactive, -i  # Select projects with numbered selection for actions
    
    💡 TIP: Use --interactive to easily select projects and perform actions!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        # Ensure non-zero exit and stderr output so JSON consumers aren't polluted
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            projects_data = client.list_projects()
        
        if format == 'json':
            emit_json(projects_data)
        else:
            if not projects_data:
                console.print("[yellow]No projects found[/yellow]")
                return
            
            table = Table(title=f"📁 Projects ({len(projects_data)} found)")
            table.add_column("Project ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Description", style="blue")
            table.add_column("Jobs", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Last Activity", style="dim")
            
            for project in projects_data:
                # Handle both project_id and id field names
                project_id = project.get('project_id') or project.get('id', '')
                description = project.get('description', '')[:30] + ('...' if len(project.get('description', '')) > 30 else '') if project.get('description') else 'No description'
                
                table.add_row(
                    str(project_id)[:8] + '...' if project_id else 'N/A',
                    project.get('name', 'Unnamed'),
                    description,
                    str(project.get('job_count', 0)),
                    project.get('created_at', '')[:10] if project.get('created_at') else 'Unknown',
                    project.get('last_activity', 'Never')[:10] if project.get('last_activity') else 'Never'
                )
            
            console.print(table)
            
            # Interactive mode - let user select a project
            if interactive:
                from ..utils.interactive import select_from_list, select_project_action
                
                # Prepare projects for selection
                project_items = []
                for project in projects_data:
                    project_id = project.get('project_id') or project.get('id', '')
                    project_name = project.get('name', 'Untitled')
                    description = project.get('description', '')
                    job_count = project.get('job_count', 0)
                    
                    desc_text = f"Jobs: {job_count}"
                    if description:
                        desc_text += f" | {description}"
                    
                    project_items.append({
                        'id': project_id,
                        'name': project_name,
                        'description': desc_text,
                        'project_data': project
                    })
                
                # Let user select a project
                selected_project_id = select_from_list(
                    items=project_items,
                    title="Select a Project",
                    display_key='name',
                    id_key='id',
                    description_key='description'
                )
                
                if selected_project_id:
                    # Find the selected project data
                    selected_project_data = None
                    for item in project_items:
                        if item['id'] == selected_project_id:
                            selected_project_data = item['project_data']
                            break
                    
                    if selected_project_data:
                        # Let user select an action
                        action = select_project_action(selected_project_data)
                        
                        if action:
                            _execute_project_action(ctx, selected_project_id, action, selected_project_data)
    
    except Exception as e:
        # Provide actionable, user-friendly error messages
        msg = str(e)
        hints = []
        if "Not authenticated" in msg or "Authentication" in msg or "401" in msg:
            hints.append("Run 'ivybloom auth status' to verify login and API key")
            hints.append("If needed, run 'ivybloom auth login --link' to relink this CLI")
        if "Unexpected response" in msg:
            hints.append("The server returned an unexpected format. Try again in a moment")
            hints.append("Run with --debug for request/response details")
        if "timeout" in msg.lower():
            hints.append("Network timeout. Check your connection and try again")
        if not hints:
            hints.append("Re-run with '--debug' to see request/response diagnostics")
        hint_text = "\n".join(f"   • {h}" for h in hints)
        raise click.ClickException(f"Error listing projects: {msg}\n\nTroubleshooting:\n{hint_text}")

@projects.command()
@click.argument('project_id')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, project_id, format):
    """ℹ️  Get detailed project information
    
    View comprehensive details about a specific project including metadata,
    job statistics, and recent activity.
    
    USAGE:
      ivybloom projects info <project_id>           # Detailed view
      ivybloom projects info <project_id> --format json  # JSON output
    
    PROJECT DETAILS SHOWN:
      • Project metadata (name, description, dates)
      • Job statistics (total, by status, by tool)
      • Recent activity and usage patterns
      • Team members and permissions (if applicable)
      • Resource usage and costs (if available)
    
    RELATED COMMANDS:
      • View project jobs:     ivybloom projects jobs <project_id>
      • Filter global jobs:    ivybloom jobs list --project-id <project_id>
    
    💡 TIP: Use this to understand project scope and activity before diving in!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            project_data = client.get_project(project_id)
        
        if format == 'json':
            emit_json(project_data)
        else:
            # Handle both project_id and id field names
            project_id = project_data.get('project_id') or project_data.get('id', 'Unknown')
            
            console.print(f"[bold cyan]📁 {project_data.get('name', 'Unnamed Project')}[/bold cyan]")
            console.print(f"   Project ID: {project_id}")
            console.print(f"   Description: {project_data.get('description', 'No description')}")
            console.print(f"   Created: {project_data.get('created_at', 'Unknown')}")
            console.print(f"   Updated: {project_data.get('updated_at', 'Unknown')}")
            console.print(f"   Jobs: {project_data.get('job_count', 0)}")
            console.print(f"   Last Activity: {project_data.get('last_activity', 'Never')}")
    
    except Exception as e:
        raise click.ClickException(f"Error getting project info: {e}")

@projects.command()
@click.argument('project_id')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def jobs(ctx, project_id, format):
    """📊 List all jobs in a specific project
    
    View all computational jobs associated with a particular project,
    showing status, progress, and results.
    
    USAGE:
      ivybloom projects jobs <project_id>              # Project job list
      ivybloom projects jobs <project_id> --format json  # JSON output
    
    JOB INFORMATION SHOWN:
      • Job ID and title
      • Tool/algorithm used  
      • Current status and progress
      • Creation and completion times
      • Links to detailed status and results
    
    PROJECT WORKFLOW:
      1. List project jobs:    ivybloom projects jobs <project_id>
      2. Check job status:     ivybloom jobs status <job_id>
      3. Get results:          ivybloom jobs results <job_id>
      4. Add more jobs:        ivybloom run <tool> --project-id <project_id>
    
    💡 TIP: This gives you a project-focused view of your computational pipeline!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            jobs_data = client.list_project_jobs(project_id)
        
        if format == 'json':
            emit_json(jobs_data)
        else:
            if not jobs_data:
                console.print(f"[yellow]No jobs found for project {project_id}[/yellow]")
                return
            
            table = Table(title=f"📋 Project Jobs ({len(jobs_data)} found)")
            table.add_column("Job ID", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Tool", style="green")
            table.add_column("Created", style="dim")
            
            for job in jobs_data:
                # Map database status values to display values (same as in jobs.py)
                status_display = {
                    'COMPLETED': '[green]COMPLETED[/green]',
                    'SUCCESS': '[green]SUCCESS[/green]',
                    'PROCESSING': '[blue]PROCESSING[/blue]',
                    'STARTED': '[blue]RUNNING[/blue]',
                    'FAILURE': '[red]FAILED[/red]',
                    'failed': '[red]FAILED[/red]',
                    'PENDING': '[yellow]PENDING[/yellow]',
                    'submitted': '[yellow]SUBMITTED[/yellow]',
                    'CANCELLED': '[dim]CANCELLED[/dim]',
                    'ARCHIVED': '[dim]ARCHIVED[/dim]'
                }.get(job.get('status', ''), job.get('status', ''))
                
                # Handle both job_id and id field names
                job_id = job.get('job_id') or job.get('id', '')
                
                table.add_row(
                    str(job_id)[:8] + '...' if job_id else 'N/A',
                    status_display,
                    job.get('job_type', ''),  # Use job_type instead of tool_name
                    job.get('created_at', '')[:16] if job.get('created_at') else ''
                )
            
            console.print(table)
    
    except Exception as e:
        raise click.ClickException(f"Error listing project jobs: {e}")

def _execute_project_action(ctx, project_id: str, action: str, project_data: Dict[str, Any]):
    """Execute the selected action on a project"""
    try:
        if action == 'info':
            # Show project info
            info(ctx, project_id, 'table')
            
        elif action == 'jobs':
            # Show project jobs
            jobs(ctx, project_id, 'table')
            
        elif action == 'create_job':
            # Help user create a job in this project
            from ..utils.interactive import select_from_list
            
            # Show available tools (simplified)
            console.print(f"\n[cyan]Creating a job in project {project_id}...[/cyan]")
            console.print("First, choose a computational tool:")
            console.print()
            
            # Common tools for quick selection
            common_tools = [
                {'id': 'esmfold', 'name': 'ESMFold', 'description': 'Protein structure prediction (5 min)'},
                {'id': 'diffdock', 'name': 'DiffDock', 'description': 'Molecular docking (30 min)'},
                {'id': 'reinvent', 'name': 'REINVENT', 'description': 'Drug design (1 hour)'},
                {'id': 'admetlab3', 'name': 'ADMETLab3', 'description': 'ADMET analysis (10 min)'},
                {'id': 'blast', 'name': 'BLAST', 'description': 'Sequence search (2 min)'},
                {'id': 'other', 'name': 'Other Tool', 'description': 'See all available tools'}
            ]
            
            selected_tool = select_from_list(
                items=common_tools,
                title="Select a Tool",
                display_key='name',
                id_key='id',
                description_key='description'
            )
            
            if selected_tool:
                if selected_tool == 'other':
                    console.print("\n[cyan]💡 To see all available tools:[/cyan]")
                    console.print("   ivybloom tools list")
                    console.print("\n[cyan]💡 To run any tool in this project:[/cyan]")
                    console.print(f"   ivybloom run <tool_name> --project-id {project_id} [parameters...]")
                else:
                    console.print(f"\n[cyan]💡 To run {selected_tool} in this project:[/cyan]")
                    console.print(f"   ivybloom run {selected_tool} --project-id {project_id} [parameters...]")
                    console.print(f"\n[cyan]💡 To see {selected_tool} parameters:[/cyan]")
                    console.print(f"   ivybloom tools schema {selected_tool} --examples")
                
    except Exception as e:
        console.print(f"[red]❌ Error executing action '{action}': {e}[/red]")
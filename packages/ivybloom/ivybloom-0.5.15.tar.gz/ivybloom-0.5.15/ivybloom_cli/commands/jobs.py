"""
Job management commands for IvyBloom CLI
"""

import click
import time
import json
import requests
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
try:
    import humanize as _humanize
except Exception:
    _humanize = None
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.panel import Panel

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, get_status_color, format_status_icon, print_success, print_error, print_warning, print_info
from ..client.api_client import IvyBloomAPIClient
from ..utils.printing import emit_json

console = get_console()

@click.group()
def jobs():
    """Manage and monitor computational jobs

    Common:
      - List:    ivybloom jobs list [--status running --tool esmfold]
      - Status:  ivybloom jobs status <job_id> [--follow]
      - Results: ivybloom jobs results <job_id>
      - Download:ivybloom jobs download <job_id>

    Tip: Use '--follow' to watch long-running jobs live.
    """
    pass

@jobs.command()
@click.option('--project-id', help='Filter by project ID')
@click.option('--status', help='Filter by job status (pending, running, completed, failed, cancelled)')
@click.option('--tool', help='Filter by tool/job type')
@click.option('--limit', default=50, help='Number of jobs to return')
@click.option('--offset', default=0, help='Number of jobs to skip')
@click.option('--created-after', help='Filter jobs created after date (ISO format)')
@click.option('--created-before', help='Filter jobs created before date (ISO format)')
@click.option('--sort-by', default='created_at', type=click.Choice(['created_at', 'status', 'job_type']), help='Sort jobs by field')
@click.option('--sort-order', default='desc', type=click.Choice(['asc', 'desc']), help='Sort order')
@click.option('--format', default='table', type=click.Choice(['table', 'json', 'csv', 'yaml']), help='Output format')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode with job selection')
@click.pass_context
def list(ctx, project_id, status, tool, limit, offset, created_after, created_before, sort_by, sort_order, format, interactive):
    """📋 List and filter your computational jobs
    
    View your job history with powerful filtering and sorting options.
    
    COMMON USAGE:
      ivybloom jobs list                           # Recent jobs
      ivybloom jobs list --status running         # Active jobs only
      ivybloom jobs list --tool esmfold           # Filter by tool
      ivybloom jobs list --project-id <id>        # Filter by project
      ivybloom jobs list --limit 5                # Last 5 jobs
      ivybloom jobs list --interactive            # Interactive selection mode
    
    ADVANCED FILTERING:
      ivybloom jobs list --status failed --created-after 2025-01-01
      ivybloom jobs list --tool reinvent --sort-by created_at --sort-order asc
    
    OUTPUT FORMATS:
      --format table     # Human-readable (default)
      --format json      # For scripts and automation
      --format csv       # For spreadsheets  
      --format yaml      # Structured data
    
    INTERACTIVE MODE:
      --interactive, -i  # Select jobs with arrow keys for actions
    
    💡 TIP: Use --interactive to easily select jobs and perform actions!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        # Build filters
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if status:
            filters['status'] = status
        if tool:
            filters['tool_name'] = tool  # This will be mapped to job_type in api_client
        if created_after:
            filters['created_after'] = created_after
        if created_before:
            filters['created_before'] = created_before
        if limit:
            filters['limit'] = limit
        if offset:
            filters['offset'] = offset
        
        with IvyBloomAPIClient(config, auth_manager) as client:
            jobs_data = client.list_jobs(**filters)
        
        if format == 'json':
            emit_json(jobs_data)
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(jobs_data, default_flow_style=False))
        elif format == 'csv':
            # Simple CSV output
            if jobs_data:
                headers = jobs_data[0].keys()
                console.print(','.join(headers))
                for job in jobs_data:
                    console.print(','.join(str(job.get(h, '')) for h in headers))
        else:
            # Table format (default)
            if not jobs_data:
                console.print("[yellow]No jobs found[/yellow]")
                return
            
            table = Table(title=f"📋 Jobs ({len(jobs_data)} found)")
            table.add_column("Job ID", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Type", style="green")
            table.add_column("Title", style="blue")
            table.add_column("Progress", style="yellow")
            table.add_column("Created", style="dim")
            table.add_column("Project", style="blue")
            
            for job in jobs_data:
                # Handle both API response formats (job_id/id, tool_name/job_type, etc.)
                job_id = job.get('job_id') or job.get('id', '')
                job_type = job.get('tool_name') or job.get('job_type', '')
                progress = job.get('progress_percentage') or job.get('progress_percent', 0)
                
                # Map database status values to display values
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
                
                progress_display = f"{progress}%" if progress is not None else "N/A"
                job_title = job.get('job_title', 'Untitled') or 'Untitled'
                title_display = job_title[:20] + ('...' if len(job_title) > 20 else '')
                
                table.add_row(
                    str(job_id)[:8] + '...' if job_id else 'N/A',
                    status_display,
                    job_type,
                    title_display,
                    progress_display,
                    job.get('created_at', '')[:16] if job.get('created_at') else '',
                    str(job.get('project_id', ''))[:8] + '...' if job.get('project_id') else 'None'
                )
            
            console.print(table)
            
            # Interactive mode - let user select a job
            if interactive:
                from ..utils.interactive import select_from_list, select_job_action
                
                # Prepare jobs for selection
                job_items = []
                for job in jobs_data:
                    job_id = job.get('job_id') or job.get('id', '')
                    job_type = job.get('tool_name') or job.get('job_type', '')
                    job_title = job.get('job_title', 'Untitled')
                    status = job.get('status', 'Unknown')
                    
                    display_name = f"{job_type} - {job_title}"
                    if len(display_name) > 40:
                        display_name = display_name[:37] + "..."
                    
                    job_items.append({
                        'id': job_id,
                        'name': display_name,
                        'description': f"Status: {status}",
                        'job_data': job
                    })
                
                # Let user select a job
                selected_job_id = select_from_list(
                    items=job_items,
                    title="Select a Job",
                    display_key='name',
                    id_key='id',
                    description_key='description'
                )
                
                if selected_job_id:
                    # Find the selected job data
                    selected_job_data = None
                    for item in job_items:
                        if item['id'] == selected_job_id:
                            selected_job_data = item['job_data']
                            break
                    
                    if selected_job_data:
                        # Let user select an action
                        action = select_job_action(selected_job_data)
                        
                        if action:
                            _execute_job_action(ctx, selected_job_id, action, selected_job_data)
    
    except Exception as e:
        console.print(f"[red]❌ Error listing jobs: {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.option('--follow', '-f', is_flag=True, help='Follow job progress')
@click.option('--interval', default=5, show_default=True, type=int, help='Polling interval in seconds for --follow')
@click.option('--logs', is_flag=True, help='Include execution logs')
@click.option('--logs-tail', type=int, default=50, show_default=True, help='When --logs is set, include only the last N log lines')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def status(ctx, job_id, follow, interval, logs, logs_tail, format):
    """📊 Monitor job status and progress
    
    Check the current status, progress, and details of a specific job.
    
    USAGE:
      ivybloom jobs status <job_id>                # One-time status check
      ivybloom jobs status <job_id> --follow      # Live progress monitoring
      ivybloom jobs status <job_id> --logs        # Include execution logs
      ivybloom jobs status <job_id> --format json # JSON output
    
    LIVE MONITORING:
      The --follow flag provides real-time updates showing:
      • Current status and progress percentage
      • Processing phase information  
      • Estimated completion time
      • Recent log entries (with --logs)
    
    STATUS MEANINGS:
      🟡 PENDING     → Job queued, waiting to start
      🔵 PROCESSING  → Job actively running
      🟢 COMPLETED   → Job finished successfully  
      🔴 FAILED      → Job encountered an error
      ⚫ CANCELLED   → Job was cancelled by user
    
    💡 TIP: Use --follow to watch long-running jobs without manual refresh!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            if follow:
                # Follow mode - continuously update status
                with Live(console=console, refresh_per_second=2) as live:
                    while True:
                        job_data = client.get_job_status(job_id, include_logs=logs, logs_tail=logs_tail if logs else None)
                        
                        # Create status display
                        status_panel = _create_status_panel(job_data)
                        live.update(status_panel)
                        
                        # Check if job is complete (handle both database and CLI status values)
                        status = job_data.get('status', '').upper()
                        if status in ['COMPLETED', 'SUCCESS', 'FAILURE', 'FAILED', 'CANCELLED', 'ARCHIVED']:
                            break
                        
                        time.sleep(max(1, int(interval)))  # Adjustable polling interval
            else:
                # Single status check
                job_data = client.get_job_status(job_id, include_logs=logs, logs_tail=logs_tail if logs else None)
                
                if format == 'json':
                    emit_json(job_data)
                else:
                    status_panel = _create_status_panel(job_data)
                    console.print(status_panel)
    
    except Exception as e:
        console.print(f"[red]❌ Error getting job status: {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.option('--format', default='json', type=click.Choice(['json', 'yaml', 'csv']), help='Output format')
@click.option('--output', '-o', help='Save to file')
@click.pass_context
def results(ctx, job_id, format, output):
    """📁 Download and view job results
    
    Retrieve the results from a completed computational job.
    
    USAGE:
      ivybloom jobs results <job_id>                    # View results  
      ivybloom jobs results <job_id> -o results.json   # Save to file
      ivybloom jobs results <job_id> --format yaml     # YAML format
    
    RESULT FORMATS:
      --format json     # Structured data (default)
      --format yaml     # Human-readable structured format
      --format csv      # Tabular data for analysis
    
    SAVE OPTIONS:  
      -o, --output FILE # Save results to specified file
      
    RESULT CONTENTS:
      • Computational outputs (structures, scores, predictions)
      • Analysis summaries and statistics
      • Generated files and data
      • Metadata (parameters used, runtime, etc.)
    
    💡 TIP: Results are only available for completed jobs. Check status first!
    
    FOR FILE DOWNLOADS:
      Use 'ivybloom jobs download <job_id>' to download actual result files
      like PDB structures, ZIP archives, and other computational artifacts.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            results_data = client.get_job_results(job_id, format=format)
        
        if output:
            # Save to file
            with open(output, 'w') as f:
                if format == 'json':
                    json.dump(results_data, f, indent=2)
                else:
                    f.write(str(results_data))
            console.print(f"[green]✅ Results saved to {output}[/green]")
        else:
            # Print to console
            if format == 'json':
                emit_json(results_data)
            else:
                console.print(results_data)
        
        # Suggest download command only when not printing JSON to stdout
        if format != 'json' and not output:
            console.print(f"\n[dim]💡 To download result files (PDB, ZIP, etc.), use:[/dim]")
            console.print(f"[dim]   ivybloom jobs download {job_id}[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Error getting job results: {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.option('--artifact-type', help='Specific artifact type to download (pdb, zip, csv, txt, sdf)')
@click.option('--output-dir', '-d', help='Directory to save downloaded files', default='.')
@click.option('--list-only', is_flag=True, help='List available artifacts without downloading')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format for --list-only')
@click.pass_context
def download(ctx, job_id, artifact_type, output_dir, list_only, format):
    """📥 Download job artifacts and results
    
    Download computational results and artifacts from completed jobs.
    
    USAGE:
      ivybloom jobs download <job_id>                    # Download all artifacts
      ivybloom jobs download <job_id> --artifact-type pdb  # Download specific type
      ivybloom jobs download <job_id> -d ~/Downloads     # Custom output directory
      ivybloom jobs download <job_id> --list-only        # List available artifacts
    
    SUPPORTED ARTIFACT TYPES:
      • pdb       - Protein structure files (.pdb)
      • zip       - Compressed archives (.zip)
      • csv       - Data files (.csv)
      • txt       - Text/log files (.txt, .log)
      • sdf       - Structure data files (.sdf)
      • primary   - Main result file (auto-detects type)
    
    DOWNLOAD PROCESS:
      1. Fetches presigned URLs from IvyBloom API
      2. Downloads files directly from secure storage
      3. Saves with original filenames to specified directory
      4. Shows progress and file information
    
    💡 TIP: Use --list-only first to see what artifacts are available!
    """
    import os
    from pathlib import Path
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            download_data = client.get_job_download_urls(job_id, artifact_type)
        
        if list_only:
            # Just show available artifacts
            if format == 'json':
                emit_json(download_data)
                return
            
            # Table format
            console.print(f"[bold cyan]📥 Available Artifacts for Job {job_id[:8]}...[/bold cyan]")
            console.print(f"[cyan]Job Status:[/cyan] {download_data.get('job_status')}")
            console.print(f"[cyan]Job Type:[/cyan] {download_data.get('job_type')}")
            console.print(f"[cyan]Total Artifacts:[/cyan] {download_data.get('total_artifacts', 0)}")
            console.print()
            
            if not download_data.get('artifacts'):
                console.print("[yellow]No downloadable artifacts found for this job.[/yellow]")
                return
            
            from rich.table import Table
            table = Table(title="Available Artifacts")
            table.add_column("Type", style="green")
            table.add_column("Filename", style="blue")
            table.add_column("Size", style="yellow")
            table.add_column("Expires", style="dim")
            
            for artifact in download_data['artifacts']:
                file_size = artifact.get('file_size', 0)
                size_str = _format_file_size(file_size) if file_size else 'Unknown'
                expires_str = f"{artifact.get('expires_in', 3600)}s"
                
                table.add_row(
                    artifact.get('artifact_type', 'unknown'),
                    artifact.get('filename', 'unknown'),
                    size_str,
                    expires_str
                )
            
            console.print(table)
            console.print(f"\n[dim]💡 Run without --list-only to download these artifacts[/dim]")
            return
        
        # Download artifacts
        artifacts = download_data.get('artifacts', [])
        if not artifacts:
            console.print("[yellow]No downloadable artifacts found for this job.[/yellow]")
            return
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        console.print(f"[cyan]📥 Downloading {len(artifacts)} artifact(s) to {output_path.absolute()}[/cyan]")
        
        downloaded_files = []
        failed_downloads = []
        
        for i, artifact in enumerate(artifacts, 1):
            artifact_type_display = artifact.get('artifact_type', 'unknown')
            filename = artifact.get('filename', f'artifact_{i}')
            presigned_url = artifact.get('presigned_url')
            file_size = artifact.get('file_size', 0)
            
            console.print(f"\n[blue]{i}/{len(artifacts)}[/blue] Downloading {artifact_type_display}: [green]{filename}[/green]")
            
            if not presigned_url:
                console.print(f"[red]  ❌ No download URL available[/red]")
                failed_downloads.append(filename)
                continue
            
            try:
                # Download the file
                response = requests.get(presigned_url, stream=True)
                response.raise_for_status()
                
                file_path = output_path / filename
                total_size = file_size or int(response.headers.get('content-length', 0))
                
                with open(file_path, 'wb') as f:
                    if total_size > 0:
                        # Show progress for larger files
                        from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn
                        with Progress(
                            TextColumn("[progress.description]{task.description}"),
                            BarColumn(),
                            DownloadColumn(),
                            TransferSpeedColumn(),
                            console=console
                        ) as progress:
                            task = progress.add_task(f"  {filename}", total=total_size)
                            
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    progress.update(task, advance=len(chunk))
                    else:
                        # Simple download for small files
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                
                actual_size = file_path.stat().st_size
                console.print(f"  [green]✅ Downloaded {_format_file_size(actual_size)}[/green]")
                downloaded_files.append(str(file_path))
                
            except Exception as e:
                console.print(f"  [red]❌ Download failed: {e}[/red]")
                failed_downloads.append(filename)
        
        # Summary
        console.print(f"\n[bold green]📥 Download Summary[/bold green]")
        console.print(f"  Successful: {len(downloaded_files)}")
        console.print(f"  Failed: {len(failed_downloads)}")
        
        if downloaded_files:
            console.print(f"\n[bold]Downloaded files:[/bold]")
            for file_path in downloaded_files:
                console.print(f"  • [green]{file_path}[/green]")
        
        if failed_downloads:
            console.print(f"\n[bold red]Failed downloads:[/bold red]")
            for filename in failed_downloads:
                console.print(f"  • [red]{filename}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error downloading job artifacts: {e}[/red]")

def _format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def _execute_job_action(ctx, job_id: str, action: str, job_data: Dict[str, Any]):
    """Execute the selected action on a job"""
    from ..utils.interactive import confirm_action
    
    try:
        if action == 'status':
            # Show job status
            status(ctx, job_id, False, False, 'table')
            
        elif action == 'follow':
            # Monitor job live
            status(ctx, job_id, True, False, 'table')
            
        elif action == 'results':
            # Show job results
            results(ctx, job_id, 'json', None)
            
        elif action == 'download':
            # Download job artifacts
            download(ctx, job_id, None, '.', False, 'table')
            
        elif action == 'cancel':
            # Cancel job with confirmation
            if confirm_action(f"Are you sure you want to cancel job {job_id[:8]}...?", False):
                cancel(ctx, job_id)
            else:
                console.print("[yellow]Job cancellation cancelled.[/yellow]")
                
    except Exception as e:
        console.print(f"[red]❌ Error executing action '{action}': {e}[/red]")

@jobs.command()
@click.argument('job_id')
@click.pass_context
def cancel(ctx, job_id):
    """Cancel a running job"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    if not click.confirm(f"Are you sure you want to cancel job {job_id}?"):
        console.print("Cancelled.")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            result = client.cancel_job(job_id)
        
        console.print(f"[green]✅ Job {job_id} cancelled successfully[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Error cancelling job: {e}[/red]")

def _create_status_panel(job_data: dict) -> Panel:
    """Create a rich panel for job status display"""
    # Handle both API response formats (job_id/id, tool_name/job_type, etc.)
    job_id = job_data.get('job_id') or job_data.get('id', 'Unknown')
    status = job_data.get('status', 'Unknown')
    job_type = job_data.get('tool_name') or job_data.get('job_type', 'Unknown')
    job_title = job_data.get('job_title', 'Untitled')
    progress = job_data.get('progress_percentage') or job_data.get('progress_percent', 0)
    current_phase = job_data.get('current_phase', 'N/A')
    
    # Status styling with correct database values
    # Status styles matching API specification (CLI → Database conversion)
    status_styles = {
        # Database statuses (what API returns)
        'PENDING': '[yellow]PENDING ⏳[/yellow]',
        'PROCESSING': '[blue]PROCESSING 🔄[/blue]',
        'COMPLETED': '[green]COMPLETED ✅[/green]',
        'SUCCESS': '[green]SUCCESS ✅[/green]',
        'FAILURE': '[red]FAILED ❌[/red]',
        'CANCELLED': '[dim]CANCELLED ⏹️[/dim]',
        'ARCHIVED': '[dim]ARCHIVED 📦[/dim]',
        # Legacy/mixed case support for backward compatibility
        'pending': '[yellow]PENDING ⏳[/yellow]',
        'running': '[blue]PROCESSING 🔄[/blue]',
        'completed': '[green]COMPLETED ✅[/green]',
        'success': '[green]SUCCESS ✅[/green]',
        'failed': '[red]FAILED ❌[/red]',
        'cancelled': '[dim]CANCELLED ⏹️[/dim]',
        'STARTED': '[blue]PROCESSING 🔄[/blue]',  # Legacy support
        'submitted': '[yellow]PENDING ⏳[/yellow]'  # Legacy support
    }
    
    styled_status = status_styles.get(status, status)
    
    # Build content
    content = f"""[bold cyan]Job ID:[/bold cyan] {job_id}
[bold cyan]Title:[/bold cyan] {job_title}
[bold cyan]Type:[/bold cyan] {job_type}
[bold cyan]Status:[/bold cyan] {styled_status}
[bold cyan]Progress:[/bold cyan] {progress}%
[bold cyan]Current Phase:[/bold cyan] {current_phase}"""
    
    if job_data.get('processing_started_at'):
        content += f"\n[bold cyan]Started:[/bold cyan] {job_data['processing_started_at']}"
    
    if job_data.get('completed_at'):
        content += f"\n[bold cyan]Completed:[/bold cyan] {job_data['completed_at']}"
    
    if job_data.get('error_message'):
        content += f"\n[bold red]Error:[/bold red] {job_data['error_message']}"
    
    if job_data.get('logs'):
        content += f"\n\n[bold cyan]Recent Logs:[/bold cyan]"
        # Split logs by newlines and show last few lines
        log_lines = job_data['logs'].split('\n')[-5:] if job_data['logs'] else []
        for log_line in log_lines:
            if log_line.strip():
                content += f"\n[dim]{log_line.strip()}[/dim]"
    
    # Determine border color based on status
    border_color = "blue"
    if status in ['PROCESSING', 'STARTED']:
        border_color = "blue"
    elif status in ['COMPLETED', 'SUCCESS']:
        border_color = "green"
    elif status in ['FAILURE', 'failed']:
        border_color = "red"
    elif status in ['CANCELLED', 'ARCHIVED']:
        border_color = "dim"
    
    return Panel(
        content,
        title="📊 Job Status",
        border_style=border_color
    )
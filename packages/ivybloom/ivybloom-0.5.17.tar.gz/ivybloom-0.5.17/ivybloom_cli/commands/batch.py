"""
Batch operations for IvyBloom CLI
"""

import click
import json
import yaml
import time
from typing import Dict, Any, List, Union
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ..client.api_client import IvyBloomAPIClient
from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info
from ..utils.printing import emit_json

console = get_console()

@click.group()
@click.pass_context
def batch(ctx):
    """High-throughput job submission (WIP)

    - Submit:  ivybloom batch submit <file.yaml> [--wait] [--max-concurrent N]
    - Cancel:  ivybloom batch cancel <job_id...>
    - Results: ivybloom batch results <job_id...> [--output-dir dir] [--format json|yaml|table]

    Notes:
      - Batch files (YAML/JSON) define a list of jobs and optional dependencies.
      - Use --dry-run to preview submissions without running.
    """
    pass

@batch.command()
@click.argument('job_file', type=click.Path(exists=True))
@click.option('--project-id', help='Project ID for all jobs (overrides file setting)')
@click.option('--batch-title', help='Title for the batch (overrides file setting)')
@click.option('--dry-run', is_flag=True, help='Preview jobs without submitting')
@click.option('--max-concurrent', default=10, help='Maximum concurrent jobs (default: 10)')
@click.option('--wait', is_flag=True, help='Wait for all jobs to complete')
@click.pass_context
def submit(ctx, job_file: str, project_id: str, batch_title: str, dry_run: bool, max_concurrent: int, wait: bool):
    """🚀 Submit multiple jobs from a batch definition file
    
    Execute many computational jobs efficiently using structured YAML or JSON 
    configuration files. Perfect for parameter sweeps and high-throughput studies.
    
    BATCH FILE STRUCTURE:
    
      ```yaml
      # Batch metadata (optional)
      batch:
        title: "Drug Screening Study"
        description: "Screening 1000 compounds against COVID target"
        project_id: "proj_abc123"
        tags: ["screening", "covid", "drugs"]
      
      # Job definitions (required)  
      jobs:
        - tool: esmfold
          title: "Fold Target Protein"
          parameters:
            protein_sequence: "MKLLVLGLV..."
            
        - tool: diffdock
          title: "Dock Compound {compound_id}"  # Template variables supported
          parameters:
            protein_pdb: "{previous_job_output}"  # Reference other job outputs
            ligand_smiles: "CCO"
            
        - tool: admetlab3
          title: "ADMET Analysis"
          parameters:
            smiles: "CCO"
            properties: ["lipophilicity", "solubility"]
      ```
    
    TEMPLATE VARIABLES:
    
      • {compound_id}, {protein_id} - Auto-incrementing IDs
      • {previous_job_output} - Reference outputs from earlier jobs
      • {batch_id} - Current batch identifier  
      • Custom variables defined in batch metadata
    
    USAGE EXAMPLES:
    
      # Preview batch without running
      ivybloom batch submit screening.yaml --dry-run
      
      # Submit and wait for completion
      ivybloom batch submit jobs.yaml --wait
      
      # Override project ID from command line
      ivybloom batch submit batch.yaml --project-id proj_new123
      
      # Limit concurrent execution
      ivybloom batch submit large_batch.yaml --max-concurrent 5
    
    The batch will be queued and jobs will execute according to dependencies
    and available computational resources.
    
    💡 TIP: Use descriptive job titles with variables for easy identification
    💡 TIP: Start small with --dry-run to validate your batch configuration
    """
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Load job definitions
    try:
        with open(job_file, 'r') as f:
            if job_file.endswith('.yaml') or job_file.endswith('.yml'):
                jobs_data = yaml.safe_load(f)
            else:
                jobs_data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading job file: {e}[/red]")
        return
    
    # Validate job structure
    if not isinstance(jobs_data, dict) or 'jobs' not in jobs_data:
        console.print("[red]Error: Job file must contain a 'jobs' array[/red]")
        return
    
    jobs = jobs_data['jobs']
    if not isinstance(jobs, list):
        console.print("[red]Error: 'jobs' must be an array[/red]")
        return
    
    # Show what will be submitted
    console.print(f"\n[bold cyan]Batch Job Submission[/bold cyan]")
    console.print(f"Jobs to submit: {len(jobs)}")
    if batch_title:
        console.print(f"Batch title: {batch_title}")
    if project_id:
        console.print(f"Project ID: {project_id}")
    
    # Show job details
    table = Table(title="Jobs to Submit")
    table.add_column("Index", style="cyan")
    table.add_column("Tool", style="green")
    table.add_column("Title", style="yellow")
    table.add_column("Parameters", style="dim")
    
    for i, job in enumerate(jobs):
        tool_name = job.get('tool_name', 'Unknown')
        job_title = job.get('job_title', f'Batch job {i+1}')
        params = str(job.get('parameters', {}))[:50] + '...' if len(str(job.get('parameters', {}))) > 50 else str(job.get('parameters', {}))
        table.add_row(str(i+1), tool_name, job_title, params)
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no jobs were submitted[/yellow]")
        return
    
    # Confirm submission
    if not Confirm.ask(f"\nSubmit {len(jobs)} jobs?"):
        console.print("[yellow]Batch submission cancelled[/yellow]")
        return
    
    # Helper: get nested value from dict using dotted path (e.g., "outputs.best_pose_url")
    def _get_nested_value(obj: Union[Dict, List], path: str) -> Any:
        parts = [p for p in path.split('.') if p]
        cur: Any = obj
        for part in parts:
            if isinstance(cur, list):
                try:
                    idx = int(part)
                    cur = cur[idx]
                except Exception:
                    raise KeyError(f"List index '{part}' invalid in path '{path}'")
            elif isinstance(cur, dict):
                if part not in cur:
                    raise KeyError(f"Missing key '{part}' in path '{path}'")
                cur = cur[part]
            else:
                raise KeyError(f"Cannot traverse '{part}' in path '{path}'")
        return cur

    # Helper: resolve parameter templates referencing prior step outputs
    # Supported: ${steps.<key>.outputs.<field.path>}
    def _resolve_templates(params: Any, results_by_key: Dict[str, Dict[str, Any]]) -> Any:
        if isinstance(params, dict):
            return {k: _resolve_templates(v, results_by_key) for k, v in params.items()}
        if isinstance(params, list):
            return [_resolve_templates(v, results_by_key) for v in params]
        if isinstance(params, str) and params.startswith('${') and params.endswith('}'):
            expr = params[2:-1]
            # Expect format: steps.<key>.outputs.<path>
            if not expr.startswith('steps.'):
                return params
            try:
                remainder = expr[len('steps.'):]
                key, _, out_path = remainder.partition('.outputs.')
                if not _:
                    return params
                if key not in results_by_key:
                    raise KeyError(f"Referenced step '{key}' not available yet")
                step_result = results_by_key[key]
                # convention: results store under 'outputs'
                outputs = step_result.get('outputs', step_result)
                return _get_nested_value(outputs, out_path)
            except Exception as e:
                raise ValueError(f"Failed to resolve template {params}: {e}")
        return params

    # Submit jobs (sequential with dependency resolution)
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            submitted_jobs = []
            failed_jobs = []
            results_by_key: Dict[str, Dict[str, Any]] = {}
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Submitting jobs...", total=len(jobs))
                
                for i, job in enumerate(jobs):
                    try:
                        # Prepare job request
                        step_key = job.get('key') or f"job_{i+1}"
                        raw_params = job.get('parameters', {})
                        # Resolve any ${steps.<key>.outputs.<path>} references
                        resolved_params = _resolve_templates(raw_params, results_by_key)
                        job_request = {
                            'tool_name': job['tool_name'],
                            'parameters': resolved_params,
                            'project_id': job.get('project_id') or project_id,
                            'job_title': job.get('job_title') or f'Batch job {i+1}'
                        }
                        
                        # Submit job
                        result = client.create_job(job_request)
                        submitted_jobs.append({
                            'index': i+1,
                            'job_id': result['job_id'],
                            'tool_name': job['tool_name'],
                            'title': job_request['job_title'],
                            'key': step_key
                        })
                        
                        progress.update(task, advance=1, description=f"Submitted job {i+1}/{len(jobs)}")
                        
                        # Wait for completion to make outputs available for subsequent steps
                        # (sequential model for correctness when chaining)
                        try:
                            from ..client.api_client import IvyBloomAPIClient as _Client
                            status = client.get_job_status(result['job_id'])
                            while status.get('status') not in ['completed', 'failed', 'cancelled']:
                                time.sleep(3)
                                status = client.get_job_status(result['job_id'])
                            if status.get('status') == 'completed':
                                job_results = client.get_job_results(result['job_id'], format='json')
                                # Store under results_by_key for template resolution
                                results_by_key[step_key] = job_results if isinstance(job_results, dict) else {'outputs': job_results}
                        except Exception:
                            # If results not available, downstream references will fail fast
                            pass

                    except Exception as e:
                        failed_jobs.append({
                            'index': i+1,
                            'error': str(e),
                            'tool_name': job.get('tool_name', 'Unknown')
                        })
                        progress.update(task, advance=1, description=f"Failed job {i+1}/{len(jobs)}")
            
            # Show results
            console.print(f"\n[bold green]Batch submission completed[/bold green]")
            console.print(f"Successfully submitted: {len(submitted_jobs)}")
            console.print(f"Failed: {len(failed_jobs)}")
            
            if submitted_jobs:
                success_table = Table(title="Successfully Submitted Jobs")
                success_table.add_column("Index", style="cyan")
                success_table.add_column("Job ID", style="green")
                success_table.add_column("Tool", style="yellow")
                success_table.add_column("Title", style="dim")
                
                for job in submitted_jobs:
                    success_table.add_row(
                        str(job['index']),
                        job['job_id'],
                        job['tool_name'],
                        job['title']
                    )
                
                console.print(success_table)
            
            if failed_jobs:
                console.print(f"\n[bold red]Failed Jobs:[/bold red]")
                for job in failed_jobs:
                    console.print(f"  {job['index']}: {job['tool_name']} - {job['error']}")
    
    except Exception as e:
        console.print(f"[red]Error during batch submission: {e}[/red]")

@batch.command()
@click.argument('job_ids', nargs=-1, required=True)
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def cancel(ctx, job_ids: tuple, confirm: bool):
    """Cancel multiple jobs by ID"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold yellow]Batch Job Cancellation[/bold yellow]")
    console.print(f"Jobs to cancel: {len(job_ids)}")
    
    # Show jobs to cancel
    for job_id in job_ids:
        console.print(f"  - {job_id}")
    
    if not confirm and not Confirm.ask(f"\nCancel {len(job_ids)} jobs?"):
        console.print("[yellow]Batch cancellation cancelled[/yellow]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            cancelled_jobs = []
            failed_jobs = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Cancelling jobs...", total=len(job_ids))
                
                for i, job_id in enumerate(job_ids):
                    try:
                        client.cancel_job(job_id)
                        cancelled_jobs.append(job_id)
                        progress.update(task, advance=1, description=f"Cancelled {i+1}/{len(job_ids)}")
                        
                    except Exception as e:
                        failed_jobs.append({'job_id': job_id, 'error': str(e)})
                        progress.update(task, advance=1, description=f"Failed {i+1}/{len(job_ids)}")
            
            # Show results
            console.print(f"\n[bold green]Batch cancellation completed[/bold green]")
            console.print(f"Successfully cancelled: {len(cancelled_jobs)}")
            console.print(f"Failed: {len(failed_jobs)}")
            
            if failed_jobs:
                console.print(f"\n[bold red]Failed Cancellations:[/bold red]")
                for job in failed_jobs:
                    console.print(f"  {job['job_id']}: {job['error']}")
    
    except Exception as e:
        console.print(f"[red]Error during batch cancellation: {e}[/red]")

@batch.command()
@click.argument('job_ids', nargs=-1, required=True)
@click.option('--format', default='json', type=click.Choice(['json', 'yaml', 'table']), help='Output format')
@click.option('--output-dir', help='Directory to save results')
@click.pass_context
def results(ctx, job_ids: tuple, format: str, output_dir: str):
    """Download results for multiple jobs"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold cyan]Batch Results Download[/bold cyan]")
    console.print(f"Jobs to download: {len(job_ids)}")
    
    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
        console.print(f"Output directory: {output_dir}")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            results = []
            failed_jobs = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Downloading results...", total=len(job_ids))
                
                for i, job_id in enumerate(job_ids):
                    try:
                        result = client.get_job_results(job_id, format=format)
                        results.append({'job_id': job_id, 'result': result})
                        
                        # Save to file if output directory specified
                        if output_dir:
                            import os
                            filename = f"job_{job_id}_results.{format}"
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'w') as f:
                                if format == 'json':
                                    json.dump(result, f, indent=2)
                                elif format == 'yaml':
                                    yaml.dump(result, f, default_flow_style=False)
                                else:
                                    f.write(str(result))
                        
                        progress.update(task, advance=1, description=f"Downloaded {i+1}/{len(job_ids)}")
                        
                    except Exception as e:
                        failed_jobs.append({'job_id': job_id, 'error': str(e)})
                        progress.update(task, advance=1, description=f"Failed {i+1}/{len(job_ids)}")
            
            # Show results
            console.print(f"\n[bold green]Batch download completed[/bold green]")
            console.print(f"Successfully downloaded: {len(results)}")
            console.print(f"Failed: {len(failed_jobs)}")
            
            if not output_dir and results:
                # Display results inline
                for result in results:
                    console.print(f"\n[bold]Job {result['job_id']}:[/bold]")
                    if format == 'json':
                        emit_json(result['result'])
                    elif format == 'yaml':
                        console.print(yaml.dump(result['result'], default_flow_style=False))
                    else:
                        console.print(str(result['result']))
            
            if failed_jobs:
                console.print(f"\n[bold red]Failed Downloads:[/bold red]")
                for job in failed_jobs:
                    console.print(f"  {job['job_id']}: {job['error']}")
    
    except Exception as e:
        console.print(f"[red]Error during batch download: {e}[/red]")
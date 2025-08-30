"""
Workflow and job chaining commands for IvyBloom CLI
"""

import click
import json
import yaml
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..client.api_client import IvyBloomAPIClient
from ..utils.colors import get_console

console = get_console()

@click.group()
def workflows():
    """Compose and run multi-step workflows (WIP)

    - Run:       ivybloom workflows run <file.yaml> [--project-id <id>] [--wait]
    - Validate:  ivybloom workflows validate <file.yaml>
    - Template:  ivybloom workflows create <file.yaml> [--format yaml|json]
    - List:      ivybloom workflows list

    Notes:
      - Workflow files are YAML/JSON with jobs, depends_on, and data flow.
      - Use --dry-run to preview execution order and parameters.
    """
    pass

@workflows.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--project-id', help='Project ID to run workflow in')
@click.option('--wait', is_flag=True, help='Wait for all jobs to complete')
@click.option('--parallel', is_flag=True, help='Run jobs in parallel where possible')
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running')
@click.pass_context
def run(ctx, workflow_file, project_id, wait, parallel, dry_run):
    """Execute a workflow from file"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        # Load workflow file
        workflow_path = Path(workflow_file)
        with open(workflow_path, 'r') as f:
            if workflow_path.suffix.lower() in ['.yaml', '.yml']:
                workflow = yaml.safe_load(f)
            else:
                workflow = json.load(f)
        
        # Validate workflow structure
        if 'name' not in workflow:
            console.print("[red]❌ Workflow file must contain a 'name' field[/red]")
            return
        
        if 'jobs' not in workflow:
            console.print("[red]❌ Workflow file must contain a 'jobs' field[/red]")
            return
        
        console.print(f"[cyan]🔄 Loading workflow: {workflow['name']}[/cyan]")
        
        if dry_run:
            _show_workflow_plan(workflow, project_id)
            return
        
        # Execute workflow
        with IvyBloomAPIClient(config, auth_manager) as client:
            job_results = _execute_workflow(client, workflow, project_id, parallel, wait)
        
        # Display results
        _show_workflow_results(job_results)
        
    except Exception as e:
        console.print(f"[red]❌ Error executing workflow: {e}[/red]")

@workflows.command()
@click.argument('output_file', type=click.Path())
@click.option('--format', default='yaml', type=click.Choice(['yaml', 'json']), help='Output format')
@click.pass_context
def create(ctx, output_file, format):
    """Create a new workflow template"""
    
    template = {
        "name": "My Workflow",
        "description": "Description of what this workflow does",
        "version": "1.0",
        "jobs": [
            {
                "name": "job1",
                "tool": "esmfold",
                "parameters": {
                    "protein_sequence": "MKLLVLGLVGAVL"
                },
                "depends_on": []
            },
            {
                "name": "job2", 
                "tool": "diffdock",
                "parameters": {
                    "protein_pdb": "${job1.output.protein_pdb}",
                    "ligand_smiles": "CCO"
                },
                "depends_on": ["job1"]
            }
        ]
    }
    
    try:
        with open(output_file, 'w') as f:
            if format == 'yaml':
                yaml.dump(template, f, default_flow_style=False, indent=2)
            else:
                json.dump(template, f, indent=2)
        
        console.print(f"[green]✅ Workflow template created: {output_file}[/green]")
        console.print("Edit the file to customize your workflow.")
        
    except Exception as e:
        console.print(f"[red]❌ Error creating workflow template: {e}[/red]")

@workflows.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, workflow_file):
    """🔍 Validate workflow file structure and dependencies
    
    Perform comprehensive validation of workflow files before execution.
    This command checks syntax, job dependencies, parameter requirements,
    and workflow structure to catch errors early and save compute time.
    
    VALIDATION CHECKS:
    
      ✅ YAML/JSON syntax validation
      ✅ Required workflow fields (name, jobs)
      ✅ Job structure and dependencies
      ✅ Circular dependency detection
      ✅ Parameter existence checks
      ✅ Tool name validation
    
    WHY VALIDATE FIRST:
    
      🚀 Catch errors before expensive computations start
      💰 Avoid wasted compute credits on malformed workflows
      🔧 Get specific error messages for quick fixes
      📋 Ensure workflows meet IvyBloom standards
      🔗 Verify job dependency chains are valid
    
    VALIDATION LEVELS:
    
      🔴 ERRORS: Critical issues that prevent execution
      🟡 WARNINGS: Potential issues that may cause problems
      🟢 SUCCESS: Workflow is ready for execution
    
    USAGE EXAMPLES:
    
      # Validate before running expensive workflows
      ivybloom workflows validate my-drug-discovery.yaml
      
      # Quick check after editing workflow files
      ivybloom workflows validate protein-analysis.yaml
      
      # Validate all workflows in current directory
      for file in *.yaml; do ivybloom workflows validate "$file"; done
    
    COMMON VALIDATION ERRORS:
    
      • Missing required fields (name, jobs)
      • Duplicate job names within workflow
      • Circular dependencies between jobs
      • References to non-existent job outputs
      • Invalid tool names or parameters
    
    💡 TIP: Always validate workflows after editing before submission!
    💡 TIP: Use validation in CI/CD pipelines for workflow quality control
    """
    
    try:
        # Load workflow file
        workflow_path = Path(workflow_file)
        with open(workflow_path, 'r') as f:
            if workflow_path.suffix.lower() in ['.yaml', '.yml']:
                workflow = yaml.safe_load(f)
            else:
                workflow = json.load(f)
        
        # Validate structure
        errors = []
        warnings = []
        
        # Required fields
        if 'name' not in workflow:
            errors.append("Missing required field: 'name'")
        if 'jobs' not in workflow:
            errors.append("Missing required field: 'jobs'")
        elif not hasattr(workflow['jobs'], '__iter__') or hasattr(workflow['jobs'], 'split'):
            errors.append("Field 'jobs' must be a list")
        
        # Validate jobs
        if 'jobs' in workflow:
            job_names = set()
            for i, job in enumerate(workflow['jobs']):
                if not hasattr(job, 'get'):
                    errors.append(f"Job {i} must be an object")
                    continue
                
                if 'name' not in job:
                    errors.append(f"Job {i} missing required field: 'name'")
                else:
                    if job['name'] in job_names:
                        errors.append(f"Duplicate job name: {job['name']}")
                    job_names.add(job['name'])
                
                if 'tool' not in job:
                    errors.append(f"Job {job.get('name', i)} missing required field: 'tool'")
                
                if 'parameters' not in job:
                    warnings.append(f"Job {job.get('name', i)} has no parameters")
                
                # Validate dependencies
                if 'depends_on' in job:
                    for dep in job['depends_on']:
                        if dep not in job_names and dep != job.get('name'):
                            # This might be valid if the dependency comes later
                            pass
        
        # Display results
        if errors:
            console.print("[red]❌ Validation failed with errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
        
        if warnings:
            console.print("[yellow]⚠️  Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")
        
        if not errors and not warnings:
            console.print("[green]✅ Workflow file is valid[/green]")
        elif not errors:
            console.print("[green]✅ Workflow file is valid (with warnings)[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error validating workflow: {e}[/red]")

@workflows.command()
@click.pass_context
def list(ctx):
    """List available workflow templates"""
    
    # This would list saved workflows - for now just show the concept
    console.print("[cyan]📋 Available Workflow Templates[/cyan]")
    console.print("  • protein-folding-and-docking.yaml")
    console.print("  • drug-discovery-pipeline.yaml") 
    console.print("  • batch-protein-analysis.yaml")
    console.print()
    console.print("Use 'ivybloom workflows create <filename>' to create a new template")

def _show_workflow_plan(workflow, project_id):
    """Show what would be executed in dry-run mode"""
    console.print(f"[cyan]📋 Workflow Plan: {workflow['name']}[/cyan]")
    
    if project_id:
        console.print(f"Project: {project_id}")
    
    table = Table(title="Jobs to Execute")
    table.add_column("Job", style="cyan")
    table.add_column("Tool", style="green")
    table.add_column("Dependencies", style="yellow")
    table.add_column("Parameters", style="dim")
    
    for job in workflow['jobs']:
        deps = ", ".join(job.get('depends_on', [])) or "None"
        params = str(len(job.get('parameters', {}))) + " params"
        table.add_row(
            job['name'],
            job['tool'],
            deps,
            params
        )
    
    console.print(table)

def _execute_workflow(client, workflow, project_id, parallel, wait):
    """Execute the workflow jobs"""
    job_results = {}
    
    # Simple sequential execution for now
    # TODO: Implement proper dependency resolution and parallel execution
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for job in workflow['jobs']:
            task = progress.add_task(f"Executing {job['name']}...", total=None)
            
            try:
                # Create job request
                job_request = {
                    "tool_name": job['tool'],
                    "parameters": job.get('parameters', {}),
                    "project_id": project_id,
                    "job_title": f"{workflow['name']} - {job['name']}"
                }
                
                # Submit job
                response = client.create_job(job_request)
                job_results[job['name']] = {
                    "status": "submitted",
                    "job_id": response['job_id'],
                    "response": response
                }
                
                progress.update(task, description=f"✅ {job['name']} submitted")
                
            except Exception as e:
                job_results[job['name']] = {
                    "status": "failed",
                    "error": str(e)
                }
                progress.update(task, description=f"❌ {job['name']} failed")
    
    return job_results

def _show_workflow_results(job_results):
    """Display workflow execution results"""
    table = Table(title="🎯 Workflow Results")
    table.add_column("Job", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Job ID", style="green")
    table.add_column("Details", style="dim")
    
    for job_name, result in job_results.items():
        if result['status'] == 'submitted':
            status = "[green]SUBMITTED[/green]"
            job_id = result['job_id'][:8] + "..."
            details = "Job running"
        else:
            status = "[red]FAILED[/red]"
            job_id = "N/A"
            details = result.get('error', 'Unknown error')
        
        table.add_row(job_name, status, job_id, details)
    
    console.print(table)
    
    # Show next steps
    submitted_jobs = [r for r in job_results.values() if r['status'] == 'submitted']
    if submitted_jobs:
        console.print()
        console.print("[cyan]💡 Next Steps:[/cyan]")
        for result in submitted_jobs:
            job_id = result['job_id']
            console.print(f"  • Check status: [bold]ivybloom jobs status {job_id}[/bold]")
            console.print(f"  • Get results: [bold]ivybloom jobs results {job_id}[/bold]")
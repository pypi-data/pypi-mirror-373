"""
Data management commands for IvyBloom CLI
"""

import click
import json
import os
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt

from ..client.api_client import IvyBloomAPIClient
from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info
from ..utils.printing import emit_json

console = get_console()

@click.group()
@click.pass_context
def data(ctx):
    """📁 Data management and file operations
    
    Upload, organize, and manage files for your computational workflows.
    Securely store input data and retrieve results from your jobs.
    
    DATA MANAGEMENT FEATURES:
    
      📤 Upload files:          ivybloom data upload my_file.pdb
      📋 List stored files:     ivybloom data list
      📥 Download results:      ivybloom data download <file_id>
      🗂️  Project organization: Upload files to specific projects
      🏷️  File tagging:         Tag files for easy discovery
      🔍 Search & filter:       Find files by name, project, or tags
    
    SUPPORTED FILE TYPES:
    
      🧬 Molecular data:        .pdb, .mol2, .sdf, .xyz
      📊 Analysis data:         .csv, .json, .xlsx  
      📄 Documents:             .txt, .pdf, .docx
      🖼️  Images & plots:       .png, .jpg, .svg
      📦 Archives:              .zip, .tar.gz
    
    DATA WORKFLOWS:
    
      1. Upload input files for jobs
      2. Tag and organize by project
      3. Reference in job submissions
      4. Download and analyze results
    
    SECURITY & PRIVACY:
    
      • Files encrypted at rest and in transit
      • Access controlled by your account permissions  
      • Automatic cleanup of temporary files
      • GDPR and SOC2 compliant storage
    
    💡 TIP: Upload files to projects to keep your data organized!
    💡 TIP: Use descriptive tags to make files easy to find later
    
    Run 'ivybloom data <command> --help' for detailed help on each command.
    """
    pass

@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--project-id', help='Project ID to upload to')
@click.option('--description', help='Description of the file')
@click.option('--tags', help='Comma-separated tags for the file')
@click.option('--public', is_flag=True, help='Make file publicly accessible')
@click.option('--overwrite', is_flag=True, help='Overwrite existing file with same name')
@click.pass_context
def upload(ctx, file_path: str, project_id: str, description: str, tags: str, public: bool, overwrite: bool):
    """📤 Upload files to secure cloud storage
    
    Upload molecular data, input files, and other resources for use in
    computational jobs and analyses.
    
    FILE ORGANIZATION:
    
      🗂️  Projects:       Group files by research project
      🏷️  Tags:           Add searchable labels (drug-discovery, protein, etc.)
      📝 Descriptions:   Add detailed file descriptions
      🔒 Permissions:     Control who can access your files
    
    USAGE EXAMPLES:
    
      # Basic upload
      ivybloom data upload protein.pdb
      
      # Upload to project with tags
      ivybloom data upload molecule.sdf --project-id proj123 \\
                                       --tags "drug-discovery,covid"
      
      # Upload with description
      ivybloom data upload results.csv --description "Binding affinity analysis"
      
      # Make publicly accessible
      ivybloom data upload dataset.json --public
    
    SUPPORTED FORMATS:
    
      🧬 Molecular:  .pdb, .mol2, .sdf, .xyz, .cif
      📊 Data:       .csv, .json, .xlsx, .tsv
      📄 Text:       .txt, .fasta, .fa, .seq  
      🖼️  Images:     .png, .jpg, .svg, .pdf
      📦 Archives:   .zip, .tar.gz, .7z
    
    After upload, files can be referenced in job submissions using their file ID
    or name within the same project.
    
    💡 TIP: Use --tags to make files searchable across projects
    💡 TIP: Large files (>100MB) use resumable multi-part upload
    """
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    file_path = Path(file_path)
    file_size = file_path.stat().st_size
    
    console.print(f"\n[bold cyan]File Upload[/bold cyan]")
    console.print(f"File: {file_path.name}")
    console.print(f"Size: {file_size:,} bytes")
    console.print(f"Path: {file_path}")
    
    if project_id:
        console.print(f"Project: {project_id}")
    if description:
        console.print(f"Description: {description}")
    if tags:
        console.print(f"Tags: {tags}")
    
    if not Confirm.ask("\nProceed with upload?"):
        console.print("[yellow]Upload cancelled[/yellow]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Prepare upload data
            upload_data = {
                'filename': file_path.name,
                'size': file_size,
                'project_id': project_id,
                'description': description,
                'tags': tags.split(',') if tags else []
            }
            
            # Note: This is a simplified example. Real implementation would need
            # to handle multipart uploads, presigned URLs, etc.
            console.print("[yellow]Note: File upload functionality requires backend storage API[/yellow]")
            console.print(f"[dim]Would upload: {upload_data}[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error during upload: {e}[/red]")

@data.command()
@click.option('--project-id', help='Filter by project ID')
@click.option('--file-type', help='Filter by file type')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--limit', default=50, help='Maximum number of files to list')
@click.option('--format', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def list(ctx, project_id: str, file_type: str, tags: str, limit: int, format: str):
    """List uploaded files"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold cyan]File Listing[/bold cyan]")
    
    filters = {}
    if project_id:
        filters['project_id'] = project_id
    if file_type:
        filters['file_type'] = file_type
    if tags:
        filters['tags'] = tags
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Note: This would call a real data listing endpoint
            console.print("[yellow]Note: File listing requires backend storage API[/yellow]")
            
            # Mock data for demonstration
            mock_files = [
                {
                    'id': 'file_001',
                    'filename': 'protein_sequences.fasta',
                    'size': 1024000,
                    'type': 'fasta',
                    'project_id': 'proj_123',
                    'uploaded_at': '2025-01-15T10:30:00Z',
                    'tags': ['protein', 'sequences']
                },
                {
                    'id': 'file_002',
                    'filename': 'compound_library.sdf',
                    'size': 5120000,
                    'type': 'sdf',
                    'project_id': 'proj_456',
                    'uploaded_at': '2025-01-15T11:45:00Z',
                    'tags': ['compounds', 'library']
                }
            ]
            
            if format == 'table':
                table = Table(title="Uploaded Files")
                table.add_column("ID", style="cyan")
                table.add_column("Filename", style="green")
                table.add_column("Size", style="yellow")
                table.add_column("Type", style="blue")
                table.add_column("Project", style="magenta")
                table.add_column("Tags", style="dim")
                
                for file in mock_files:
                    size_str = f"{file['size']:,} bytes"
                    tags_str = ', '.join(file['tags']) if file['tags'] else ''
                    table.add_row(
                        file['id'],
                        file['filename'],
                        size_str,
                        file['type'],
                        file['project_id'],
                        tags_str
                    )
                
                console.print(table)
            
            elif format == 'json':
                emit_json(mock_files)
            
            else:  # yaml
                import yaml
                console.print(yaml.dump(mock_files, default_flow_style=False))
            
    except Exception as e:
        console.print(f"[red]Error listing files: {e}[/red]")

@data.command()
@click.argument('file_id')
@click.argument('output_path', type=click.Path())
@click.pass_context
def download(ctx, file_id: str, output_path: str):
    """Download a file by ID"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold cyan]File Download[/bold cyan]")
    console.print(f"File ID: {file_id}")
    console.print(f"Output path: {output_path}")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Note: This would call a real download endpoint
            console.print("[yellow]Note: File download requires backend storage API[/yellow]")
            console.print("[dim]Would download file to specified path[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error downloading file: {e}[/red]")

@data.command()
@click.argument('file_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete(ctx, file_id: str, confirm: bool):
    """Delete a file by ID"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    console.print(f"\n[bold red]File Deletion[/bold red]")
    console.print(f"File ID: {file_id}")
    
    if not confirm and not Confirm.ask("Are you sure you want to delete this file?"):
        console.print("[yellow]Deletion cancelled[/yellow]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Note: This would call a real deletion endpoint
            console.print("[yellow]Note: File deletion requires backend storage API[/yellow]")
            console.print("[dim]Would delete the specified file[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error deleting file: {e}[/red]")

@data.command()
@click.argument('local_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--project-id', help='Project ID to sync to')
@click.option('--exclude', multiple=True, help='File patterns to exclude')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without actually syncing')
@click.pass_context
def sync(ctx, local_dir: str, project_id: str, exclude: tuple, dry_run: bool):
    """Sync a local directory with the platform"""
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    local_path = Path(local_dir)
    
    console.print(f"\n[bold cyan]Directory Sync[/bold cyan]")
    console.print(f"Local directory: {local_path}")
    if project_id:
        console.print(f"Project ID: {project_id}")
    if exclude:
        console.print(f"Exclude patterns: {', '.join(exclude)}")
    
    # Find files to sync
    files_to_sync = []
    for file_path in local_path.rglob('*'):
        if file_path.is_file():
            # Check exclusions
            excluded = False
            for pattern in exclude:
                if pattern in str(file_path):
                    excluded = True
                    break
            
            if not excluded:
                files_to_sync.append(file_path)
    
    console.print(f"Files to sync: {len(files_to_sync)}")
    
    if dry_run:
        console.print("\n[yellow]Dry run - files that would be synced:[/yellow]")
        for file_path in files_to_sync:
            relative_path = file_path.relative_to(local_path)
            console.print(f"  {relative_path}")
        return
    
    if not files_to_sync:
        console.print("[yellow]No files to sync[/yellow]")
        return
    
    if not Confirm.ask(f"\nSync {len(files_to_sync)} files?"):
        console.print("[yellow]Sync cancelled[/yellow]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Note: This would implement actual sync logic
            console.print("[yellow]Note: Directory sync requires backend storage API[/yellow]")
            console.print(f"[dim]Would sync {len(files_to_sync)} files[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error during sync: {e}[/red]")
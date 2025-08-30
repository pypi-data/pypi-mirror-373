"""
Run command for executing individual tools
"""

import click
import json
import time
import re
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info
from ..utils.schema_loader import (
    get_tool_schema,
    get_available_tools,
    resolve_tool_name,
    normalize_parameters_schema,
    build_json_schema,
)
from ..client.api_client import IvyBloomAPIClient
from ..utils.printing import emit_json
import httpx

console = get_console()

@click.command()
@click.argument('tool_name')
@click.argument('parameters', nargs=-1)
@click.option('--project-id', help='Project ID to run the job in')
@click.option('--job-title', help='Custom title for the job')
@click.option('--wait', is_flag=True, help='Wait for job completion')
@click.option('--dry-run', is_flag=True, help='Validate parameters without executing')
@click.option('--show-schema', is_flag=True, help='Show tool parameter schema and exit')
@click.option('--output-format', default='table', type=click.Choice(['json', 'yaml', 'table']), help='Output format')
@click.option('--json-verbose', is_flag=True, help='Print verbose JSON payload with resolved parameters and schema hints (implies --output-format json)')
@click.option('--need', 'needs', multiple=True, help='Declare required features or outputs (name or name=value). Can be repeated.')
@click.option('--want', 'wants', multiple=True, help='Declare optional features or outputs (name or name=value). Can be repeated.')
@click.option('--feature', 'features', multiple=True, help='Set feature flags (name or name=value). Can be repeated.')
@click.pass_context
def run(ctx, tool_name, parameters, project_id, job_title, wait, dry_run, show_schema, output_format, json_verbose, needs, wants, features):
    """Run a tool with parameters and feature flags

    - Basic: ivybloom run <tool> key=value [key=value ...]
    - Params: pass inputs as key=value (quote strings; JSON allowed for objects)
    - Schema: --show-schema to view accepted parameters and defaults
    - Validate: --dry-run to validate without executing

    Examples:
      - ivybloom run esmfold protein_sequence=MKLLVLGLVGFGVGFG
      - ivybloom run diffdock protein_file="protein.pdb" ligand_smiles="CCO"
      - ivybloom run esmfold protein_sequence=MK... --project-id proj_123 --job-title "My Analysis" --wait
      - ivybloom run diffdock protein_file=protein.pdb ligand_file=ligand.sdf --need primary=pdb --want scores --feature use_fast_mode=true
      - ivybloom run reinvent input_json='{"scaffold":"c1ccccc1"}' --feature max_steps=2500 --want designs

    Common options:
      --project-id <id>   Project to associate this job with
      --job-title <text>  Custom job title
      --wait              Wait for completion, then print status
      --output-format     json|yaml|table (default: table)
      --need NAME[=VAL]   Declare required outputs/capabilities (repeatable)
      --want NAME[=VAL]   Declare optional outputs/capabilities (repeatable)
      --feature NAME[=VAL]  Enable feature flags (repeatable)

    Tip: Run 'ivybloom tools info <tool>' to review parameters and examples.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Check authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    # Resolve tool aliases
    resolved_tool_name = resolve_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Show schema and exit if requested
            if show_schema:
                _show_tool_schema(client, tool_name)
                return
            
            # Get and validate tool schema
            schema_data = get_tool_schema(tool_name, client)
            if not schema_data:
                console.print(f"[red]❌ Tool '{tool_name}' not found or not available[/red]")
                console.print("Run 'ivybloom tools list' to see available tools.")
                return
            
            # Parse parameters
            tool_params = _parse_parameters(parameters)

            # Normalize dashed keys to underscores for compatibility with schemas
            tool_params = _normalize_param_keys(tool_params)

            # Parse feature directives and embed under reserved key
            feature_directives = _parse_feature_directives(needs, wants, features)
            if feature_directives:
                tool_params['__features__'] = feature_directives

            # Tool-specific preprocessing (e.g., esmfold uniprot handling)
            tool_params = _preprocess_tool_parameters(tool_name, tool_params, schema_data)
            
            # Validate parameters against schema
            validation_errors = _validate_parameters(tool_params, schema_data)
            if validation_errors:
                console.print("[red]❌ Parameter validation failed:[/red]")
                for error in validation_errors:
                    console.print(f"   • {error}")
                console.print()
                console.print(f"[dim]💡 Run 'ivybloom tools info {tool_name}' to see parameter requirements[/dim]")
                return
            
            # Dry run - show what would be executed
            if dry_run:
                if json_verbose:
                    payload = {
                        "tool_name": tool_name,
                        "parameters": tool_params,
                        "project_id": project_id,
                        "job_title": job_title,
                        "validation": {
                            "errors": [],
                        },
                        "schema_hints": normalize_parameters_schema(schema_data),
                        "json_schema": build_json_schema(schema_data),
                    }
                    emit_json(payload)
                else:
                    _show_dry_run(tool_name, tool_params, project_id, job_title)
                return
            
            # Submit the job
            console.print(f"[cyan]🚀 Submitting {tool_name} job...[/cyan]")
            
            job_data = {
                "tool_name": tool_name,
                "parameters": tool_params,
                "wait_for_completion": wait
            }
            
            if project_id:
                job_data["project_id"] = project_id
            if job_title:
                job_data["job_title"] = job_title
                
            # API client uses create_job
            job_result = client.create_job(job_data)
            
            if json_verbose:
                verbose_payload = {
                    "request": job_data,
                    "response": job_result,
                    "schema_hints": normalize_parameters_schema(schema_data),
                    "json_schema": build_json_schema(schema_data),
                }
                emit_json(verbose_payload)
                return
            if output_format == 'json':
                emit_json(job_result)
                return
            elif output_format == 'yaml':
                import yaml
                console.print(yaml.dump(job_result, default_flow_style=False))
                return
            
            # Table format
            job_id = job_result.get('job_id', 'Unknown')
            status = job_result.get('status', 'unknown')
            
            console.print(f"[green]✅ Job submitted successfully![/green]")
            console.print(f"   Job ID: [cyan]{job_id}[/cyan]")
            console.print(f"   Status: [yellow]{status}[/yellow]")
            console.print(f"   Tool: [blue]{tool_name}[/blue]")
            
            if project_id:
                console.print(f"   Project: [magenta]{project_id}[/magenta]")
            if job_title:
                console.print(f"   Title: [green]{job_title}[/green]")
            
            console.print()
            console.print("[dim]📋 Next steps:[/dim]")
            console.print(f"   [dim]• Monitor: ivybloom jobs status {job_id}[/dim]")
            console.print(f"   [dim]• Results: ivybloom jobs results {job_id}[/dim]")
            console.print(f"   [dim]• Download: ivybloom jobs download {job_id}[/dim]")
            
            # Wait for completion if requested
            if wait:
                console.print()
                console.print("[yellow]⏳ Waiting for job completion...[/yellow]")
                _wait_for_completion(client, job_id)
                
    except Exception as e:
        console.print(f"[red]❌ Error executing tool: {e}[/red]")

def _parse_parameters(parameter_strings):
    """Parse key=value parameter strings into a dictionary"""
    params = {}
    
    for param_str in parameter_strings:
        if '=' not in param_str:
            console.print(f"[red]❌ Invalid parameter format: {param_str}[/red]")
            console.print("Parameters must be in format: key=value")
            continue
            
        key, value = param_str.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Try to parse as JSON for complex values
        if value.startswith('{') or value.startswith('[') or value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # Keep as string
        # Try to parse numbers
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string
        # Parse booleans
        elif value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
            
        params[key] = value
    
    return params

def _normalize_param_keys(value):
    """Recursively normalize parameter keys by converting dashes to underscores.

    The CLI should allow dashed input keys for ergonomics, but schemas typically
    use snake_case. This normalizer converts keys like "ligand-file" -> "ligand_file".
    """
    if isinstance(value, dict):
        normalized = {}
        for k, v in value.items():
            new_key = k.replace('-', '_') if isinstance(k, str) else k
            normalized[new_key] = _normalize_param_keys(v)
        return normalized
    if isinstance(value, list):
        return [_normalize_param_keys(v) for v in value]
    return value

def _parse_feature_directives(needs, wants, features):
    """Parse --need/--want/--feature options into a structured directives object.

    Each item can be "name" or "name=value". Values follow the same parsing rules
    as regular parameters (JSON, numbers, booleans), and names are normalized to
    snake_case by replacing dashes with underscores.
    """
    def parse_items(items):
        result = {}
        for raw in items or []:
            if not isinstance(raw, str):
                continue
            if '=' in raw:
                name, val = raw.split('=', 1)
                name = (name or '').strip()
                val = (val or '').strip()
                # Attempt JSON/typed parse similar to _parse_parameters
                if val.startswith('{') or val.startswith('[') or val.startswith('"'):
                    try:
                        parsed_val = json.loads(val)
                    except json.JSONDecodeError:
                        parsed_val = val
                elif val.lower() in ('true', 'false'):
                    parsed_val = (val.lower() == 'true')
                elif val.isdigit():
                    parsed_val = int(val)
                else:
                    try:
                        parsed_val = float(val)
                    except ValueError:
                        parsed_val = val
                result[name.replace('-', '_')] = parsed_val
            else:
                name = raw.strip().replace('-', '_')
                if name:
                    result[name] = True
        return result

    directives = {}
    need_obj = parse_items(needs)
    want_obj = parse_items(wants)
    flag_obj = parse_items(features)
    if need_obj:
        directives['need'] = need_obj
    if want_obj:
        directives['want'] = want_obj
    if flag_obj:
        directives['flags'] = flag_obj
    return directives

def _looks_like_uniprot_accession(value: str) -> bool:
    """Heuristic check for UniProt accession (e.g., P69905, Q9XYZ1)."""
    if not isinstance(value, str):
        return False
    return bool(re.fullmatch(r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]{5}", value))

def _resolve_uniprot_sequence(accession: str) -> str:
    """Fetch protein sequence from UniProt. Returns empty string on failure."""
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
        resp = httpx.get(url, timeout=10)
        if resp.status_code != 200:
            return ""
        text = resp.text or ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # Remove FASTA header lines starting with '>'
        seq_lines = [ln for ln in lines if not ln.startswith('>')]
        seq = ''.join(seq_lines).strip()
        # Basic validation: letters only
        if seq and re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", seq):
            return seq
        return ""
    except Exception:
        return ""

def _preprocess_tool_parameters(tool_name: str, params: dict, schema_data: dict) -> dict:
    """Apply tool-specific conveniences and normalize into schema-aligned params.

    For 'esmfold':
      - Accept 'uniprot', 'uniprot_id', 'uniprot_accession', 'accession' and resolve to
        'protein_sequence' by fetching from UniProt
      - Accept 'protein' and map based on content: sequence string -> 'protein_sequence'
        URL ending with .fasta -> 'protein_fasta_url'
    Unknown convenience keys are removed after mapping to avoid validation errors.
    """
    if not isinstance(params, dict):
        return params

    effective = dict(params)
    tool_key = (tool_name or '').strip().lower()
    if tool_key == 'esmfold':
        # Gather convenience keys
        uni_keys = ['uniprot', 'uniprot_id', 'uniprot_accession', 'accession']
        uni_val = None
        for k in uni_keys:
            if k in effective and isinstance(effective[k], str) and effective[k].strip():
                uni_val = effective[k].strip()
                break
        if uni_val and _looks_like_uniprot_accession(uni_val):
            seq = _resolve_uniprot_sequence(uni_val)
            if seq:
                effective['protein_sequence'] = seq
            else:
                print_warning(f"Could not resolve UniProt accession '{uni_val}'. Proceeding without automatic sequence.")
            # Remove convenience keys to avoid validation errors
            for k in uni_keys:
                effective.pop(k, None)

        # 'protein' convenience mapping
        if 'protein' in effective and 'protein_sequence' not in effective and 'protein_fasta_url' not in effective:
            val = effective.get('protein')
            if isinstance(val, str):
                stripped = val.strip()
                if re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", stripped):
                    effective['protein_sequence'] = stripped
                    effective.pop('protein', None)
                elif stripped.startswith('http') and stripped.lower().endswith(('.fasta', '.fa')):
                    effective['protein_fasta_url'] = stripped
                    effective.pop('protein', None)
        # Final cleanup: remove any remaining unknown convenience keys
        for k in uni_keys:
            effective.pop(k, None)
    return effective

def _validate_parameters(params, schema_data):
    """Validate parameters against tool schema (recursive)."""
    errors = []

    def validate_value(value, schema, path):
        local_errors = []
        if not isinstance(schema, dict):
            return local_errors

        param_type = schema.get('type')

        # Enum constraint on the value itself
        enum_values = schema.get('enum')
        if enum_values is not None and value not in enum_values:
            local_errors.append(f"{path} must be one of: {', '.join(map(str, enum_values))}")
            return local_errors

        # Primitive type checks
        if param_type == 'integer':
            if not isinstance(value, int):
                local_errors.append(f"{path} must be an integer")
                return local_errors
        elif param_type == 'number':
            if not isinstance(value, (int, float)):
                local_errors.append(f"{path} must be a number")
                return local_errors
        elif param_type == 'boolean':
            if not isinstance(value, bool):
                local_errors.append(f"{path} must be true or false")
                return local_errors
        elif param_type == 'string':
            if not isinstance(value, str):
                local_errors.append(f"{path} must be a string")
                return local_errors
        elif param_type == 'array':
            if not isinstance(value, list):
                local_errors.append(f"{path} must be an array")
                return local_errors
        elif param_type == 'object':
            if not isinstance(value, dict):
                local_errors.append(f"{path} must be an object")
                return local_errors

        # Numeric bounds
        if isinstance(value, (int, float)):
            if 'min' in schema and value < schema['min']:
                local_errors.append(f"{path} must be >= {schema['min']}")
            if 'max' in schema and value > schema['max']:
                local_errors.append(f"{path} must be <= {schema['max']}")

        # String length bounds
        if isinstance(value, str):
            if 'minLength' in schema and len(value) < schema['minLength']:
                local_errors.append(f"{path} length must be >= {schema['minLength']}")
            if 'maxLength' in schema and len(value) > schema['maxLength']:
                local_errors.append(f"{path} length must be <= {schema['maxLength']}")

        # Array constraints and per-item validation
        if isinstance(value, list):
            if 'minItems' in schema and len(value) < schema['minItems']:
                local_errors.append(f"{path} must contain at least {schema['minItems']} items")
            if 'maxItems' in schema and len(value) > schema['maxItems']:
                local_errors.append(f"{path} must contain at most {schema['maxItems']} items")
            items_schema = schema.get('items')
            if isinstance(items_schema, dict):
                for idx, item in enumerate(value):
                    local_errors.extend(validate_value(item, items_schema, f"{path}[{idx}]"))

        # Object properties and required
        if isinstance(value, dict):
            props = schema.get('properties') or {}
            required = schema.get('required') or []
            for req in required:
                if req not in value:
                    local_errors.append(f"Missing required parameter: {path}.{req}")
            # Unknown keys
            for key in value.keys():
                if props and key not in props:
                    local_errors.append(f"Unknown parameter: {path}.{key}")
            for key, child_schema in props.items():
                if key in value:
                    local_errors.extend(validate_value(value[key], child_schema, f"{path}.{key}"))

        return local_errors

    # Normalize schema and validate
    normalized = normalize_parameters_schema(schema_data)
    properties = normalized.get('properties', {})
    required_fields = normalized.get('required', [])

    # Required at top-level
    for required_field in required_fields:
        if required_field not in params:
            errors.append(f"Missing required parameter: {required_field}")

    # Unknown at top-level (allow reserved __features__)
    for param_name in params.keys():
        if param_name == '__features__':
            continue
        if param_name not in properties:
            errors.append(f"Unknown parameter: {param_name}")

    # Per-parameter validation
    for param_name, schema in properties.items():
        if param_name in params:
            errors.extend(validate_value(params[param_name], schema or {}, param_name))

    return errors

def _show_tool_schema(client, tool_name):
    """Display tool schema information"""
    schema_data = get_tool_schema(tool_name, client)
    
    if not schema_data:
        console.print(f"[red]❌ Schema for '{tool_name}' not found[/red]")
        return
    
    console.print(f"[bold cyan]🧬 {tool_name.title()} - Parameter Schema[/bold cyan]")
    console.print(f"   {schema_data.get('description', 'No description available')}")
    console.print()
    
    # Show parameters (normalized from both flat and JSON-schema shapes)
    normalized = normalize_parameters_schema(schema_data)
    properties = normalized.get('properties', {})
    required_fields = normalized.get('required', [])
    
    if properties:
        table = Table(title="Parameters", show_header=True, header_style="bold cyan")
        table.add_column("Parameter", style="green")
        table.add_column("Type", style="blue") 
        table.add_column("Required", style="red")
        table.add_column("Description", style="white")
        table.add_column("Default", style="dim")
        
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'unknown')
            description = param_info.get('description', 'No description')
            is_required = "Yes" if param_name in required_fields else "No"
            default = str(param_info.get('default', '')) if 'default' in param_info else ''
            if 'enum' in param_info and param_info['enum']:
                description = f"{description} [choices: {', '.join(map(str, param_info['enum']))}]"
            
            table.add_row(param_name, param_type, is_required, description, default)
        
        console.print(table)
        console.print()
        
        # Show usage example
        console.print("[bold]Usage Example:[/bold]")
        example_params = []
        for param_name in required_fields[:3]:  # Show first 3 required params
            param_info = properties.get(param_name, {})
            param_type = param_info.get('type', 'string')
            
            if param_type == 'string':
                example_params.append(f'{param_name}="example_value"')
            elif param_type == 'integer':
                example_params.append(f'{param_name}=5')
            elif param_type == 'number':
                example_params.append(f'{param_name}=1.5')
            elif param_type == 'boolean':
                example_params.append(f'{param_name}=true')
            else:
                example_params.append(f'{param_name}=value')
        
        param_str = ' '.join(example_params)
        console.print(f"  [green]ivybloom run {tool_name} {param_str}[/green]")
        
    else:
        console.print("[yellow]No parameter information available[/yellow]")

def _show_dry_run(tool_name, params, project_id, job_title):
    """Show what would be executed in a dry run"""
    console.print(f"[yellow]🧪 Dry Run - No job will be submitted[/yellow]")
    console.print()
    
    console.print(f"[bold]Tool:[/bold] {tool_name}")
    if job_title:
        console.print(f"[bold]Title:[/bold] {job_title}")
    if project_id:
        console.print(f"[bold]Project:[/bold] {project_id}")
    
    console.print(f"[bold]Parameters:[/bold]")
    if params:
        for key, value in params.items():
            console.print(f"  • {key}: {value}")
    else:
        console.print("  (none)")
    
    console.print()
    console.print("[green]✅ Parameter validation passed![/green]")
    console.print("[dim]Run without --dry-run to execute the job.[/dim]")

def _wait_for_completion(client, job_id):
    """Wait for job completion and show results"""
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("Waiting for job completion...", total=None)
        
        while True:
            try:
                status_result = client.get_job_status(job_id)
                status = status_result.get('status', 'unknown')
                
                if status in ['completed', 'failed', 'cancelled']:
                    progress.update(task, description=f"Job {status}!")
                    time.sleep(0.5)
                    break
                
                progress.update(task, description=f"Job running... ({status})")
                time.sleep(3)  # Poll every 3 seconds
                
            except KeyboardInterrupt:
                progress.update(task, description="Cancelled by user!")
                time.sleep(0.5)
                console.print("\n[yellow]Stopped waiting, but job continues running on server.[/yellow]")
                console.print(f"[dim]Check status: ivybloom jobs status {job_id}[/dim]")
                return
            except Exception as e:
                progress.update(task, description=f"Error: {e}")
                time.sleep(1)
                return
    
    # Show final results
    console.print()
    try:
        final_status = client.get_job_status(job_id)
        status = final_status.get('status')
        
        if status == 'completed':
            print_success("🎉 Job completed successfully!")
            console.print(f"[dim]Get results: ivybloom jobs results {job_id}[/dim]")
        elif status == 'failed':
            print_error("❌ Job failed!")
            console.print(f"[dim]Check logs: ivybloom jobs status {job_id} --logs[/dim]")
        else:
            print_warning(f"Job ended with status: {status}")
            
    except Exception as e:
        console.print(f"[red]Error getting final status: {e}[/red]")

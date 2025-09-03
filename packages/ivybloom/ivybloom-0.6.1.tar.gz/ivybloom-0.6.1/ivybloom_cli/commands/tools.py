"""
Tool execution commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..utils.colors import get_console, get_tool_color, print_success, print_error, print_warning, print_info
from ..utils.schema_loader import (
    get_tool_schema,
    get_available_tools,
    resolve_tool_name as resolve_schema_tool_name,
    normalize_parameters_schema,
    extract_enum_choices,
)
from ..client.api_client import IvyBloomAPIClient
from ..utils.printing import emit_json

console = get_console()

@click.group()
def tools():
    """Discover available tools and their parameters

    - List:    ivybloom tools list [--verbose]
    - Details: ivybloom tools info <tool>
    - Schema:  ivybloom tools schema <tool> [--format json]
    - Hints:   ivybloom tools completions <tool> [--format json]
    """
    pass

@tools.command(name="list")
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.option('--verbose', is_flag=True, help='Show extended tool details (safe-rendered)')
@click.option('--format-json-with-schemas', is_flag=True, help='Return verbose JSON with embedded schemas (implies --format json)')
@click.pass_context
def list_tools_cmd(ctx, format, verbose, format_json_with_schemas):
    """🧬 List all available computational tools
    
    Browse the complete catalog of scientific tools available on the IvyBloom platform.
    Authentication is required to access the current tool catalog.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # All tools list access now requires authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Request compact vs verbose per flag
            tools_response = client.list_tools(verbose=verbose)
            # If verbose JSON with schemas is requested, fetch per-tool schemas and embed
            if format_json_with_schemas:
                verbose = True

            # Normalize various API shapes into a list of dict-like items
            items = []
            if isinstance(tools_response, dict):
                if 'tools' in tools_response and isinstance(tools_response['tools'], list):
                    items = tools_response['tools']
                else:
                    # Single object or unexpected shape
                    items = [tools_response]
            elif isinstance(tools_response, list):
                items = tools_response
            else:
                items = []

            # Separate into meta dicts vs plain names
            tools_meta = []
            tools_list = []
            for it in items:
                if isinstance(it, dict):
                    tools_meta.append(it)
                    name_val = it.get('name') or it.get('tool') or it.get('id') or ''
                    if name_val:
                        tools_list.append(str(name_val))
                else:
                    # Treat any non-dict (e.g., string) as a simple name
                    tools_list.append(str(it))
            
        if format == 'table':
            table = Table(title="🧬 Available Tools", show_header=True, header_style="bold cyan")
            table.add_column("Name", style="green", width=24)
            table.add_column("Display Name", style="white", width=28)
            table.add_column("Category", style="blue", width=16)
            table.add_column("Version", style="magenta", width=10)
            table.add_column("Status", style="cyan", width=12)
            table.add_column("Description", style="dim")

            if tools_meta is None:
                # Minimal fallback when only names are available
                for tool_name in tools_list:
                    table.add_row(tool_name, "", "", "", "Available", "")
            else:
                for t in tools_meta:
                    # Only safe-rendered fields; nested fields should be stringified by API
                    name = str(t.get('name', ''))
                    display_name = str(t.get('display_name', ''))
                    category = str(t.get('category', ''))
                    version = str(t.get('version', ''))
                    status = str(t.get('status', '')) or "Available"
                    description = str(t.get('description', ''))
                    table.add_row(name, display_name, category, version, status, description)

            console.print(table)
            console.print(f"\n[dim]💡 Total: {len(tools_list)} tools available[/dim]")
            console.print("[dim]📖 Run 'ivybloom tools info <tool_name>' for detailed parameter information[/dim]")
        
        elif format == 'json' or format_json_with_schemas:
            # Optionally enrich with per-tool schemas for programmatic clients
            if format_json_with_schemas and tools_meta:
                with IvyBloomAPIClient(config, auth_manager) as client:
                    enriched = []
                    for t in tools_meta:
                        name = t.get('name') or t.get('tool') or t.get('id')
                        schema_obj = None
                        if name:
                            try:
                                schema_obj = get_tool_schema(name, client)
                            except Exception:
                                schema_obj = None
                        t_enriched = dict(t)
                        if schema_obj:
                            t_enriched['schema'] = schema_obj
                        # If enum choices exist, expose for completion helpers
                        try:
                            from ..utils.schema_loader import extract_enum_choices
                            t_enriched['completion_hints'] = extract_enum_choices(schema_obj or {})
                        except Exception:
                            pass
                        enriched.append(t_enriched)
                emit_json(enriched)
                return
            if tools_meta:
                payload = tools_meta if verbose else [
                    {
                        'name': t.get('name'),
                        'display_name': t.get('display_name'),
                        'category': t.get('category'),
                        'description': t.get('description'),
                        'version': t.get('version'),
                        'status': t.get('status'),
                    } for t in tools_meta
                ]
                emit_json(payload)
            else:
                emit_json(tools_list)
            
    except Exception as e:
        console.print(f"[red]❌ Error fetching tools: {e}[/red]")

@tools.command()
@click.argument('tool_name')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, tool_name, format):
    """Show detailed information and parameters for a tool

    Displays required/optional parameters, types, defaults, and choices (enums).
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Resolve tool aliases
    resolved_tool_name = resolve_schema_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
    # All schema access now requires authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = get_tool_schema(tool_name, client)
            
        if not schema_data:
            console.print(f"[red]❌ Tool '{tool_name}' not found or schema not available[/red]")
            return
            
        if format == 'json':
            emit_json(schema_data)
            return
            
        # Table format display
        console.print(f"[bold cyan]{tool_name}[/bold cyan]")
        console.print(f"{schema_data.get('description', 'No description available')}")
        console.print()
        
        # Extract schema parameters (normalized)
        normalized = normalize_parameters_schema(schema_data)
        properties = normalized.get('properties', {})
        required_fields = normalized.get('required', [])
        
        if properties:
            console.print("[bold]Parameters:[/bold]")
            
            # Show required parameters first
            if required_fields:
                console.print("\n  [bold red]Required Parameters:[/bold red]")
                for param_name in required_fields:
                    param_info = properties.get(param_name, {})
                    param_type = param_info.get('type', 'unknown')
                    description = param_info.get('description', 'No description')
                    if 'enum' in param_info and param_info['enum']:
                        description = f"{description} [choices: {', '.join(map(str, param_info['enum']))}]"
                    console.print(f"    • [green]{param_name}[/green] ({param_type}): {description}")
                    if 'default' in param_info:
                        console.print(f"      [dim]Default: {param_info['default']}[/dim]")
            
            # Show optional parameters
            optional_fields = [name for name in properties.keys() if name not in required_fields]
            if optional_fields:
                console.print("\n  [bold yellow]Optional Parameters:[/bold yellow]")
                for param_name in optional_fields:
                    param_info = properties.get(param_name, {})
                    param_type = param_info.get('type', 'unknown')
                    description = param_info.get('description', 'No description')
                    if 'enum' in param_info and param_info['enum']:
                        description = f"{description} [choices: {', '.join(map(str, param_info['enum']))}]"
                    console.print(f"    • [green]{param_name}[/green] ({param_type}): {description}")
                    if 'default' in param_info:
                        console.print(f"      [dim]Default: {param_info['default']}[/dim]")
            
            console.print()
            console.print(f"[bold]Summary:[/bold] {len(required_fields)} required, {len(optional_fields)} optional")
            console.print()
            console.print("[bold]Common flags:[/bold] --need NAME[=VAL] (required outputs), --want NAME[=VAL] (optional outputs), --feature NAME[=VAL] (feature flags)")
            console.print()
            console.print("[bold]Example:[/bold]")
            # Simple example with flags in comment for discoverability
            example = []
            for param_name in required_fields[:2]:
                param_info = properties.get(param_name, {})
                t = param_info.get('type', 'string')
                if t == 'string':
                    example.append(f'{param_name}="..."')
                elif t == 'integer':
                    example.append(f'{param_name}=1')
                elif t == 'number':
                    example.append(f'{param_name}=1.0')
                elif t == 'boolean':
                    example.append(f'{param_name}=true')
                else:
                    example.append(f'{param_name}=value')
            example_str = ' '.join(example)
            console.print(f"  ivybloom run {tool_name} {example_str}  # add --need/--want/--feature as needed")
        else:
            console.print("[yellow]No parameter information available[/yellow]")
            
        console.print()
        console.print(f"[dim]💡 Run 'ivybloom run {tool_name} --help' to execute this tool[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error getting tool info: {e}[/red]")

@tools.command()
@click.argument('tool_name')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def schema(ctx, tool_name, format):
    """Get comprehensive parameter schema for a tool"""
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    # Resolve tool aliases
    resolved_tool_name = resolve_schema_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name
    
    # All schema access now requires authentication
    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = get_tool_schema(tool_name, client)
            
        if not schema_data:
            console.print(f"[red]❌ Schema for '{tool_name}' not found[/red]")
            return
            
        if format == 'json':
            emit_json(schema_data)
        else:
            console.print(f"[bold cyan]{tool_name} schema[/bold cyan]")
            console.print(f"{schema_data.get('description', 'No description available')}")
            console.print()
            
            # Show parameters with detailed information
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
                    
                    table.add_row(param_name, param_type, is_required, description, default)
                
                console.print(table)
                console.print(f"\n[dim]💡 Total: {len(properties)} parameters ({len(required_fields)} required)[/dim]")

                # Completion hints (enums) summary
                enums = extract_enum_choices(schema_data)
                if enums:
                    console.print("\n[bold]Completion hints (choices):[/bold]")
                    for path, choices in enums.items():
                        console.print(f"  • {path}: {', '.join(choices)}")
            else:
                console.print("[yellow]No parameter information available[/yellow]")
                
    except Exception as e:
        console.print(f"[red]❌ Error getting tool schema: {e}[/red]")


@tools.command()
@click.argument('tool_name')
@click.option('--format', default='json', type=click.Choice(['json', 'table']), help='Output format')
@click.option('--path', help='Limit to a specific parameter path (e.g., ligand.input_type)')
@click.pass_context
def completions(ctx, tool_name, format, path):
    """Show completion hints (enum choices) for a tool's parameters

    Outputs enum choices discovered in the tool schema for use by shell completion scripts.
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)

    # Resolve tool aliases
    resolved_tool_name = resolve_schema_tool_name(tool_name)
    if resolved_tool_name != tool_name:
        console.print(f"[dim]Using alias: {tool_name} → {resolved_tool_name}[/dim]")
        tool_name = resolved_tool_name

    if not auth_manager.is_authenticated():
        console.print("[red]❌ Not authenticated. Run 'ivybloom auth login' first.[/red]")
        return

    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            schema_data = get_tool_schema(tool_name, client)

        if not schema_data:
            console.print(f"[red]❌ Schema for '{tool_name}' not found[/red]")
            return

        choices = extract_enum_choices(schema_data)
        if path:
            # Filter by exact path
            choices = {k: v for k, v in choices.items() if k == path}

        if format == 'json':
            emit_json(choices)
        else:
            table = Table(title=f"Completion Hints for {tool_name}")
            table.add_column("Parameter Path", style="green")
            table.add_column("Choices", style="blue")
            if not choices:
                console.print("[yellow]No completion hints available[/yellow]")
                return
            for p, vals in choices.items():
                table.add_row(p, ", ".join(vals))
            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error getting completions: {e}[/red]")

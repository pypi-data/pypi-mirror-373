#!/usr/bin/env python3
"""
IvyBloom CLI - Main entry point
"""

import sys
import click
try:
    from click_didyoumean import DYMGroup
except Exception:
    DYMGroup = click.Group
try:
    import click_completion
except Exception:
    click_completion = None
try:
    from click_repl import repl
except Exception:
    repl = None
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.align import Align

try:
    from . import __version__
    from .utils.config import Config
    from .utils.welcome import show_welcome_screen
    from .utils.colors import get_console
    from .commands.auth import auth
    from .commands.jobs import jobs
    from .commands.projects import projects
    from .commands.tools import tools
    from .commands.run import run
    from .commands.account import account
    from .commands.config import config
    from .commands.workflows import workflows
    from .commands.batch import batch
    from .commands.data import data
    from .utils.auth import AuthManager
    from .utils.test_gate import TestGate
except ImportError:
    # Direct execution - use absolute imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from ivybloom_cli import __version__
    from utils.config import Config
    from utils.welcome import show_welcome_screen
    from commands.auth import auth
    from commands.jobs import jobs
    from commands.projects import projects
    from commands.tools import tools
    from commands.run import run
    from commands.account import account
    from commands.config import config
    from commands.workflows import workflows
    from commands.batch import batch
    from commands.data import data
    from utils.colors import get_console
    from utils.auth import AuthManager

console = get_console()

@click.group(invoke_without_command=True, cls=DYMGroup)
@click.option('--config-file', type=click.Path(), help='Path to configuration file')
@click.option('--api-url', help='API base URL (overrides config)')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output-format', default='table', type=click.Choice(['json', 'yaml', 'table', 'csv']), help='Output format')
@click.option('--timeout', default=30, type=int, help='Request timeout in seconds')
@click.option('--retries', default=3, type=int, help='Number of retry attempts')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-essential output')
@click.option('--no-progress', is_flag=True, help='Disable progress bars and spinners')
@click.option('--offline', is_flag=True, help='Enable offline mode (use cached data)')
@click.option('--profile', is_flag=True, help='Enable performance profiling')
@click.version_option(version=__version__, prog_name='ivybloom')
@click.pass_context
def cli(ctx, config_file, api_url, debug, verbose, output_format, timeout, retries, quiet, no_progress, offline, profile):
    """🌿 IvyBloom CLI

    - Auth:      ivybloom auth login --browser
    - Tools:     ivybloom tools list | ivybloom tools info <tool>
    - Run:       ivybloom run <tool> key=value [key=value ...]
    - Jobs:      ivybloom jobs list | ivybloom jobs status <job_id> --follow
    - Workflows: ivybloom workflows run <file.yaml> --dry-run
    - Shell:     ivybloom shell  (interactive mode if available)

    Tip: use --help on any command for detailed options.
    Docs: https://docs.ivybiosciences.com/cli
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Initialize configuration
    config = Config(config_file)
    if api_url:
        config.set('api_url', api_url)
    if debug:
        config.set('debug', True)
    if verbose:
        config.set('verbose', True)
    if output_format:
        config.set('output_format', output_format)
    if timeout:
        config.set('timeout', timeout)
    if retries:
        config.set('retries', retries)
    if quiet:
        config.set('quiet', True)
    if no_progress:
        config.set('no_progress', True)
    if offline:
        config.set('offline', True)
    if profile:
        config.set('profile', True)
    
    ctx.obj['config'] = config
    ctx.obj['debug'] = debug
    ctx.obj['verbose'] = verbose
    ctx.obj['output_format'] = output_format
    ctx.obj['quiet'] = quiet
    ctx.obj['no_progress'] = no_progress
    ctx.obj['offline'] = offline
    ctx.obj['profile'] = profile

    # Always-on test gating for all CLI invocations (non-TUI as well).
    # Run tests once before executing any subcommand other than the implicit root help/version.
    try:
        gate = TestGate()
        result = gate.run_sync()
        if not result.get('ok'):
            from .utils.colors import print_error, print_warning
            preview = (result.get('output') or '').strip()
            max_chars = int(config.get('cli_test_preview_max_chars', 2000))
            if len(preview) > max_chars:
                preview = preview[-max_chars:]
            header = result.get('summary_line') or 'Tests failed'
            print_error(f"{header}. Fix issues and re-run.")
            if preview:
                console.print(f"[dim]{preview}[/dim]")
            warnings = int(result.get('warnings') or 0)
            if warnings > 0:
                print_warning(f"Warnings: {warnings}")
            raise SystemExit(2)
        else:
            warnings = int(result.get('warnings') or 0)
            summary = result.get('summary_line') or 'All tests passed'
            if warnings > 0:
                console.print(f"[green]{summary}[/green]  [yellow](warnings: {warnings})[/yellow]")
    except SystemExit:
        raise
    except Exception:
        # If gating fails unexpectedly, don't block CLI usage
        pass

    # Show welcome screen if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        show_welcome_screen(__version__)
        click.echo(ctx.get_help())
        return

    # Initialize shell completion (if available) once CLI is invoked
    if click_completion is not None:
        try:
            click_completion.init()
        except Exception:
            pass

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information with welcome screen"""
    show_welcome_screen(__version__)

@cli.command()
def shell():
    """Start an interactive CLI shell (if available)."""
    if repl is None:
        click.echo("Interactive shell not available (click-repl not installed)")
        return
    repl(cli)

@cli.command()
@click.option('--project-id', help='Filter initial view to a specific project')
@click.option('--header/--no-header', default=False, help='Show or hide the header (default hidden)')
@click.option('--footer/--no-footer', default=False, help='Show or hide the footer (default hidden)')
@click.pass_context
def tui(ctx, project_id: str = None, header: bool = False, footer: bool = False):
    """Launch the IvyBloom Text User Interface (TUI).

    A lightweight, brand-aligned terminal UI for monitoring jobs and viewing
    basic details. Think of this as a streamlined alternative to the web app.
    """
    try:
        # Lazy import textual app to keep startup light
        from .tui.app import IvyBloomTUI
    except Exception as e:
        click.echo("Textual TUI not available. Ensure 'textual' is installed.")
        click.echo(f"Details: {e}")
        return

    # Build app with current configuration and auth context
    config = ctx.obj.get('config')
    auth_manager = AuthManager(config)

    app = IvyBloomTUI(
        config=config,
        auth_manager=auth_manager,
        initial_project_id=project_id,
        show_header=header,
        show_footer=footer,
    )
    app.run()

# Add command groups
cli.add_command(auth)
cli.add_command(jobs)
cli.add_command(projects) 
cli.add_command(tools)
cli.add_command(account)
cli.add_command(config)
cli.add_command(workflows)
cli.add_command(batch)
cli.add_command(data)

# Add the run command as a top-level command
cli.add_command(run)

def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        # Route to stderr to avoid contaminating stdout for JSON consumers
        click.echo("Operation cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        # Route to stderr to avoid contaminating stdout for JSON consumers
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
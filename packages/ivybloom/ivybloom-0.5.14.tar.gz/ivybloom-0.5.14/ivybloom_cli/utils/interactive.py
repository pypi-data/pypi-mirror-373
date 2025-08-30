"""
Interactive utilities for IvyBloom CLI.

Lightweight helpers (uses rich + themed console) for:
- List selection with optional filtering and paging
- Project/job action pickers
- Simple prompts (text, choice, multi-select)
- Rendering helpers (panel, key-value table)
"""

from typing import List, Dict, Any, Optional, Callable
try:
    # Optional enhanced prompts
    from InquirerPy import inquirer as _inq
    _INQUIRER_AVAILABLE = True
except Exception:
    _INQUIRER_AVAILABLE = False

from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .colors import get_console

console = get_console()


def _truncate(text: str, max_len: int) -> str:
    if text is None:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def select_from_list(
    items: List[Dict[str, Any]],
    title: str,
    display_key: str = "name",
    id_key: str = "id",
    description_key: Optional[str] = None,
    max_display: int = 10,
    allow_cancel: bool = True,
    enable_search: bool = True,
) -> Optional[str]:
    """Interactive selection from a list with simple filtering and paging.

    Returns the selected item's id or None if cancelled.
    """
    if not items:
        console.print("[yellow]No items available for selection.[/yellow]")
        return None

    # If InquirerPy is available, use a fuzzy finder immediately
    if _INQUIRER_AVAILABLE and len(items) <= 200:
        try:
            choices = [str(it.get(display_key, "")) for it in items]
            result = _inq.fuzzy(message=title, choices=choices).execute()
            # map back to id
            for it in items:
                if str(it.get(display_key, "")) == result:
                    return str(it.get(id_key))
        except Exception:
            pass

    page = 0
    query = ""

    def apply_filter() -> List[Dict[str, Any]]:
        if not enable_search or not query:
            return items
        q = query.lower()
        result = []
        for it in items:
            label = str(it.get(display_key, ""))
            desc = str(it.get(description_key, "")) if description_key else ""
            if q in label.lower() or (description_key and q in desc.lower()):
                result.append(it)
        return result

    while True:
        filtered = apply_filter()
        total = len(filtered)
        start = page * max_display
        end = min(start + max_display, total)
        page_items = filtered[start:end]

        console.print()
        subtitle = f"{total} item(s)" + (f" • filter: '{query}'" if query else "")
        console.print(Panel.fit(Text(title + "\n" + subtitle), border_style="blue"))

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("#", style="cyan", width=4)
        table.add_column("Item", style="white")
        if description_key:
            table.add_column("Description", style="dim")

        for idx, item in enumerate(page_items, 1):
            label = _truncate(str(item.get(display_key, "Unknown")), 60)
            row = [f"{idx}.", label]
            if description_key:
                desc = _truncate(str(item.get(description_key, "")), 80)
                row.append(desc)
            table.add_row(*row)

        console.print(table)

        nav = []
        if start > 0:
            nav.append("p=prev")
        if end < total:
            nav.append("n=next")
        if enable_search:
            nav.append("/=search")
        if allow_cancel:
            nav.append("q=quit")
        nav_help = ", ".join(nav)

        try:
            prompt = f"Select (1-{len(page_items)})" + (f" | {nav_help}" if nav_help else "") + ": "
            response = input(prompt).strip()

            if allow_cancel and response.lower() in {"q", "quit", "exit"}:
                return None
            if response.lower() == "n" and end < total:
                page += 1
                continue
            if response.lower() == "p" and start > 0:
                page -= 1
                continue
            if enable_search and (response.startswith("/") or response.lower() == "s"):
                # Either '/text' or 's' then prompt
                if response.startswith("/"):
                    query = response[1:]
                else:
                    query = input("Filter text: ").strip()
                page = 0
                continue

            choice = int(response)
            if 1 <= choice <= len(page_items):
                selected = page_items[choice - 1]
                return str(selected.get(id_key))
            console.print(f"[red]Enter a number between 1 and {len(page_items)}[/red]")
        except (ValueError, KeyboardInterrupt):
            if allow_cancel:
                return None
            console.print("[red]Invalid input[/red]")


def select_job_action(job_data: Dict[str, Any]) -> Optional[str]:
    """Pick an action to perform on a job."""
    job_id = job_data.get("job_id") or job_data.get("id", "Unknown")
    job_title = job_data.get("job_title", "Untitled")
    job_type = job_data.get("job_type") or job_data.get("tool_name", "Unknown")
    status = job_data.get("status", "Unknown")

    console.print(f"\n[bold cyan]Job Actions for:[/bold cyan]")
    console.print(f"  [cyan]ID:[/cyan] {job_id}")
    console.print(f"  [cyan]Title:[/cyan] {job_title}")
    console.print(f"  [cyan]Type:[/cyan] {job_type}")
    console.print(f"  [cyan]Status:[/cyan] {status}")

    actions: List[Dict[str, Any]] = [
        {"id": "status", "name": "📊 View Status", "description": "Show detailed job status and progress"},
    ]
    if status.upper() in {"COMPLETED", "SUCCESS"}:
        actions.extend([
            {"id": "results", "name": "📄 View Results", "description": "Show job results and metadata"},
            {"id": "download", "name": "📥 Download Files", "description": "Download result files and artifacts"},
        ])
    if status.upper() in {"PENDING", "PROCESSING", "STARTED"}:
        actions.extend([
            {"id": "follow", "name": "👁️  Monitor Live", "description": "Watch job progress in real-time"},
            {"id": "cancel", "name": "❌ Cancel Job", "description": "Cancel the running job"},
        ])

    return select_from_list(
        items=actions,
        title="Available Actions",
        display_key="name",
        id_key="id",
        description_key="description",
        allow_cancel=True,
    )


def select_project_action(project_data: Dict[str, Any]) -> Optional[str]:
    """Pick an action to perform on a project."""
    project_id = project_data.get("project_id") or project_data.get("id", "Unknown")
    project_name = project_data.get("name", "Untitled")

    console.print(f"\n[bold cyan]Project Actions for:[/bold cyan]")
    console.print(f"  [cyan]ID:[/cyan] {project_id}")
    console.print(f"  [cyan]Name:[/cyan] {project_name}")

    actions = [
        {"id": "info", "name": "ℹ️  View Details", "description": "Show detailed project information"},
        {"id": "jobs", "name": "📋 View Jobs", "description": "List all jobs in this project"},
        {"id": "create_job", "name": "🚀 Create Job", "description": "Run a new job in this project"},
    ]

    return select_from_list(
        items=actions,
        title="Available Actions",
        display_key="name",
        id_key="id",
        description_key="description",
        allow_cancel=True,
    )


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for confirmation with y/n prompt."""
    default_text = "Y/n" if default else "y/N"
    prompt = f"{message} ({default_text}): "
    try:
        response = input(prompt).strip().lower()
        if not response:
            return default
        return response in {"y", "yes", "true", "1"}
    except KeyboardInterrupt:
        return False


def prompt_text(message: str, default: Optional[str] = None, validator: Optional[Callable[[str], bool]] = None) -> Optional[str]:
    """Prompt for a line of text, with optional default and validator."""
    prompt = f"{message}"
    if default is not None:
        prompt += f" [{default}]"
    prompt += ": "
    try:
        value = input(prompt)
        if not value and default is not None:
            value = default
        if validator and value is not None and not validator(value):
            console.print("[red]Invalid value[/red]")
            return None
        return value
    except KeyboardInterrupt:
        return None


def prompt_choice(message: str, choices: List[str], default: Optional[str] = None) -> Optional[str]:
    """Prompt to select one from a list of string choices."""
    if default and default not in choices:
        default = None
    choice_text = ", ".join(choices)
    prompt = f"{message} ({choice_text})"
    if default is not None:
        prompt += f" [{default}]"
    prompt += ": "
    try:
        value = input(prompt).strip()
        if not value and default is not None:
            value = default
        if value not in choices:
            console.print("[red]Please choose one of the listed options[/red]")
            return None
        return value
    except KeyboardInterrupt:
        return None


def prompt_multi_select(
    items: List[Dict[str, Any]],
    title: str,
    display_key: str = "name",
    id_key: str = "id",
    description_key: Optional[str] = None,
    max_display: int = 10,
) -> List[str]:
    """Prompt to select multiple items by entering comma-separated numbers.

    Returns a list of selected ids. Empty on cancel/invalid.
    """
    if not items:
        console.print("[yellow]No items to select[/yellow]")
        return []

    console.print(Panel.fit(Text(title), border_style="blue"))
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("#", style="cyan", width=4)
    table.add_column("Item", style="white")
    if description_key:
        table.add_column("Description", style="dim")

    display_items = items[:max_display]
    for i, item in enumerate(display_items, 1):
        label = _truncate(str(item.get(display_key, "Unknown")), 60)
        row = [f"{i}.", label]
        if description_key:
            desc = _truncate(str(item.get(description_key, "")), 80)
            row.append(desc)
        table.add_row(*row)
    console.print(table)

    try:
        raw = input(f"Select one or more (e.g., 1,3,4) [max {len(display_items)}]: ").strip()
        if not raw:
            return []
        selected: List[str] = []
        for tok in raw.split(','):
            tok = tok.strip()
            if not tok:
                continue
            idx = int(tok)
            if 1 <= idx <= len(display_items):
                selected.append(str(display_items[idx - 1].get(id_key)))
        return selected
    except (ValueError, KeyboardInterrupt):
        return []


def render_panel(title: str, lines: List[str], border_style: str = "blue") -> None:
    """Render a simple panel with multiple lines of text."""
    text = "\n".join(lines)
    console.print(Panel.fit(Text(text), title=title, border_style=border_style))


def render_kv_table(title: str, rows: List[Dict[str, str]]) -> None:
    """Render a simple key-value table. Each row is {key, value}."""
    table = Table(title=title)
    table.add_column("Key", style="cyan", width=24)
    table.add_column("Value", style="white")
    for row in rows:
        table.add_row(str(row.get("key", "")), str(row.get("value", "")))
    console.print(table)
"""
Interactive helpers for CLI (selection and completion scaffolding).

Note: Minimal scaffolding to avoid adding heavy runtime deps.
"""

from typing import List, Dict, Any, Optional

def select_from_list(items: List[Dict[str, Any]], title: str, display_key: str, id_key: str, description_key: Optional[str] = None) -> Optional[str]:
    """Simple selection helper placeholder.

    Returns the id_key of the first item (placeholder to keep API intact without TUI deps).
    """
    if not items:
        return None
    return items[0].get(id_key)


def select_job_action(job_data: Dict[str, Any]) -> Optional[str]:
    """Return a default action as placeholder.
    """
    return 'status'


def confirm_action(message: str, default: bool = False) -> bool:
    """Non-interactive confirm placeholder.
    """
    return default

"""
Interactive utilities for IvyBloom CLI
"""

import sys
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def select_from_list(
    items: List[Dict[str, Any]], 
    title: str,
    display_key: str = 'name',
    id_key: str = 'id',
    description_key: Optional[str] = None,
    max_display: int = 10,
    allow_cancel: bool = True
) -> Optional[str]:
    """
    Interactive selection from a list using arrow keys (fallback to number selection)
    
    Args:
        items: List of dictionaries containing selectable items
        title: Title to display above the selection
        display_key: Key to use for display text
        id_key: Key to use for return value
        description_key: Optional key for additional description
        max_display: Maximum items to display at once
        allow_cancel: Whether to allow canceling selection
    
    Returns:
        Selected item ID or None if cancelled
    """
    if not items:
        console.print(f"[yellow]No items available for selection.[/yellow]")
        return None
    
    # For now, implement a simple numbered selection
    # TODO: Add proper arrow key navigation with a library like inquirer
    return _numbered_selection(items, title, display_key, id_key, description_key, max_display, allow_cancel)

def _numbered_selection(
    items: List[Dict[str, Any]], 
    title: str,
    display_key: str,
    id_key: str,
    description_key: Optional[str],
    max_display: int,
    allow_cancel: bool
) -> Optional[str]:
    """Numbered selection interface"""
    
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print()
    
    # Display items with numbers
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Number", style="cyan", width=4)
    table.add_column("Item", style="white")
    if description_key:
        table.add_column("Description", style="dim")
    
    display_items = items[:max_display]
    
    for i, item in enumerate(display_items, 1):
        display_text = str(item.get(display_key, 'Unknown'))
        row = [f"{i}.", display_text]
        
        if description_key:
            desc = str(item.get(description_key, ''))
            if len(desc) > 50:
                desc = desc[:47] + "..."
            row.append(desc)
        
        table.add_row(*row)
    
    console.print(table)
    
    if len(items) > max_display:
        console.print(f"[dim]... and {len(items) - max_display} more items[/dim]")
    
    console.print()
    
    # Get user selection
    while True:
        if allow_cancel:
            prompt_text = f"Select an item (1-{len(display_items)}) or 'q' to quit: "
        else:
            prompt_text = f"Select an item (1-{len(display_items)}): "
        
        try:
            response = input(prompt_text).strip().lower()
            
            if allow_cancel and response in ['q', 'quit', 'cancel', '']:
                return None
            
            selection = int(response)
            if 1 <= selection <= len(display_items):
                selected_item = display_items[selection - 1]
                return str(selected_item.get(id_key))
            else:
                console.print(f"[red]Please enter a number between 1 and {len(display_items)}[/red]")
                
        except (ValueError, KeyboardInterrupt):
            if allow_cancel:
                return None
            console.print("[red]Please enter a valid number[/red]")

def select_job_action(job_data: Dict[str, Any]) -> Optional[str]:
    """
    Select an action to perform on a job
    
    Args:
        job_data: Job information dictionary
        
    Returns:
        Selected action or None if cancelled
    """
    job_id = job_data.get('job_id') or job_data.get('id', 'Unknown')
    job_title = job_data.get('job_title', 'Untitled')
    job_type = job_data.get('job_type') or job_data.get('tool_name', 'Unknown')
    status = job_data.get('status', 'Unknown')
    
    # Show job info
    console.print(f"\n[bold cyan]Job Actions for:[/bold cyan]")
    console.print(f"  [cyan]ID:[/cyan] {job_id}")
    console.print(f"  [cyan]Title:[/cyan] {job_title}")
    console.print(f"  [cyan]Type:[/cyan] {job_type}")
    console.print(f"  [cyan]Status:[/cyan] {status}")
    console.print()
    
    # Available actions based on job status
    actions = []
    
    # Always available
    actions.append({
        'id': 'status',
        'name': '📊 View Status',
        'description': 'Show detailed job status and progress'
    })
    
    # For completed jobs
    if status.upper() in ['COMPLETED', 'SUCCESS']:
        actions.extend([
            {
                'id': 'results',
                'name': '📄 View Results',
                'description': 'Show job results and metadata'
            },
            {
                'id': 'download',
                'name': '📥 Download Files',
                'description': 'Download result files and artifacts'
            }
        ])
    
    # For running jobs
    if status.upper() in ['PENDING', 'PROCESSING', 'STARTED']:
        actions.extend([
            {
                'id': 'follow',
                'name': '👁️  Monitor Live',
                'description': 'Watch job progress in real-time'
            },
            {
                'id': 'cancel',
                'name': '❌ Cancel Job',
                'description': 'Cancel the running job'
            }
        ])
    
    return select_from_list(
        items=actions,
        title="Available Actions",
        display_key='name',
        id_key='id',
        description_key='description',
        allow_cancel=True
    )

def select_project_action(project_data: Dict[str, Any]) -> Optional[str]:
    """
    Select an action to perform on a project
    
    Args:
        project_data: Project information dictionary
        
    Returns:
        Selected action or None if cancelled
    """
    project_id = project_data.get('project_id') or project_data.get('id', 'Unknown')
    project_name = project_data.get('name', 'Untitled')
    
    # Show project info
    console.print(f"\n[bold cyan]Project Actions for:[/bold cyan]")
    console.print(f"  [cyan]ID:[/cyan] {project_id}")
    console.print(f"  [cyan]Name:[/cyan] {project_name}")
    console.print()
    
    actions = [
        {
            'id': 'info',
            'name': 'ℹ️  View Details',
            'description': 'Show detailed project information'
        },
        {
            'id': 'jobs',
            'name': '📋 View Jobs',
            'description': 'List all jobs in this project'
        },
        {
            'id': 'create_job',
            'name': '🚀 Create Job',
            'description': 'Run a new job in this project'
        }
    ]
    
    return select_from_list(
        items=actions,
        title="Available Actions",
        display_key='name',
        id_key='id',
        description_key='description',
        allow_cancel=True
    )

def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask for confirmation with y/n prompt
    
    Args:
        message: Confirmation message
        default: Default value if user just presses enter
        
    Returns:
        True if confirmed, False otherwise
    """
    default_text = "Y/n" if default else "y/N"
    prompt = f"{message} ({default_text}): "
    
    try:
        response = input(prompt).strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
        
    except KeyboardInterrupt:
        return False

"""Visualization utilities for different artifact types."""

from typing import Any, Dict, List, Optional, Union
import json
import os

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class ArtifactVisualizer:
    """Visualize different types of artifacts."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize the artifact visualizer.
        
        Args:
            console: Rich console for rendering
        """
        self.console = console or Console()

    def visualize_json(self, content: Union[str, bytes], filename: str = "data.json") -> Union[str, Panel, Tree]:
        """Visualize JSON content.
        
        Args:
            content: JSON content as string or bytes
            filename: Name of the file
            
        Returns:
            Rich-compatible visualization object
        """
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
            
        try:
            # Parse the JSON
            data = json.loads(content)
            
            # If it's a small object, use Syntax for syntax highlighting
            if len(content) < 10000:
                pretty_json = json.dumps(data, indent=2)
                syntax = Syntax(pretty_json, "json", theme="monokai", line_numbers=True)
                return Panel(syntax, title=f"JSON: {filename}", border_style="blue")
            
            # For larger JSON objects, create a tree view
            if isinstance(data, dict):
                tree = Tree(f"[bold blue]{filename}[/bold blue]")
                self._build_json_tree(data, tree)
                return tree
            elif isinstance(data, list):
                tree = Tree(f"[bold blue]{filename}[/bold blue] [dim](Array with {len(data)} items)[/dim]")
                for i, item in enumerate(data[:100]):  # Limit to first 100 items
                    if isinstance(item, (dict, list)):
                        subtree = tree.add(f"[yellow]Item {i}[/yellow]")
                        self._build_json_tree(item, subtree, max_depth=2)
                    else:
                        tree.add(f"Item {i}: {str(item)[:100]}")
                if len(data) > 100:
                    tree.add(f"[dim]...and {len(data) - 100} more items[/dim]")
                return tree
            else:
                return f"JSON content: {str(data)[:1000]}"
        except json.JSONDecodeError:
            return f"Invalid JSON content in {filename}"
    
    def _build_json_tree(self, data: Union[Dict, List], tree: Tree, max_depth: int = 3, current_depth: int = 0) -> None:
        """Build a tree representation of JSON data.
        
        Args:
            data: JSON data as dict or list
            tree: Rich Tree to add nodes to
            max_depth: Maximum depth to render
            current_depth: Current depth in the tree
        """
        if current_depth >= max_depth:
            if isinstance(data, dict):
                tree.add(f"[dim]...and {len(data)} more key-value pairs[/dim]")
            elif isinstance(data, list):
                tree.add(f"[dim]...and {len(data)} more items[/dim]")
            return
            
        if isinstance(data, dict):
            for key, value in list(data.items())[:50]:  # Limit to first 50 keys
                if isinstance(value, (dict, list)):
                    subtree = tree.add(f"[green]{key}[/green]")
                    self._build_json_tree(value, subtree, max_depth, current_depth + 1)
                else:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    tree.add(f"[green]{key}[/green]: {value_str}")
            if len(data) > 50:
                tree.add(f"[dim]...and {len(data) - 50} more keys[/dim]")
        elif isinstance(data, list):
            for i, item in enumerate(data[:50]):  # Limit to first 50 items
                if isinstance(item, (dict, list)):
                    subtree = tree.add(f"[yellow]Item {i}[/yellow]")
                    self._build_json_tree(item, subtree, max_depth, current_depth + 1)
                else:
                    item_str = str(item)
                    if len(item_str) > 100:
                        item_str = item_str[:100] + "..."
                    tree.add(f"[yellow]Item {i}[/yellow]: {item_str}")
            if len(data) > 50:
                tree.add(f"[dim]...and {len(data) - 50} more items[/dim]")

    def visualize_txt(self, content: Union[str, bytes], filename: str = "data.txt") -> Panel:
        """Visualize text content.
        
        Args:
            content: Text content as string or bytes
            filename: Name of the file
            
        Returns:
            Rich Panel with text visualization
        """
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
            
        # Determine if this is a structured text format
        lines = content.splitlines()
        
        # If file is too large, show only first 200 lines
        if len(lines) > 200:
            truncated_content = "\n".join(lines[:200])
            truncated_content += f"\n\n[dim]... (truncated, {len(lines) - 200} more lines)[/dim]"
        else:
            truncated_content = content
            
        # Use syntax highlighting based on file extension
        extension = os.path.splitext(filename)[1].lower()
        lexer = None
        
        if extension in {'.py', '.pyw'}:
            lexer = 'python'
        elif extension in {'.js', '.jsx'}:
            lexer = 'javascript'
        elif extension in {'.ts', '.tsx'}:
            lexer = 'typescript'
        elif extension in {'.html', '.htm'}:
            lexer = 'html'
        elif extension in {'.css'}:
            lexer = 'css'
        elif extension in {'.md', '.markdown'}:
            lexer = 'markdown'
        elif extension in {'.yml', '.yaml'}:
            lexer = 'yaml'
        elif extension in {'.xml'}:
            lexer = 'xml'
        elif extension in {'.sh', '.bash'}:
            lexer = 'bash'
        elif extension in {'.sql'}:
            lexer = 'sql'
        elif extension in {'.r'}:
            lexer = 'r'
        elif extension in {'.java'}:
            lexer = 'java'
        elif extension in {'.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hh', '.h'}:
            lexer = 'cpp'
        elif extension in {'.c', '.h'}:
            lexer = 'c'
        elif extension in {'.go'}:
            lexer = 'go'
        elif extension in {'.rs'}:
            lexer = 'rust'
        
        if lexer:
            syntax = Syntax(truncated_content, lexer, theme="monokai", line_numbers=True)
            return Panel(syntax, title=f"Text: {filename}", border_style="cyan")
        else:
            return Panel(Text(truncated_content), title=f"Text: {filename}", border_style="cyan")


def visualize_json(content: Union[str, bytes], filename: str = "data.json") -> Union[str, Panel, Tree]:
    """Visualize JSON content.
    
    Args:
        content: JSON content as string or bytes
        filename: Name of the file
        
    Returns:
        Rich-compatible visualization object
    """
    visualizer = ArtifactVisualizer()
    return visualizer.visualize_json(content, filename)


def visualize_txt(content: Union[str, bytes], filename: str = "data.txt") -> Panel:
    """Visualize text content.
    
    Args:
        content: Text content as string or bytes
        filename: Name of the file
        
    Returns:
        Rich Panel with text visualization
    """
    visualizer = ArtifactVisualizer()
    return visualizer.visualize_txt(content, filename)

"""
Earth tone color scheme for IvyBloom CLI
Provides consistent color palette across all CLI components
"""

from rich.console import Console
from rich.theme import Theme
from typing import Dict, Any

# Custom earth tone color palette - Ivy Biosciences Brand Colors
EARTH_TONES = {
    # Primary sage greens
    "sage_dark": "#4A5D4C",      # Deep sage
    "sage_medium": "#739177",     # Medium sage  
    "sage_light": "#8FA98F",      # Light sage
    "sage_pale": "#A3B899",       # Pale sage
    "sage_mist": "#C7D3C5",       # Sage mist
    
    # Warm earth tones
    "earth_warm": "#A49592",      # Warm earth
    "earth_deep": "#8E7267",      # Deep earth
    "earth_cream": "#D6C3B6",     # Cream earth
    "earth_tan": "#C8B6A6",       # Tan earth
    "earth_brown": "#A67F5D",     # Brown earth
    
    # Cool earth tones
    "cool_gray": "#8B8C89",       # Cool gray
    "cool_blue": "#9BA0A3",       # Cool blue-gray
    "cool_light": "#C5CCD3",      # Light cool
    "cool_medium": "#B4B7BA",     # Medium cool
    "cool_muted": "#A6A5A2",      # Muted cool
    
    # Muted sage variants
    "muted_beige": "#B2A59F",     # Muted beige
    "muted_green": "#8B9D77",     # Muted green
    "muted_gold": "#D4B08C",      # Muted gold
    "muted_olive": "#94A187",     # Muted olive
    "muted_sage": "#B6AD9A",      # Muted sage
    
    # Warm neutrals
    "neutral_cream": "#E6D5C7",   # Cream neutral
    "neutral_tan": "#C4B7A6",     # Tan neutral
    "neutral_rose": "#B79B8F",    # Rose neutral
    "neutral_brown": "#9F8B82",   # Brown neutral
    "neutral_warm": "#D1C2B3",    # Warm neutral
    
    # Status colors using palette
    "success": "#739177",         # Medium sage for success
    "warning": "#D4B08C",         # Muted gold for warnings
    "error": "#B79B8F",           # Rose neutral for errors
    "info": "#8FA98F",            # Light sage for info
    
    # UI element colors
    "accent": "#4A5D4C",          # Deep sage accent
    "secondary": "#A3B899",       # Pale sage secondary
    "muted": "#A6A5A2",           # Cool muted for less important text
    "bright": "#E6D5C7",          # Cream for highlights
}

# Rich theme configuration with new color palette
EARTH_TONE_THEME = Theme({
    # Basic styling
    "info": EARTH_TONES["info"],
    "warning": EARTH_TONES["warning"], 
    "error": EARTH_TONES["error"],
    "success": EARTH_TONES["success"],
    
    # CLI-specific styles
    "cli.title": f"bold {EARTH_TONES['accent']}",           # Deep sage
    "cli.subtitle": EARTH_TONES["secondary"],               # Pale sage
    "cli.accent": EARTH_TONES["accent"],                    # Deep sage
    "cli.muted": EARTH_TONES["muted"],                      # Cool muted
    "cli.bright": f"bold {EARTH_TONES['bright']}",          # Cream highlights
    
    # Job status colors
    "job.running": EARTH_TONES["sage_medium"],              # Medium sage
    "job.completed": EARTH_TONES["success"],                # Medium sage
    "job.failed": EARTH_TONES["error"],                     # Rose neutral
    "job.pending": EARTH_TONES["cool_medium"],              # Medium cool
    "job.cancelled": EARTH_TONES["warning"],                # Muted gold
    
    # Table styling
    "table.header": f"bold {EARTH_TONES['sage_dark']}",     # Deep sage headers
    "table.row": EARTH_TONES["muted"],                      # Cool muted rows
    "table.border": EARTH_TONES["sage_pale"],               # Pale sage borders
    
    # Progress indicators
    "progress.bar": EARTH_TONES["sage_medium"],             # Medium sage progress
    "progress.percentage": EARTH_TONES["accent"],           # Deep sage percentage
    "progress.description": EARTH_TONES["muted"],           # Cool muted description
    
    # Welcome screen (using new palette)
    "welcome.art": EARTH_TONES["sage_medium"],              # Medium sage for art
    "welcome.text": f"bold {EARTH_TONES['earth_warm']}",    # Warm earth for text
    "welcome.border": EARTH_TONES["muted_gold"],            # Muted gold border
    
    # Authentication styles
    "auth.success": EARTH_TONES["success"],                 # Medium sage
    "auth.error": EARTH_TONES["error"],                     # Rose neutral
    "auth.info": EARTH_TONES["sage_light"],                 # Light sage
    
    # Tool-specific colors
    "tool.protein": EARTH_TONES["sage_medium"],             # Protein tools
    "tool.chemistry": EARTH_TONES["muted_gold"],            # Chemistry tools
    "tool.analysis": EARTH_TONES["cool_blue"],              # Analysis tools
})

def get_console() -> Console:
    """Get console instance with earth tone theme"""
    return Console(theme=EARTH_TONE_THEME)

def get_status_color(status: str) -> str:
    """Get color for job status"""
    status_colors = {
        "running": EARTH_TONES["sage_medium"],     # Medium sage for running
        "completed": EARTH_TONES["success"],       # Medium sage for success
        "failed": EARTH_TONES["error"],            # Rose neutral for errors
        "pending": EARTH_TONES["muted"],           # Cool muted for pending
        "cancelled": EARTH_TONES["warning"],       # Muted gold for cancelled
        "queued": EARTH_TONES["cool_medium"],      # Medium cool for queued
    }
    return status_colors.get(status.lower(), EARTH_TONES["muted"])

def get_tool_color(tool_name: str) -> str:
    """Get color for different tool types"""
    # Different earth tones for different tool categories
    tool_colors = {
        # Protein tools
        "esmfold": EARTH_TONES["sage_medium"],
        "alphafold": EARTH_TONES["sage_dark"],
        "protox3": EARTH_TONES["earth_warm"],
        
        # Chemistry tools
        "reinvent": EARTH_TONES["muted_gold"],
        "admetlab3": EARTH_TONES["earth_brown"],
        "aizynthfinder": EARTH_TONES["neutral_cream"],
        
        # Analysis tools
        "deepsol": EARTH_TONES["cool_blue"],
        "deeppurpose": EARTH_TONES["muted_olive"],
        "fragment_library": EARTH_TONES["neutral_tan"],
        
        # Default
        "default": EARTH_TONES["accent"]
    }
    return tool_colors.get(tool_name.lower(), tool_colors["default"])

def format_status_icon(status: str) -> str:
    """Get status icon with earth tone styling"""
    icons = {
        "running": f"[{get_status_color(status)}]⚡[/{get_status_color(status)}]",
        "completed": f"[{get_status_color(status)}]✅[/{get_status_color(status)}]",
        "failed": f"[{get_status_color(status)}]❌[/{get_status_color(status)}]",
        "pending": f"[{get_status_color(status)}]⏳[/{get_status_color(status)}]",
        "cancelled": f"[{get_status_color(status)}]🚫[/{get_status_color(status)}]",
        "queued": f"[{get_status_color(status)}]📋[/{get_status_color(status)}]",
    }
    return icons.get(status.lower(), f"[{EARTH_TONES['muted']}]❓[/{EARTH_TONES['muted']}]")

def print_success(message: str, console: Console = None) -> None:
    """Print success message with earth tone styling"""
    if console is None:
        console = get_console()
    console.print(f"[success]✅ {message}[/success]")

def print_error(message: str, console: Console = None) -> None:
    """Print error message with earth tone styling"""
    if console is None:
        console = get_console()
    console.print(f"[error]❌ {message}[/error]")

def print_warning(message: str, console: Console = None) -> None:
    """Print warning message with earth tone styling"""
    if console is None:
        console = get_console()
    console.print(f"[warning]⚠️  {message}[/warning]")

def print_info(message: str, console: Console = None) -> None:
    """Print info message with earth tone styling"""
    if console is None:
        console = get_console()
    console.print(f"[info]ℹ️  {message}[/info]")
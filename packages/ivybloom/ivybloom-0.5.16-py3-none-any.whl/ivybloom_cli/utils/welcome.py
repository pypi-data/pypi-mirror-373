"""
Welcome screen display for ivybloom CLI
"""

import shutil
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich import box
from .colors import get_console

console = get_console()

def get_terminal_width() -> int:
    """Get current terminal width"""
    return shutil.get_terminal_size().columns

def load_ivy_leaf_art() -> str:
    """Load the elegant text-based ivy leaf design"""
    return """                  `    `  `          `            
 ¨¨¨¨¨¨¨¨¨…¨¨…¨¨¨¨¨¨¨¨¨¨¨¨¨   ›Æ…¨x  ¨¨¨¨¨¨¨¨¨¨¨¨ 
 ¨¨¨¨¨¸¨¨¸¨¨¨¨¨ˆ¨¨¨¨¨¨¨     ’Æ+ | ì“ `¨¨¨¨¨¨¨¨¨¨¨ 
`¨·¨¨¨…¸¨¨¸¨¨¨¨¨¨¨¨…    ­ÝFâ—  †¨  t  ¨¨ˆ·¨¨¨…ˆ¨¨ 
 ¨¨¨¨¨¨¨ˆ¨…¨¨…¨¨…ˆ`` ÆÆ `  `¿``—h;+/  ´¨¨¨¨¨¨¨´¨¨ 
`¨¨¨´´``´´´¨¨¨¨¨´  f¡ ¹ ›¡:›| < ·%…:t  ¨¨¨¨¨¨¨¨…¨ 
 ¨¨¨   `     ``¨  Æ  ·¹· J ‚’`8¸`  †Æ¸ `¨¨¨ˆ¨¨¨¨´ 
 ¨¨¨ ;—¬×aé&©    o‘`º/;×  µ  ¾; ä``  1  ´¨¨¨¨¨¨¨¨ 
 ¨¨´ ë¸}‰` {z¨Æ‰ ç …`~’÷r‘t~G   ·D‰/…¥Ì  ¨¨¨¨¨¨¨¨ 
 ¨·  è‹ `n¹ ¯`•  c 7·2  » `}`£0   ˆ`:*`Æ ¨¨¨¨¨¨¨¨`
 ¨¨ í  ‰7…9  ¨ í¸…¸˜ j¹‚ ’·O  ¸7i… ù˜ w  ¨¨¨¨¨¨ˆ¨`
 ¨¨ û;‚    ~·  <)` “ˆ †˜ ­Ï  %’ ˆž  tÍ­ `¨ˆ·¨ˆ¨¨¨ 
 ˆ¨ z )`· ˆ’7C`+“ˆ ” ’? `J  `º?x `·¢Y   ¨¨¨¨¨¨¨¨¨ 
 ´¨  ý  âÝßµ¤’|ï•  I‚ × á ˜é´  • ¨:²          `¨¨ 
`¨…  yˆˆ `     «ú  ì­²·ö½‘ ¸»¸“ ?{¸ûpD¬±yÐF§u   ´ 
 ¨` ùº˜˜ ‚  ` ` `^5´ `ü` °*`  4L`¸`   ˆ  ÷ `¹´Ý`` 
`¨ °ò /i“¢Ï±4—%òˆ` J ƒ `   ˆI¸ ` ¹•~Ìh{ƒ¡l  ´86 ` 
`¨  Ý?~˜     ÷¦i   Jv±hÿ×º¬=³¬‰‹„` ˜ª     %Á“   ``
`¨´   `{g|  ¨  ¨¹Mc †~ {´  ’   ´¼ º  [<J»ôY   ¨¨´`
 ¨¨·´`    Æ$fäÆî   ˆ`ò ) U¨``s`…^’L|›´ `D   ´´…¨¨ 
 ¨¨¨·¨¨¨´  ` `    ±: æ  ª`in¿ º¨L  ¿¿Æá``  ´…´¨´¨ 
 ¨¨¨¨¨¨¨¨´¨´…¸¨  (< `‚ƒ ˜ ¦`©`÷í¨3S`    `´…´¨¨¨¨¨ 
 ´ˆ¨¨¨·¨¨¨…´¨`  <@    ì–`± · ˜ ‘I    ¨¨¨…´¨¨¨¨¨¨¨ 
 ¨¨¨¨¨¨¨¨¨´´   xi  ¨´  ·hV”˜ r`(° ´¨ˆ¨¨¨¨¨ˆ¨¨¨¨¨¨ 
 ¨¨¨ˆ¨…¨¨    xÚ`  …¨¨¨`    ”Æø#   ¨¨¨¨·¨¨¨¨¨¨¨ˆ¨´ 
 ¨¨¨¨¨¨¨  ˜èQº  `¨¨¨¨¨¨¨¨´`   ` `¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨ 
 `        ``    `             `   `       ``      """

def load_compact_art() -> str:
    """Load compact version for narrow terminals"""
    return """🌿 ivybloom"""

def show_welcome_screen(version: str = "0.3.0", force_compact: bool = False) -> None:
    """Display welcome screen with ASCII art and a minimal panel.
    Extra usage details are intentionally deferred to '--help'.
    """

    # Render ASCII art at the top
    ascii_art = load_ivy_leaf_art()
    console.print()
    console.print(Align.center(Text(ascii_art, style="welcome.art")))
    console.print()

    # Minimal guidance only
    welcome_text = (
        f"🌿 [cli.title]ivybloom CLI v{version}[/cli.title]\n"
        "[welcome.text]Computational Biology & Drug Discovery[/welcome.text]\n\n"
        "Run [cli.accent]ivybloom --help[/cli.accent] for usage"
    )
    panel = Panel(
        Align.left(Text.from_markup(welcome_text)),
        title="🌿 ivybloom",
        border_style="welcome.border",
        box=box.ROUNDED,
        padding=(1, 2),
        width=min(68, get_terminal_width() - 4)
    )

    console.print(Align.center(panel))
    console.print()

def show_welcome_panel(version: str = "0.3.0") -> None:
    """Show welcome screen in a concise bordered panel (used by 'version' command)."""

    welcome_text = (
        f"🌿 ivybloom CLI v{version}\n"
        "Computational Biology & Drug Discovery\n\n"
        "Run 'ivybloom --help' for usage"
    )

    panel = Panel(
        Align.left(Text(welcome_text, style="green")),
        title="🌿 ivybloom CLI",
        title_align="center",
        border_style="welcome.border",
        box=box.ROUNDED,
        padding=(1, 2),
        width=min(68, get_terminal_width() - 4)
    )

    console.print()
    console.print(Align.center(panel))
    console.print()
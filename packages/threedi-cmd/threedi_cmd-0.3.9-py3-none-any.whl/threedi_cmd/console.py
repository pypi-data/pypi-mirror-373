from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "black",
        "success": "bold spring_green4",
        "warning": "bold gold3",
        "error": "bold red3",
    }
)

console = Console(theme=custom_theme)

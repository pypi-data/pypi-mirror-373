from dataclasses import dataclass
from typing import Dict, Optional

import typer


@dataclass
class AppMeta:
    app: typer.Typer
    name: str
    help: str
    add_to: Optional[str] = ""


@dataclass
class AppRegistry:
    apps: Dict[str, AppMeta]

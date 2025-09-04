from __future__ import annotations
import os
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


from rich.console import Console

console = Console()


HOME = Path.home()
CACHE_ROOT = Path(os.getenv("AGENTHUB_CACHE_DIR", HOME / ".cache" / "agenthub"))
AGENTS_DIR = CACHE_ROOT / "agents"
DOCKER_DIR = CACHE_ROOT / "docker"
INDEX_FILE = CACHE_ROOT / "index.json"
TOKEN_FILE = Path(os.getenv("AGENTHUB_TOKEN_FILE", HOME / ".agenthub" / "token"))


# Default base URL for your repo API (replace with your real endpoint)
DEFAULT_BASE_URL = os.getenv("AGENTHUB_BASE_URL", "https://api.agenthub.local/v1")




def ensure_dirs() -> None:
    (CACHE_ROOT).mkdir(parents=True, exist_ok=True)
    (AGENTS_DIR).mkdir(parents=True, exist_ok=True)
    (DOCKER_DIR).mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("{}", encoding="utf-8")

def load_index() -> Dict[str, Any]:
    ensure_dirs()
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}




def save_index(data: Dict[str, Any]) -> None:
    ensure_dirs()
    INDEX_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")




def set_token(token: str) -> None:
    ensure_dirs()
    TOKEN_FILE.write_text(token.strip() + "\n", encoding="utf-8")
    # Best-effort secure perms on POSIX
    if os.name == "posix":
        try:
            os.chmod(TOKEN_FILE, 0o600)
        except Exception:
            pass




def get_token() -> Optional[str]:
    if TOKEN_FILE.exists():
        try:
            return TOKEN_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            return None
    return None




def clear_token() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink(missing_ok=True)

@dataclass
class Settings:
    base_url: str = DEFAULT_BASE_URL
    cache_root: Path = CACHE_ROOT
    agents_dir: Path = AGENTS_DIR
    docker_dir: Path = DOCKER_DIR
    index_file: Path = INDEX_FILE
    token_file: Path = TOKEN_FILE


@classmethod
def load(cls) -> "Settings":
    ensure_dirs()
    return cls()
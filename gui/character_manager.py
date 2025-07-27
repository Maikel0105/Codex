# Character management utilities
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent
CHAR_DIR = BASE_DIR / 'characters'
CHAR_DIR.mkdir(exist_ok=True)

@dataclass
class Character:
    """Represents a chat character"""
    name: str
    description: str = ''
    memory: str = ''
    nsfw: bool = False
    avatar: str = ''  # path to avatar image

    def save(self):
        """Save character to JSON file"""
        path = CHAR_DIR / f"{self.name}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)

    @staticmethod
    def load(name: str) -> 'Character':
        """Load character by name"""
        path = CHAR_DIR / f"{name}.json"
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Character(**data)

    @staticmethod
    def list_characters() -> List[str]:
        """Return available character names"""
        return [p.stem for p in CHAR_DIR.glob('*.json')]

# Optional imports for fetching info
try:
    import wikipedia
    from duckduckgo_search import DDGS
except Exception:
    wikipedia = None
    DDGS = None


def autofill_character(name: str) -> Character:
    """Create character with info from Wikipedia or DuckDuckGo"""
    desc = ''
    if wikipedia:
        try:
            desc = wikipedia.summary(name, sentences=2)
        except Exception:
            desc = ''
    if not desc and DDGS:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(name, max_results=1):
                    desc = r.get('body', '')
                    break
        except Exception:
            pass
    return Character(name=name, description=desc)

"""Language style registry — dynamic plugin loader.

Discovers language modules in style/*.py and registers them.
New language = new file, zero changes to existing code.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional

from style.base import LanguageStyle


class StyleRegistry:
    """Singleton registry of language style plugins."""

    _instance = None
    _styles: Dict[str, LanguageStyle] = {}
    _ext_map: Dict[str, str] = {}  # extension → language name
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _discover(self):
        """Auto-import all modules in style/ package."""
        if self._loaded:
            return
        self._loaded = True

        package_dir = Path(__file__).parent
        for _, name, _ in pkgutil.iter_modules([str(package_dir)]):
            if name.startswith("_") or name in ("base", "registry"):
                continue
            try:
                mod = importlib.import_module(f"style.{name}")
                # Look for LanguageStyle subclasses
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (isinstance(attr, type)
                            and issubclass(attr, LanguageStyle)
                            and attr is not LanguageStyle):
                        instance = attr()
                        self.register(instance)
            except Exception as e:
                print(f"[style registry] failed to load {name}: {e}")

    def register(self, style: LanguageStyle):
        """Register a language style."""
        self._styles[style.name.lower()] = style
        for ext in style.file_extensions:
            self._ext_map[ext.lower()] = style.name.lower()

    def get(self, language: str) -> Optional[LanguageStyle]:
        """Get style by language name."""
        self._discover()
        return self._styles.get(language.lower().strip())

    def get_by_extension(self, ext: str) -> Optional[LanguageStyle]:
        """Get style by file extension."""
        self._discover()
        lang = self._ext_map.get(ext.lower())
        if lang:
            return self._styles.get(lang)
        return None

    def list_languages(self) -> List[str]:
        """List all registered languages."""
        self._discover()
        return sorted(self._styles.keys())

    def list_all(self) -> List[dict]:
        """List all registered languages with their configs."""
        self._discover()
        return [
            {"name": s.name, "extensions": s.file_extensions,
             "max_line": s.max_line_length, "indent": s.indent_size}
            for s in sorted(self._styles.values(), key=lambda x: x.name)
        ]


# Global singleton
registry = StyleRegistry()

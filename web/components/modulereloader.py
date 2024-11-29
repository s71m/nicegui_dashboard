import os
import sys
import importlib
from pathlib import Path
from loguru import logger


class ModuleReloader:
    def __init__(self):
        """
        Reloading current running project modules.
        """
        current_file = Path(__file__).resolve()
        self.project_root = current_file.parent.parent.parent

        self.modules_to_reload = set()

    def get_project_modules(self):
        """
        Get list of currently running project modules excluding venv and external packages

        Returns:
            list: List of project module names
        """
        project_root = Path(self.project_root).resolve()
        venv_path = Path(os.getenv("VIRTUAL_ENV"))
        # venv_path = project_root / "venv"

        project_modules = []

        for name, module in sys.modules.items():
            # Skip modules without a file path
            if not hasattr(module, '__file__') or module.__file__ is None:
                continue

            module_path = Path(module.__file__).resolve()

            # Check if module is within project root but not in venv
            if (project_root in module_path.parents and
                    venv_path not in module_path.parents):
                # Get relative path from project root
                rel_path = module_path.relative_to(project_root)
                project_modules.append({
                    'name': name,
                    'path': str(rel_path)
                })

        return project_modules


    def reload_project_modules(self):
        """Simple module reloader that skips __main__ and __mp_main__"""

        self.modules_to_reload = sorted(set(module['name'] for module in self.get_project_modules()))
        modules_reloaded = []
        for module in self.modules_to_reload:

            if module in ('__main__', '__mp_main__'):
                continue

            try:
                importlib.reload(sys.modules[module])
                modules_reloaded.append(module)
            except ModuleNotFoundError:
                logger.debug(f"Module: '{module}' not found")
            except Exception as e:
                logger.error(f"Module: '{module}' can't be reloaded: {e}.")

        return modules_reloaded

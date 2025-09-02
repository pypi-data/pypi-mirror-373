
import importlib
import pkgutil
import inspect
import threading
import sys
import os
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class Loader:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Loader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.timer        = None

    def loadSkills(self, source, component=None, useThreading=False):
        if useThreading:
            def loader():
                try:
                    if isinstance(source, str) and not os.path.exists(source):
                        self._loadSkillsFromModule(source, component)
                    else:
                        self._loadSkillsFromDirectory(source, component)
                except Exception as e:
                    logger.error(f"Error Loading Skills from {source}:", exc_info=True)
            threading.Thread(target=loader, daemon=True).start()
        else:
            try:
                if isinstance(source, str) and not os.path.exists(source):
                    self._loadSkillsFromModule(source, component)
                else:
                    self._loadSkillsFromDirectory(source, component)
            except Exception as e:
                logger.error(f"Error Loading Skills from {source}:", exc_info=True)

    def _loadSkillsFromModule(self, source, component = None):
        component = component if component is not None else []
        src = source.lstrip('.') if source.startswith('.') else source
        package = importlib.import_module(src)
        prefix  = package.__name__ + "."

        for _, modName, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            if ispkg:
                continue
            try:
                module = importlib.import_module(modName)
            except Exception as e:
                logger.warning(f"Could not load module {modName}: {e}", exc_info=True)
                continue

            # 1) instantiate classes as before
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != modName:
                    continue
                try:
                    component.append(cls())
                except Exception:
                    logger.error(f"Failed to instantiate {cls.__name__} in {modName}", exc_info=True)

            # 2) only treat module as a skill if it has its own ACTION_MAP
            #    or if it defines its own top‐level functions (not imports)
            action_map = getattr(module, "actionMap", None) or getattr(module, "ACTION_MAP", None)
            public_funcs = [
                fn for name, fn in inspect.getmembers(module, inspect.isfunction)
                if fn.__module__ == modName and not name.startswith("_")
            ]
            if isinstance(action_map, dict) or public_funcs:
                component.append(module)


    def _loadSkillsFromDirectory(self, source, component = None):
        component = component if component is not None else []
        src = Path(source)
        if not src.is_dir():
            logger.error(f"Skills directory not found: {src}")
            return

        for py in src.iterdir():
            if not (py.is_file() and py.suffix == ".py" and py.name != "__init__.py"):
                continue

            modName = f"_dynamic_{py.stem}"
            try:
                spec = importlib.util.spec_from_file_location(modName, str(py))
                mod  = importlib.util.module_from_spec(spec)
                sys.modules[modName] = mod
                spec.loader.exec_module(mod)
                #print(f"Loaded skill module: {modName}")
            except Exception as e:
                logger.warning(f"Could not load module from {py}: {e}", exc_info=True)
                continue

            # instantiate classes
            for _, cls in inspect.getmembers(mod, inspect.isclass):
                if cls.__module__ != modName:
                    continue
                try:
                    component.append(cls())
                except Exception:
                    logger.error(f"Failed to instantiate {cls.__name__} in {py.name}", exc_info=True)

            # module‐level functions filter by modName
            action_map = getattr(mod, "actionMap", None) or getattr(mod, "ACTION_MAP", None)
            public_funcs = [
                fn for name, fn in inspect.getmembers(mod, inspect.isfunction)
                if fn.__module__ == modName and not name.startswith("_")
            ]
            if isinstance(action_map, dict) or public_funcs:
                component.append(mod)
                #print(f"Loaded skill module: {py.name}")
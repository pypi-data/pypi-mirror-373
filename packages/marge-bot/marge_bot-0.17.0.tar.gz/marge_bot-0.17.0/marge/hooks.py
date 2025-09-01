import asyncio
import importlib.util
import inspect
import logging as log
from pathlib import Path
from typing import Any, Callable, Optional, cast

HookType = Callable[..., Optional[Any]]


def load_hook(hooks_dir_path: Path, hook_name: str) -> Optional[HookType]:
    file_path = hooks_dir_path / f"{hook_name}.py"
    if not file_path.is_file():
        log.info("Hook file not found: %s", file_path)
        return None

    try:
        spec = importlib.util.spec_from_file_location(hook_name, file_path)
        if spec is None or spec.loader is None:
            log.warning("Could not load spec for file: %s", file_path)
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return cast(HookType, module.main)

    except (AttributeError, RuntimeError, TypeError, ValueError) as err:
        log.error("Error loading hook %s: %s", hook_name, err, exc_info=True)

    return None


def run_hook(
    hooks_dir: str, hook_name: str, *args: Any, **kwargs: Any
) -> Optional[Any]:
    hooks_dir_path = Path(hooks_dir)
    if not hooks_dir_path.is_dir():
        log.info("Hook directory not found: %s", hooks_dir)
        return None

    hook = load_hook(hooks_dir_path, hook_name)
    if hook is None:
        log.info("Hook '%s' not loaded.", hook_name)
        return None

    try:
        if inspect.iscoroutinefunction(hook):
            return asyncio.run(hook(*args, **kwargs))
        return hook(*args, **kwargs)
    except (AttributeError, RuntimeError, TypeError, ValueError) as err:
        log.error("Error running hook '%s': %s", hook_name, err, exc_info=True)
        return None

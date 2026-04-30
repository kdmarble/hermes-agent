"""Memory-provider shim for the personal-context plugin.

The actual provider class lives in
~/homelab/hermes-plugins/personal-context/memory_provider.py. This bundled
shim lets Hermes discover it as memory.provider=personal-context without
moving the homelab plugin source into the Hermes checkout.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_PLUGIN_DIR = Path("/home/key/homelab/hermes-plugins/personal-context")


def _load_provider_module():
    module_name = "_personal_context_memory_provider"
    if module_name in sys.modules:
        return sys.modules[module_name]

    provider_file = _PLUGIN_DIR / "memory_provider.py"
    if not provider_file.exists():
        raise ImportError(
            f"personal-context memory_provider.py not found at {provider_file}. "
            "Is the homelab plugin source available?"
        )

    spec = importlib.util.spec_from_file_location(module_name, str(provider_file))
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load spec for personal-context memory_provider at {provider_file}"
        )

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def register(ctx) -> None:
    mod = _load_provider_module()
    provider_cls = getattr(mod, "PersonalContextMemoryProvider", None)
    if provider_cls is None:
        raise ImportError(
            "PersonalContextMemoryProvider class missing from "
            f"{_PLUGIN_DIR / 'memory_provider.py'}"
        )
    ctx.register_memory_provider(provider_cls())
    logger.info("personal-context memory provider registered via shim")

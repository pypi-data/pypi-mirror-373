"""Micro-Manager drivers package.

This package provides pre-compiled test adapters for Micro-Manager.
"""

import os.path

try:
    from .version import __version__
except ImportError:
    __version__ = "uninstalled"


def device_adapter_path() -> str:
    mm_dir = os.path.join(os.path.dirname(__file__), "libs")
    env_path = os.environ["PATH"]
    if mm_dir not in env_path:
        os.environ["PATH"] = env_path + os.pathsep + mm_dir
    return mm_dir

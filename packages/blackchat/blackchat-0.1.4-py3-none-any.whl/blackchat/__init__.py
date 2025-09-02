# blackchat/__init__.py

"""
BlackChat Package
=================
Ini adalah package utama BlackChat.

Submodul:
- core: user_manager, chat_manager, grup
- utils: node, notifier, peers
"""

# Import submodul agar mudah diakses dari package
from .core import user_manager, chat_manager, grup
from .utils import node, notifier, peers

# Optional: versi package
__version__ = "0.1.4"

# Optional: API publik (apa saja yang boleh diimport saat "from blackchat import *")
__all__ = [
    "user_manager",
    "chat_manager",
    "grup",
    "node",
    "notifier",
    "peers",
]

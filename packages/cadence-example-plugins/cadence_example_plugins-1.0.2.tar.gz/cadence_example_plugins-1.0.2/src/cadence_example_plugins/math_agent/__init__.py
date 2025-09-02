"""Math Agent Plugin for Cadence - SDK Version.

This plugin demonstrates the new SDK-based architecture with true decoupling.
Auto-registers the plugin when imported.
"""

from cadence_sdk import register_plugin

from .plugin import MathPlugin

register_plugin(MathPlugin)

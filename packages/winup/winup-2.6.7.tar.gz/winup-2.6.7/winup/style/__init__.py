"""
The Style module for WinUp.

This module provides the `styler` singleton, which is the main entry point
for all styling-related operations in a WinUp application.
"""

# winup/style/__init__.py
from .styler import styler

# To fix the namespace issues, we explicitly expose the styler's methods
# and its theme manager directly from the 'style' module. This ensures
# that `style.apply_props` and `style.themes` exist for all parts of the code.
apply_props = styler.apply_props
add_style_dict = styler.add_style_dict
reapply_global_styles = styler.reapply_global_styles
init_app = styler.init_app

# The 'themes' property is now available directly on the module.
# It is populated when init_app is called.
themes = styler.themes

# The styler object itself is also exposed for any remaining internal uses.
__all__ = ["styler", "apply_props", "add_style_dict", "reapply_global_styles", "init_app", "themes"] 
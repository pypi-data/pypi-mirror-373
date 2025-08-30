from .core.window import _winup_app, Window
from .core.component import component
from .core.events import event_bus as events
from .core.hot_reload import hot_reload_service, _import_from_string
from .core.memoize import memo, clear_memo_cache
from typing import Optional

from . import ui
from . import style
from .state import state
from . import tools
from .tools import wintools, profiler
from . import shell
from . import tasks
from . import traits
from . import net

try:
    from . import web
except ImportError:
    # Web dependencies are not installed.
    # Users can install them with `pip install winup[web]`
    web = None

import sys
import importlib
from PySide6.QtCore import QTimer

# --- Main API ---

def run(main_component_path: str, title="WinUp App", width=800, height=600, icon=None, dev=False, menu_bar: Optional[shell.MenuBar] = None, tool_bar: Optional[shell.ToolBar] = None, status_bar: Optional[shell.StatusBar] = None, tray_icon: Optional[shell.SystemTrayIcon] = None):
    """
    The main entry point for a WinUp application.
    ... (docstring) ...
    """
    # Initialize the style manager immediately, before any widgets are created.
    style.init_app(_winup_app.app)

    main_component = _import_from_string(main_component_path)
    main_widget = main_component()
    
    shell_kwargs = {
        "menu_bar": menu_bar,
        "tool_bar": tool_bar,
        "status_bar": status_bar,
    }

    # Pass shell components to the main window factory
    main_window = _winup_app.create_main_window(main_widget, title, width, height, icon, **shell_kwargs)
    
    # Initialize all modules that require a window instance
    wintools.init_app(main_window)
    
    if dev:
        print("Development mode enabled. Starting hot reloader...")
        
        def on_reload():
            """
            Dynamically re-imports the main component and rebuilds the entire UI.
            """
            nonlocal main_component
            try:
                print("[Hot Reload] Reloading UI on main thread...")
                
                fresh_main_component = _import_from_string(main_component_path)
                
                print(f"[Hot Reload] Replacing old component: {main_component}")
                print(f"[Hot Reload] With new component: {fresh_main_component}")

                old_widget = main_window.centralWidget()
                if old_widget:
                    old_widget.deleteLater()

                new_widget = fresh_main_component()
                main_window.setCentralWidget(new_widget)
                
                main_component = fresh_main_component
                
                print("[Hot Reload] UI Reloaded successfully.")
            except Exception as e:
                print(f"[Hot Reload] Error during component reload: {e}")
                import traceback
                traceback.print_exc()

        def schedule_reload():
            """
            This function is called by the hot reload service in the
            background thread. It schedules the actual reload on the
            main GUI thread.
            """
            QTimer.singleShot(0, on_reload)

        hot_reload_service.start(callback=schedule_reload)

    # Run the application event loop
    _winup_app.run()


__all__ = [
    "run", "Window", "hot_reload_service", "events", 
    "ui", "style", "state", "tools", "wintools", "profiler",
    "component", "memo", "clear_memo_cache",
    "shell", "tasks", "traits", "net", "web"
]

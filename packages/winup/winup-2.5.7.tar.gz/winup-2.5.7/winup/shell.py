"""
This module contains classes for building the main application shell,
including the Menu Bar, Tool Bar, Status Bar, and System Tray icon.
"""
from PySide6.QtWidgets import QMenuBar, QToolBar, QStatusBar, QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon
from typing import List, Optional, Callable

class MenuBar(QMenuBar):
    """Defines the main menu bar for a window."""
    def __init__(self, menu_items: dict[str, dict[str, Callable]]):
        super().__init__()
        for menu_name, actions in menu_items.items():
            menu = self.addMenu(menu_name)
            for action_name, handler in actions.items():
                if action_name == "---":
                    menu.addSeparator()
                else:
                    action = QAction(action_name, self)
                    action.triggered.connect(handler)
                    menu.addAction(action)

class ToolBar(QToolBar):
    """Defines the main toolbar for a window."""
    def __init__(self, tool_items: dict[str, Callable], icon_dir: Optional[str] = None):
        super().__init__()
        for name, handler in tool_items.items():
            icon_path = f"{icon_dir}/{name.lower()}.png" if icon_dir else None
            action = QAction(QIcon(icon_path), name, self) if icon_path else QAction(name, self)
            action.triggered.connect(handler)
            self.addAction(action)

class StatusBar(QStatusBar):
    """Defines the status bar for a window."""
    _instance = None
    
    def __init__(self):
        super().__init__()
        StatusBar._instance = self

    @staticmethod
    def show_message(message: str, timeout: int = 3000):
        if StatusBar._instance:
            StatusBar._instance.showMessage(message, timeout)

class SystemTrayIcon(QSystemTrayIcon):
    """Defines the application's icon in the system tray."""
    def __init__(self, icon_path: str, tooltip: str, menu_items: Optional[dict[str, Callable]] = None):
        super().__init__()
        self.setIcon(QIcon(icon_path))
        self.setToolTip(tooltip)
        
        if menu_items:
            tray_menu = QMenu()
            for item_name, handler in menu_items.items():
                if item_name == "---":
                    tray_menu.addSeparator()
                else:
                    action = QAction(item_name)
                    action.triggered.connect(handler)
                    tray_menu.addAction(action)
            self.setContextMenu(tray_menu)
        
        self.show() 
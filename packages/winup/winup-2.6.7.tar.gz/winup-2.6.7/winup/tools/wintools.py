import platform
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from typing import Callable

class WindowTools:
    def __init__(self):
        self._window = None

    def init_app(self, window):
        """Stores the main window instance to be manipulated."""
        self._window = window

    def check_availability(self, tool_name: str) -> bool:
        """Checks if a tool is available on the current operating system."""
        if tool_name in ["flash", "set_as_background"]:
            return platform.system() == "Windows"
        # Most other tools are cross-platform
        return True

    def lock_aspect_ratio(self, lock: bool = True):
        """Locks or unlocks the window's aspect ratio."""
        if not self._window: return
        # A bit of a hidden feature, we get the layout of the central widget
        # and use its size constraint to lock the aspect ratio.
        self._window.centralWidget().layout().setSizeConstraint(
            3 if lock else 0 # 3 is SetFixedSize, 0 is SetNoConstraint
        )

    def unlock_aspect_ratio(self):
        """Convenience method to unlock the aspect ratio."""
        self.lock_aspect_ratio(False)

    def center(self):
        """Centers the window on the primary screen."""
        if not self._window: return
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.get_window_geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self._window.move(x, y)

    def maximize(self):
        """Maximizes the window."""
        if self._window: self._window.showMaximized()

    def minimize(self):
        """Minimizes the window."""
        if self._window: self._window.showMinimized()

    def set_as_background(self):
        """
        (Windows-only) Attempts to set the application window as part of the background desktop.
        This is an advanced and often restricted operation.
        """
        if not self.check_availability("set_as_background"):
            print("Warning: set_as_background is only available on Windows.")
            return
            
        import ctypes
        from ctypes import wintypes

        # Find the window handle
        hwnd = self._window.winId()

        # Find the Progman window (the desktop manager)
        progman = ctypes.windll.user32.FindWindowW("Progman", None)
        
        # Send a message to Progman to spawn a WorkerW behind the desktop icons
        ctypes.windll.user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0, 1000, ctypes.pointer(wintypes.DWORD()))
        
        # Find the newly created WorkerW
        workerw = ctypes.windll.user32.FindWindowExW(None, None, "WorkerW", None)

        # Set our window's parent to be this WorkerW
        ctypes.windll.user32.SetParent(hwnd, workerw)


    def flash(self):
        """(Windows-only) Flashes the application icon on the taskbar."""
        if self.check_availability("flash"):
            QApplication.alert(self._window)
        else:
            print("Warning: Window flashing is not available on this OS.")
            
    def get_window_geometry(self):
        return self._window.frameGeometry()

    def call_later(self, delay_ms: int, callback: Callable):
        """
        Calls a function after a specified delay on the main UI thread.
        This is the thread-safe way to schedule UI updates from other threads.

        Args:
            delay_ms: The delay in milliseconds. Use 0 for "as soon as possible".
            callback: The function to execute.
        """
        QTimer.singleShot(delay_ms, callback)


# Singleton instance
wintools = WindowTools()

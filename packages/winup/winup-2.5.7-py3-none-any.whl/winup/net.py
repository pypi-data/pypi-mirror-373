"""
A simple networking module for WinUp, starting with a WebSocket client.
"""
import asyncio
import websockets
from typing import Callable
from threading import Thread

class WebSocketClient:
    """
    A robust WebSocket client that runs its own asyncio event loop in a
    dedicated background thread, providing thread-safe methods for a WinUp app.
    """
    def __init__(self, uri: str):
        self.uri = uri
        self.connection = None
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        print("WebSocket client thread started.")

    def _run_event_loop(self):
        """Runs the asyncio event loop forever in the background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _submit_coroutine(self, coro):
        """Submits a coroutine to the client's event loop thread-safely."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def _connect_and_listen(self, on_message: Callable[[str], None]):
        """The main coroutine that connects and then listens for messages."""
        try:
            async with websockets.connect(self.uri) as websocket:
                self.connection = websocket
                print(f"WebSocket connected to {self.uri}")
                # Listen for messages forever
                async for message in websocket:
                    on_message(message)
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
        finally:
            self.connection = None
            print("WebSocket connection closed.")
            
    async def _send_message(self, message: str):
        """The coroutine that sends a single message."""
        if not self.connection:
            print("Cannot send message: not connected.")
            return
        await self.connection.send(message)

    # --- Public, Thread-Safe Methods ---
    
    def start_listening(self, on_message: Callable[[str], None]):
        """
        Starts the connection and listening process in the background.
        
        Args:
            on_message: The callback function to execute with each received message.
        """
        self._submit_coroutine(self._connect_and_listen(on_message))

    def send(self, message: str):
        """
        Sends a message to the server. This method is thread-safe.
        """
        self._submit_coroutine(self._send_message(message)) 
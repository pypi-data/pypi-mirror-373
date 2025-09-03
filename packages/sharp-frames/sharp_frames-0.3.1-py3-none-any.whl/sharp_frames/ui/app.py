"""
Main Sharp Frames Textual application.
"""

import signal
import os
import time
import re
from textual.app import App
from textual.events import Key, Paste
from textual.widgets import Input

from .screens import ConfigurationForm
from .styles import SHARP_FRAMES_CSS
from .utils import sanitize_path_input


class SharpFramesApp(App):
    """Sharp Frames Textual application with interactive processing."""
    
    CSS = SHARP_FRAMES_CSS
    TITLE = "Sharp Frames - by Reflct.app"
    
    def __init__(self, **kwargs):
        """Initialize app with cross-platform compatibility fixes."""
        # Set appropriate terminal driver based on platform
        if os.name == 'posix':  # macOS/Linux
            os.environ['TEXTUAL_DRIVER'] = 'linux'
        elif os.name == 'nt':  # Windows
            # Let Textual auto-detect the best Windows driver
            # Don't force a specific driver on Windows as it can cause issues
            pass
        
        # Track spurious escape sequences
        self._last_escape_time = 0
        self._escape_count = 0
        self._last_action_time = 0
        self._original_signal_handlers = {}
        super().__init__(**kwargs)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for cross-platform compatibility."""
        def signal_handler(signum, frame):
            self.log.info(f"Received signal {signum} in main app, ignoring to prevent premature exit")
        
        # Handle common signals - only use signals available on current platform
        signals_to_handle = []
        
        # Always available signals
        for signal_attr in ['SIGTERM', 'SIGINT']:
            if hasattr(signal, signal_attr):
                signals_to_handle.append(getattr(signal, signal_attr))
        
        # Unix/Linux specific signals (not available on Windows)
        if os.name == 'posix':
            for signal_attr in ['SIGUSR1', 'SIGUSR2', 'SIGHUP', 'SIGPIPE']:
                if hasattr(signal, signal_attr):
                    signals_to_handle.append(getattr(signal, signal_attr))
        
        for sig in signals_to_handle:
            try:
                self._original_signal_handlers[sig] = signal.signal(sig, signal_handler)
                self.log.info(f"Registered signal handler for {sig}")
            except (OSError, ValueError) as e:
                self.log.warning(f"Could not register handler for signal {sig}: {e}")
    
    def restore_signal_handlers(self):
        """Restore original signal handlers before running subprocesses."""
        for sig, original_handler in self._original_signal_handlers.items():
            try:
                if original_handler is not None:
                    signal.signal(sig, original_handler)
                    self.log.debug(f"Restored original handler for signal {sig}")
            except (OSError, ValueError) as e:
                self.log.warning(f"Could not restore handler for signal {sig}: {e}")
    
    def on_key(self, event: Key) -> None:
        """Handle key events including cancellation keys for Windows compatibility."""
        # Handle Ctrl+C and Ctrl+Q for cancellation (Windows-friendly)
        if event.key == "ctrl+c" or event.key == "ctrl+q":
            self.log.info(f"Received {event.key} - attempting to cancel current operation")
            # Try to cancel current screen's operations
            try:
                current_screen = self.screen_stack[-1] if self.screen_stack else None
                if current_screen and hasattr(current_screen, 'action_cancel'):
                    current_screen.action_cancel()
                    return  # Handled
                elif current_screen and hasattr(current_screen, 'processor'):
                    # Try to cancel processor directly
                    if hasattr(current_screen.processor, 'cancel_processing'):
                        current_screen.processor.cancel_processing()
                        self.log.info("Cancelled processor operations")
            except Exception as e:
                self.log.error(f"Error during cancellation: {e}")
            
            # Fall back to standard handling
            return
        
        # Track escape key patterns to identify spurious sequences
        if event.key == "escape":
            current_time = time.time()
            
            # If we've had multiple escapes in quick succession, it's likely spurious
            if current_time - self._last_escape_time < 0.5:  # Within 500ms
                self._escape_count += 1
            else:
                self._escape_count = 1
            
            self._last_escape_time = current_time
            
            # If we have many escape sequences, log it but don't take action
            if self._escape_count > 2:
                self.log.warning(f"Detected {self._escape_count} rapid escape sequences - possible spurious input")
                return  # Suppress the escape
        
        # Reset escape count for other keys
        elif event.key != "escape":
            self._escape_count = 0
    
    def action_cancel(self) -> None:
        """Handle cancel action with spurious escape sequence protection."""
        # Check if we're in a screen that wants to handle its own cancellation
        current_screen = self.screen_stack[-1] if self.screen_stack else None
        
        # If the current screen has its own action_cancel method, delegate to it
        if current_screen and hasattr(current_screen, 'action_cancel') and callable(getattr(current_screen, 'action_cancel')):
            # Delegate to processing screens
            if any(screen_type in str(type(current_screen)) for screen_type in ['ProcessingScreen', 'SelectionScreen']):
                self.log.info("Delegating cancel action to screen")
                current_screen.action_cancel()
                return
        
        current_time = time.time()
        
        # If we just had escape sequences recently, this is likely spurious
        if current_time - self._last_escape_time < 2.0:  # Within 2 seconds of escape detection
            self.log.info(f"Blocking cancel action - likely triggered by spurious escape sequence")
            return
        
        self._last_action_time = current_time
        
        # Proceed with normal cancel logic
        if len(self.screen_stack) > 1:
            self.log.info("Popping screen")
            self.pop_screen()
        else:
            self.log.info("Exiting app")
            self.exit()
    
    def on_paste(self, event: Paste) -> None:
        """Handle paste events and route file paths to appropriate inputs."""
        pasted_text = event.text.strip()
        
        # Check if this looks like a file path
        if self._looks_like_file_path(pasted_text):
            self.log.info(f"Detected potential file path paste: {pasted_text}")
            if self._route_file_path_to_input(pasted_text):
                event.stop()  # Prevent default paste behavior
                return
        
        # Let the event propagate normally to the focused widget
    
    def _looks_like_file_path(self, text: str) -> bool:
        """Determine if pasted text looks like a file path."""
        if not text or len(text) < 2:
            return False
        
        # Common path indicators
        path_indicators = [
            text.startswith('/'),           # Unix absolute path
            re.match(r'^[A-Za-z]:[/\\]', text),  # Windows absolute path
            text.startswith('~'),           # Home directory reference
            './' in text or '../' in text,  # Relative path indicators
            '\\' in text,                   # Windows path separators
            os.path.exists(text)            # Actually exists on filesystem
        ]
        
        return any(path_indicators)
    
    def _route_file_path_to_input(self, file_path: str) -> bool:
        """Route detected file path to appropriate input field."""
        try:
            current_screen = self.screen_stack[-1] if self.screen_stack else None
            
            # Only handle ConfigurationForm
            if not isinstance(current_screen, ConfigurationForm):
                self.log.info("Not on two-phase configuration screen, skipping file path routing")
                return False
            
            # Determine target input based on current step
            target_input_id = self._get_target_input_for_step(current_screen, file_path)
            
            if target_input_id:
                try:
                    input_widget = current_screen.query_one(f"#{target_input_id}", Input)
                    sanitized_path = sanitize_path_input(file_path)
                    
                    # For output_dir, if a file is dragged, use its parent directory
                    if target_input_id == "output-dir-input" and os.path.isfile(sanitized_path):
                        sanitized_path = os.path.dirname(sanitized_path)
                    
                    input_widget.value = sanitized_path
                    input_widget.focus()
                    self.log.info(f"Routed file path to {target_input_id}: {sanitized_path}")
                    return True
                except Exception as e:
                    self.log.warning(f"Could not find or update input {target_input_id}: {e}")
            
        except Exception as e:
            self.log.error(f"Error routing file path: {e}")
        
        return False
    
    def _get_target_input_for_step(self, config_screen: ConfigurationForm, file_path: str) -> str:
        """Determine which input field should receive the file path."""
        current_step = config_screen.get_current_step_name()
        
        # Check what type of path this is (Windows-safe)
        is_directory = os.path.isdir(file_path) if os.path.exists(file_path) else file_path.endswith(('/', '\\'))
        is_video = any(file_path.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'])
        
        # Normalize path separators for consistent handling
        file_path = os.path.normpath(file_path)
        
        # Route based on current step and path type
        if current_step == "input_path":
            return "input-path"  # Always route to input path field
        elif current_step == "output_dir":
            # For output dir, accept both directories and any path (user might drag a file to get its directory)
            return "output-dir-input"  # Route to output dir field
        
        return None  # No suitable target
    
    def on_mount(self) -> None:
        """Start with the two-phase configuration form."""
        try:
            self.setup_signal_handlers()
            self.theme = "flexoki"
            self.push_screen(ConfigurationForm())
            self.log.info("Two-phase app mounted successfully")
        except Exception as e:
            self.log.error(f"Error during mount: {e}")
            self.notify(f"Error starting app: {e}", severity="error")


# Create alias for compatibility

"""
Core client for pbar.io API
"""

import os
import sys
import time
import threading
from typing import Optional, Dict, Any
from contextlib import contextmanager
import requests
from urllib.parse import urljoin

# Global configuration
_config = {
    "api_url": os.environ.get("PBAR_API_URL", "https://pbar.io/api"),
    "api_key": os.environ.get("PBAR_API_KEY", None),  # Optional for authenticated users
    "batch_updates": True,
    "update_interval": 0.5,  # seconds
    "display_interval": 1.0,  # seconds for display polling
}

# Global lock for coordinating terminal output
_terminal_lock = threading.Lock()


def configure(**kwargs):
    """Configure the pbar.io client"""
    _config.update(kwargs)


def get_config():
    """Get current configuration"""
    return _config.copy()


def _supports_color(file=sys.stderr) -> bool:
    """Check if the terminal supports color"""
    try:
        return hasattr(file, 'isatty') and file.isatty()
    except:
        return False


def _render_bar(title: str, current: int, total: int, width: int = 40, use_color: bool = True, cancelled: bool = False, has_cancelled_children: bool = False) -> str:
    """Render a progress bar string with optional color"""
    percentage = (current / total * 100) if total > 0 else 0
    filled = int(width * current / total) if total > 0 else 0
    
    # Color codes
    if use_color:
        # ANSI color codes
        RESET = '\033[0m'
        BOLD = '\033[1m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        CYAN = '\033[36m'
        GRAY = '\033[90m'
        
        # Choose color based on status
        if cancelled:
            bar_color = RED
            status_text = f" {RED}[CANCELLED]{RESET}"
        elif has_cancelled_children:
            bar_color = YELLOW
            status_text = f" {YELLOW}[INCOMPLETE]{RESET}" if percentage >= 100 else ""
        elif percentage >= 100:
            bar_color = GREEN
            status_text = f" {GREEN}[COMPLETE]{RESET}"
        elif percentage >= 50:
            bar_color = YELLOW
            status_text = ""
        else:
            bar_color = CYAN
            status_text = ""
    else:
        RESET = BOLD = RED = GREEN = YELLOW = CYAN = GRAY = ''
        bar_color = ''
        if cancelled:
            status_text = " [CANCELLED]"
        elif has_cancelled_children and percentage >= 100:
            status_text = " [INCOMPLETE]"
        elif percentage >= 100:
            status_text = " [COMPLETE]"
        else:
            status_text = ""
    
    bar = '█' * filled + '░' * (width - filled)
    
    # Build the progress bar string
    return (
        f"\r{BOLD}{title}:{RESET} "
        f"{bar_color}{bar}{RESET} "
        f"{BOLD}{current}/{total}{RESET} "
        f"{GRAY}({percentage:.1f}%){RESET}{status_text}"
    )


class ProgressBar:
    """A progress bar that syncs to pbar.io"""
    
    def __init__(
        self,
        title: str = None,
        total: int = 100,
        current: int = 0,
        parent: Optional["ProgressBar"] = None,
        unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_public: bool = True,
        is_writable: bool = True,  # For authenticated users: allow public updates
        slug: Optional[str] = None,  # For connecting to existing bar
        batch_updates: Optional[bool] = None,  # Override global batch setting
    ):
        self.title = title or "Progress"
        self.total = total
        self.current = current
        self.unit = unit
        self.metadata = metadata or {}
        self.is_public = is_public
        self.is_writable = is_writable
        self.parent = parent
        
        # Use instance-specific batch setting if provided, otherwise use global
        self._batch_updates = batch_updates if batch_updates is not None else _config["batch_updates"]
        
        self._slug = slug
        self._url = None
        self._api_url = None
        self._pending_updates = 0
        self._pending_increment = 0  # Track increments separately for atomic updates
        self._last_update = 0
        self._update_thread = None
        self._display_thread = None
        self._stop_threads = threading.Event()
        self._lock = threading.Lock()
        self._is_connected = False  # Track if we're connecting to existing bar
        self._cancelled = False  # Track if bar was cancelled
        self._has_cancelled_children = False  # Track if bar has cancelled children
        
        if slug:
            # Connect to existing progress bar
            self._is_connected = True
            self._fetch()
        else:
            # Create new progress bar on the server
            self._create()
        
        # Start update thread if batch updates are enabled for this instance
        # But NOT for connected bars - they should flush immediately
        if self._batch_updates and not self._is_connected:
            self._start_update_thread()
    
    def _create(self):
        """Create the progress bar on the server"""
        data = {
            "title": self.title,
            "total": self.total,
            "current": self.current,
            "metadata": self.metadata,
            "is_public": self.is_public,
            "is_writable": self.is_writable,
        }
        
        # Only include unit if it's not None
        if self.unit is not None:
            data["unit"] = self.unit
        
        if self.parent:
            # Handle both ProgressBar objects and string slugs
            if isinstance(self.parent, str):
                data["parent_slug"] = self.parent
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Setting parent_slug to {self.parent} (string) for {self.title}")
            elif isinstance(self.parent, ProgressBar):
                # Wait for parent to be created if needed
                max_wait = 5  # seconds
                wait_time = 0
                while not hasattr(self.parent, '_slug') or not self.parent._slug:
                    time.sleep(0.01)  # Short sleep
                    wait_time += 0.01
                    if wait_time >= max_wait:
                        break
                
                if hasattr(self.parent, '_slug') and self.parent._slug:
                    data["parent_slug"] = self.parent._slug
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Setting parent_slug to {self.parent._slug} for {self.title}")
                else:
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"WARNING: Parent has no slug after waiting {wait_time}s for {self.title}")
            elif hasattr(self.parent, 'slug'):
                data["parent_slug"] = self.parent.slug
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Setting parent_slug to {self.parent.slug} for {self.title}")
        
        headers = {"Content-Type": "application/json"}
        if _config["api_key"]:
            headers["X-API-Key"] = _config["api_key"]
        
        try:
            response = requests.post(
                urljoin(_config["api_url"] + "/", "bars"),
                json=data,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            
            result = response.json()
            self._slug = result["slug"]
            self._url = result["url"]
            self._api_url = result["api_url"]
            
            # Print the URL for the user
            print(f"Track progress at: {self._url}")
            
            # Debug parent-child relationship
            if os.environ.get('PBAR_DEBUG') and self.parent:
                if hasattr(self.parent, '_slug'):
                    print(f"  └─ Child of: {self.parent._slug}")
                print(f"  Request data included: {data}")
            
        except requests.exceptions.HTTPError as e:
            # Print more detailed error info
            print(f"Warning: Could not create remote progress bar: {e}")
            if hasattr(e.response, 'text'):
                print(f"Server response: {e.response.text}")
            # Continue working even if remote tracking fails
        except Exception as e:
            print(f"Warning: Could not create remote progress bar: {e}")
            # Continue working even if remote tracking fails
    
    def _fetch(self):
        """Fetch the current state from the server (for existing bars)"""
        if not self._slug:
            return False
            
        try:
            response = requests.get(
                f"{_config['api_url']}/bars/{self._slug}",
                headers={"Accept": "application/json"},
                timeout=2,
            )
            if response.status_code == 200:
                data = response.json()
                with self._lock:
                    self.title = data["title"]
                    self.current = data["current"]
                    self.total = data["total"]
                    self.metadata = data.get("metadata", {})
                    self.is_writable = data.get("is_writable", True)
                    self._cancelled = data.get("cancelled", False)
                    self._has_cancelled_children = data.get("has_cancelled_children", False)
                    self._url = f"{_config['api_url'].replace('/api', '')}/{self._slug}"
                    self._api_url = f"{_config['api_url']}/bars/{self._slug}"
                return True
        except Exception as e:
            print(f"Warning: Could not fetch progress bar: {e}")
        return False
    
    def _start_update_thread(self):
        """Start background thread for batched updates"""
        def update_loop():
            while not self._stop_threads.is_set():
                time.sleep(_config["update_interval"])
                with self._lock:
                    if (self._pending_updates > 0 or self._pending_increment > 0) and self._slug:
                        self._flush_updates()
        
        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()
    
    def _flush_updates(self):
        """Send pending updates to server"""
        if not self._slug:
            return
        
        # Use atomic increment when we have pending increments
        if self._pending_increment > 0:
            data = {"increment": self._pending_increment}
        else:
            # Fall back to setting current value (for set() method)
            data = {"current": self.current}
        
        if self.metadata:
            data["metadata"] = self.metadata
        
        # Include cancelled flag if set
        if self._cancelled:
            data["cancelled"] = True
        
        headers = {"Content-Type": "application/json"}
        # For authenticated bars, include API key if available
        if _config["api_key"]:
            headers["X-API-Key"] = _config["api_key"]
        
        try:
            response = requests.patch(
                f"{_config['api_url']}/bars/{self._slug}",
                json=data,
                headers=headers,
                timeout=2,
            )
            response.raise_for_status()
            self._pending_updates = 0
            self._pending_increment = 0
        except Exception as e:
            # Log the error for debugging but don't interrupt
            if "401" in str(e) or "read-only" in str(e):
                print(f"Warning: Progress bar is read-only. Updates not allowed.")
            else:
                # Silently fail for other errors
                pass
    
    def display(self, file=sys.stderr, auto_refresh: bool = True, show_children: bool = True):
        """Display the progress bar with live updates from the server
        
        Args:
            file: File object to write to (default: sys.stderr)
            auto_refresh: Whether to auto-refresh from server (default: True)
            show_children: Whether to display child progress bars (default: True)
        """
        if self._display_thread and self._display_thread.is_alive():
            return  # Already displaying
        
        # Check if terminal supports color
        use_color = _supports_color(file)
        
        if not auto_refresh:
            # Just display once
            if self._slug:
                # Fetch from server with or without children
                try:
                    params = {}
                    if not show_children:
                        params["children"] = "false"
                    
                    response = requests.get(
                        f"{_config['api_url']}/bars/{self._slug}",
                        headers={"Accept": "text/plain"},
                        params=params,
                        timeout=2
                    )
                    if response.status_code == 200:
                        file.write(response.text + "\n")
                        file.flush()
                        return
                except Exception as e:
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Display fetch error: {e}", file=sys.stderr)
            
            # Fallback to local render
            bar_str = _render_bar(self.title, self.current, self.total, use_color=use_color, 
                                 cancelled=self._cancelled, has_cancelled_children=self._has_cancelled_children)
            file.write(bar_str + "\n")
            file.flush()
            return
        
        def display_loop():
            last_displayed = -1
            
            while True:
                try:
                    if show_children:
                        # Fetch with children from terminal endpoint
                        response = requests.get(
                            f"{_config['api_url']}/bars/{self._slug}",
                            headers={"Accept": "text/plain"},
                            params={"children": "true"},
                            timeout=2,
                        )
                        if response.status_code == 200:
                            # Clear previous lines if multi-line display
                            lines = response.text.split('\n')
                            num_lines = len(lines)
                            
                            # Move cursor up to overwrite all lines
                            if last_displayed >= 0:
                                file.write(f"\033[{num_lines}A")  # Move up N lines
                            
                            # Write all lines
                            file.write(response.text)
                            file.flush()
                            
                            # Track that we displayed
                            last_displayed = self.current
                            
                            # If complete, add newline and exit
                            if self.current >= self.total:
                                file.write("\n")
                                file.flush()
                                return
                    else:
                        # Original single-line display
                        response = requests.get(
                            f"{_config['api_url']}/bars/{self._slug}",
                            headers={"Accept": "application/json"},
                            timeout=2,
                        )
                        if response.status_code == 200:
                            data = response.json()
                            with self._lock:
                                self.current = data["current"]
                                self.total = data["total"]
                                self.title = data["title"]
                            
                            # Only update display if progress changed
                            if self.current != last_displayed:
                                # Render and display with carriage return to overwrite
                                bar_str = _render_bar(self.title, self.current, self.total, use_color=use_color, 
                                                     cancelled=self._cancelled, has_cancelled_children=self._has_cancelled_children)
                                file.write(bar_str)
                                file.flush()
                                
                                last_displayed = self.current
                                
                                # If complete, add newline and exit
                                if self.current >= self.total:
                                    file.write("\n")
                                    file.flush()
                                    return  # Exit the display thread
                except Exception as e:
                    # Only show errors in debug mode
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Display error: {e}", file=sys.stderr)
                
                # Check if we should stop (but only after displaying 100% if needed)
                if self._stop_threads.is_set() and self.current < self.total:
                    # Stopped before completion
                    file.write("\n")
                    file.flush()
                    return
                
                time.sleep(_config["display_interval"])
        
        self._display_thread = threading.Thread(target=display_loop, daemon=True)
        self._display_thread.start()
    
    def wait(self, timeout: Optional[float] = None):
        """Wait for progress to reach 100% and display to show it"""
        if not self._display_thread:
            return  # No display to wait for
            
        start_time = time.time()
        
        # Poll until progress reaches 100% or timeout
        while self.current < self.total:
            if timeout and (time.time() - start_time) > timeout:
                break
            time.sleep(0.2)
            # Refresh from server to get latest state
            if self._slug:
                self._fetch()
        
        # Give display thread a moment to show the final state
        if self.current >= self.total:
            time.sleep(0.5)  # Let display catch up to 100%
        
        # Wait for display thread to finish
        if self._display_thread and self._display_thread.is_alive():
            remaining_timeout = None
            if timeout:
                remaining_timeout = timeout - (time.time() - start_time)
                if remaining_timeout <= 0:
                    return
            self._display_thread.join(remaining_timeout)
    
    def write_line(self):
        """Write a newline to move to next line (useful when printing logs)"""
        if self._display_thread and self._display_thread.is_alive():
            sys.stderr.write("\n")
            sys.stderr.flush()
    
    @contextmanager
    def pause_display(self):
        """Context manager to temporarily pause display for clean logging"""
        # Simple approach: just add newline before and let display resume
        if self._display_thread and self._display_thread.is_alive():
            sys.stderr.write("\n")
            sys.stderr.flush()
        yield
        # Display will continue on same line after the log
    
    def refresh(self):
        """Manually refresh the progress bar state from server"""
        return self._fetch()
    
    @property
    def url(self) -> str:
        """Get the web URL for this progress bar"""
        return self._url or ""
    
    @property
    def slug(self) -> str:
        """Get the slug of this progress bar"""
        return self._slug or ""
    
    def update(self, n: int = 1, metadata: Optional[Dict[str, Any]] = None):
        """Update the progress bar by n steps"""
        with self._lock:
            self.current = min(self.current + n, self.total)
            if metadata:
                self.metadata.update(metadata)
            self._pending_updates += 1
            self._pending_increment += n  # Track increments for atomic updates
            
            # Send immediate update if not batching or if we just completed
            if self._slug and (not self._batch_updates or self.current >= self.total):
                self._flush_updates()
    
    def increment(self, n: int = 1):
        """Increment the progress bar by n steps"""
        self.update(n)
    
    def set(self, value: int, metadata: Optional[Dict[str, Any]] = None):
        """Set the progress bar to a specific value"""
        with self._lock:
            self.current = min(max(0, value), self.total)
            if metadata:
                self.metadata.update(metadata)
            self._pending_updates += 1
            # Don't increment _pending_increment for set() - we want absolute value
            self._pending_increment = 0  # Clear any pending increments
            
            # Always flush immediately if setting to complete (100%)
            # or if not batching
            if self._slug and (not self._batch_updates or self.current >= self.total):
                self._flush_updates()
    
    def cancel(self):
        """Mark the progress bar as cancelled"""
        with self._lock:
            self._cancelled = True
            self._pending_updates += 1
            # Flush immediately to send cancelled status
            if self._slug:
                self._flush_updates()
    
    def close(self):
        """Flush pending updates and stop the update thread"""
        # First, flush any pending updates
        with self._lock:
            if (self._pending_updates > 0 or self._pending_increment > 0 or self._cancelled) and self._slug:
                self._flush_updates()
        
        # Only stop threads if we created this bar (not if we're connecting to existing)
        # SharedProgressBar instances shouldn't stop the shared update infrastructure
        if not self._is_connected:
            # Stop the update thread (not display thread)
            self._stop_threads.set()
            
            # Wait for update thread to finish
            if self._update_thread:
                self._update_thread.join(timeout=1)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.close()
        except:
            pass


class SharedProgressBar(ProgressBar):
    """Connect to and optionally update an existing progress bar"""
    
    def __init__(self, slug: str, silent: bool = True):
        """Initialize by connecting to an existing progress bar by slug
        
        Args:
            slug: The slug of the existing progress bar
            silent: If True, don't print connection messages (default: True)
        """
        # Call parent with slug parameter and disable batching for immediate updates
        # Important: Multiple workers need their updates to go through immediately
        super().__init__(slug=slug, batch_updates=False)
        
        # Only print if not silent (for debugging)
        if not silent and self._url:
            print(f"Connected to: {self._url}")
"""
Drop-in replacement for tqdm with automatic pbar.io integration.

Usage:
    from pbar_io.tqdm import tqdm  # instead of: from tqdm import tqdm
    
    # Everything else works the same!
    for item in tqdm(range(100), desc="Processing"):
        process(item)
"""

import os
import threading
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
from tqdm import tqdm as original_tqdm
from .client import ProgressBar

# Thread-local storage for tracking nested context
_context = threading.local()

# Global registry of tqdm instances for parent-child tracking
_tqdm_registry: Dict[int, ProgressBar] = {}

def _get_context_stack() -> List['tqdm']:
    """Get the current context stack for this thread."""
    if not hasattr(_context, 'stack'):
        _context.stack = []
    return _context.stack


class tqdm(original_tqdm):
    """
    Drop-in replacement for tqdm that automatically syncs to pbar.io.
    Supports automatic nesting for up to 5 levels (database limit).
    Automatically detects parent-child relationships in nested loops.
    """
    
    def __init__(self, *args, **kwargs):
        # Extract our custom parameters if present
        self._pbar_parent = kwargs.pop('pbar_parent', None)
        self._pbar_disable = kwargs.pop('pbar_disable', False)
        
        # Save the position parameter before tqdm consumes it
        self._pbar_position = kwargs.get('position', None)
        
        # Initialize original tqdm
        super().__init__(*args, **kwargs)
        
        # Skip pbar.io integration if disabled or in notebook mode
        if self._pbar_disable or self.disable or os.environ.get('PBAR_DISABLE'):
            self._pbar_io = None
            return
        
        # Extract properties for pbar.io
        title = self.desc or "Progress"
        total = self.total or 100
        
        # Determine parent - check position-based first since it's more reliable
        parent = None
        
        # Method 1: Explicit parent
        if self._pbar_parent:
            parent = self._pbar_parent
            if os.environ.get('PBAR_DEBUG'):
                print(f"Using explicit parent for {title}")
        
        # Method 2: Position-based (most reliable for nested loops with position parameter)
        # Use our saved position parameter
        my_position = self._pbar_position
        
        if not parent and my_position is not None and my_position > 0:
            # Look for a bar at position-1
            parent_pos = my_position - 1
            
            # First check the registry
            if parent_pos in _tqdm_registry:
                parent = _tqdm_registry[parent_pos]
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Found parent at position {parent_pos} for {title} at position {my_position}")
            else:
                # Look through active instances for parent at the right position
                for instance in self._instances:
                    if instance and instance != self and hasattr(instance, '_pbar_io') and instance._pbar_io:
                        # Use our saved position if this is our tqdm class
                        if isinstance(instance, tqdm):
                            inst_position = instance._pbar_position
                        else:
                            inst_position = instance.pos if instance.pos >= 0 else None
                        
                        if inst_position == parent_pos:
                            parent = instance._pbar_io
                            if os.environ.get('PBAR_DEBUG'):
                                print(f"Found parent via instance scan at position {parent_pos} for {title}")
                            break
        
        # Create remote progress bar
        try:
            self._pbar_io = ProgressBar(
                title=title,
                total=total,
                current=self.n,
                unit=self.unit,
                parent=parent,
                batch_updates=True,  # Enable batching for performance
            )
            
            # Register this instance by position (if set) or pos
            if self._pbar_position is not None:
                _tqdm_registry[self._pbar_position] = self._pbar_io
            elif self.pos >= 0:
                _tqdm_registry[self.pos] = self._pbar_io
            
        except Exception as e:
            # Silently fail if pbar.io is unavailable
            if os.environ.get('PBAR_DEBUG'):
                print(f"Failed to create pbar.io bar: {e}")
            self._pbar_io = None
        
        # Add ourselves to the context stack (for future use)
        _get_context_stack().append(self)
    
    def _find_parent_from_context(self) -> Optional[ProgressBar]:
        """Find parent progress bar from the context stack or position."""
        if self._pbar_parent:
            # Explicit parent provided
            return self._pbar_parent
        
        # First, try to find parent from context stack (for true nested loops)
        stack = _get_context_stack()
        if len(stack) > 1:  # More than just ourselves
            # The parent is the previous item in the stack
            for i in range(len(stack) - 1, -1, -1):
                parent_tqdm = stack[i]
                if parent_tqdm != self and hasattr(parent_tqdm, '_pbar_io') and parent_tqdm._pbar_io:
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Found parent via context: {parent_tqdm.desc} -> {self.desc}")
                    return parent_tqdm._pbar_io
        
        # Fallback: Use position parameter if explicitly set
        # position=0 is root, position=1 is first nested level, etc.
        if hasattr(self, 'position') and self.position is not None and self.position > 0:
            # Look for a bar at the previous position level
            parent_pos = self.position - 1
            if parent_pos in _tqdm_registry:
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Found parent via position: pos {parent_pos} -> pos {self.position}")
                return _tqdm_registry[parent_pos]
        
        # Alternative: Look through all active tqdm instances by position
        if self.pos > 0:
            for instance in self._instances:
                if instance and instance != self and hasattr(instance, '_pbar_io') and instance._pbar_io:
                    if instance.pos < self.pos:
                        # Find the closest parent (highest position less than ours)
                        if os.environ.get('PBAR_DEBUG'):
                            print(f"Found parent via pos scan: {instance.desc} (pos {instance.pos}) -> {self.desc} (pos {self.pos})")
                        return instance._pbar_io
        
        return None
    
    def update(self, n=1):
        """Update the progress bar."""
        result = super().update(n)
        
        # Update remote bar if available
        if self._pbar_io:
            try:
                # Include rate and ETA in metadata
                metadata = {}
                if self.format_dict.get('rate'):
                    metadata['rate'] = f"{self.format_dict['rate']:.2f} it/s"
                if self.format_dict.get('elapsed'):
                    metadata['elapsed'] = str(self.format_dict['elapsed'])
                
                self._pbar_io.update(n, metadata=metadata)
            except Exception as e:
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Failed to update pbar.io: {e}")
        
        return result
    
    def set_description(self, desc=None, refresh=True):
        """Set/update the description of the progress bar."""
        result = super().set_description(desc, refresh)
        
        # Update remote bar title if available
        if self._pbar_io and desc:
            try:
                self._pbar_io.title = desc
                # Force an update to sync the title
                self._pbar_io.set(self.n, metadata={'title': desc})
            except Exception as e:
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Failed to update pbar.io description: {e}")
        
        return result
    
    def close(self):
        """Cleanup and close the progress bar."""
        # Remove from context stack
        stack = _get_context_stack()
        if self in stack:
            stack.remove(self)
        
        # Check if we were interrupted (not at 100% completion)
        was_interrupted = self.n < self.total if self.total else False
        
        # Ensure final state is sent before closing
        if self._pbar_io:
            try:
                # If interrupted (not at 100%), cancel the bar
                if was_interrupted:
                    self._pbar_io.cancel()
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Cancelled incomplete progress bar '{self.desc}' at {self.n}/{self.total}")
                else:
                    # Force set to final value (self.n should be at total if completed)
                    # This ensures the bar shows 100% even if updates were batched
                    final_value = self.n
                    if hasattr(self, 'total') and self.total:
                        # If we've reached or exceeded total, set to total
                        if final_value >= self.total:
                            final_value = self.total
                    
                    # Send final update immediately (bypass batching)
                    self._pbar_io.set(final_value)
                
                # Now close the remote bar
                self._pbar_io.close()
            except Exception as e:
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Failed to finalize pbar.io: {e}")
            
            # Remove from registry
            if self.pos in _tqdm_registry:
                del _tqdm_registry[self.pos]
            if self._pbar_position is not None and self._pbar_position in _tqdm_registry:
                if _tqdm_registry[self._pbar_position] == self._pbar_io:
                    del _tqdm_registry[self._pbar_position]
        
        # Then close original tqdm
        super().close()
    
    def __iter__(self):
        """Iterator protocol - ensures proper context management."""
        try:
            for obj in super().__iter__():
                yield obj
        except KeyboardInterrupt:
            # Cancel the progress bar on keyboard interrupt
            if self._pbar_io:
                try:
                    self._pbar_io.cancel()
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Cancelled progress bar '{self.desc}' due to KeyboardInterrupt")
                except Exception as e:
                    if os.environ.get('PBAR_DEBUG'):
                        print(f"Failed to cancel pbar.io on KeyboardInterrupt: {e}")
            
            # Cancel all bars in the current context stack (nested bars)
            stack = _get_context_stack()
            for bar in stack:
                if bar != self and hasattr(bar, '_pbar_io') and bar._pbar_io:
                    try:
                        bar._pbar_io.cancel()
                        if os.environ.get('PBAR_DEBUG'):
                            print(f"Cancelled nested bar '{bar.desc}' due to parent KeyboardInterrupt")
                    except:
                        pass
            
            raise  # Re-raise the KeyboardInterrupt
        finally:
            # Ensure final state is sent when iteration completes
            if self._pbar_io and self.n >= self.total:
                try:
                    # Force final update to show 100%
                    self._pbar_io.set(self.total)
                except:
                    pass
            
            # Make sure we're removed from stack when iteration completes
            stack = _get_context_stack()
            if self in stack:
                stack.remove(self)
    
    def __enter__(self):
        """Context manager entry."""
        # Ensure we're in the stack
        stack = _get_context_stack()
        if self not in stack:
            stack.append(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Cancel on KeyboardInterrupt
        if exc_type is KeyboardInterrupt and self._pbar_io:
            try:
                self._pbar_io.cancel()
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Cancelled progress bar '{self.desc}' due to KeyboardInterrupt")
            except Exception as e:
                if os.environ.get('PBAR_DEBUG'):
                    print(f"Failed to cancel pbar.io on KeyboardInterrupt: {e}")
        
        # Remove from stack
        stack = _get_context_stack()
        if self in stack:
            stack.remove(self)
        self.close()
        return False


# Convenience function for simple iteration
def trange(*args, **kwargs):
    """
    Shortcut for tqdm(range(*args), **kwargs).
    
    Example:
        from pbar_io.tqdm import trange
        
        for i in trange(100, desc="Processing"):
            process(i)
    """
    return tqdm(range(*args), **kwargs)


# Decorator for tracking function execution
def track(func=None, *, desc=None, total=None, unit='it', leave=True):
    """
    Decorator to track function execution with a progress bar.
    Automatically handles KeyboardInterrupt by cancelling the bar.
    
    Example:
        @track(desc="Processing items", total=100)
        def process_items(items):
            for item in items:
                yield item
                # do processing
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Get description from function name if not provided
            bar_desc = desc or f.__name__
            
            # If the function is a generator, wrap it with tqdm
            import inspect
            if inspect.isgeneratorfunction(f):
                with tqdm(f(*args, **kwargs), desc=bar_desc, total=total, unit=unit, leave=leave) as pbar:
                    try:
                        for item in pbar:
                            yield item
                    except KeyboardInterrupt:
                        # The context manager will handle cancellation
                        raise
            else:
                # For regular functions, just show a simple progress bar
                with tqdm(total=1, desc=bar_desc, unit=unit, leave=leave) as pbar:
                    try:
                        result = f(*args, **kwargs)
                        pbar.update(1)
                        return result
                    except KeyboardInterrupt:
                        # The context manager will handle cancellation
                        raise
        
        return wrapper
    
    if func is None:
        # Called with arguments: @track(desc="...")
        return decorator
    else:
        # Called without arguments: @track
        return decorator(func)


# Auto-tracking function
def auto_track():
    """
    Automatically track ALL tqdm instances in your script.
    Call this once at the beginning of your script.
    
    Example:
        from pbar_io.tqdm import auto_track
        auto_track()
        
        # Now all tqdm bars will be tracked automatically
        from tqdm import tqdm
        for i in tqdm(range(100)):
            pass
    """
    import sys
    
    # Replace tqdm in sys.modules
    class TrackedModule:
        def __getattr__(self, name):
            if name == 'tqdm':
                return tqdm
            elif name == 'trange':
                return trange
            else:
                # Fallback to original tqdm module
                import tqdm as original_module
                return getattr(original_module, name)
    
    sys.modules['tqdm'] = TrackedModule()
    print("✓ Auto-tracking enabled for all tqdm instances")
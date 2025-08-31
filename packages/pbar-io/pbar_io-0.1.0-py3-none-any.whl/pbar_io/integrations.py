"""
Integrations with popular progress bar libraries
"""

from typing import Any, Optional
from .client import ProgressBar


def register(pbar_instance) -> Any:
    """
    Register any progress bar for remote tracking.
    Works with tqdm, rich, and other progress bars.
    
    Example:
        from tqdm import tqdm
        from pbar_io import register
        
        for item in register(tqdm(range(100))):
            process(item)
    """
    # Detect the type of progress bar
    class_name = pbar_instance.__class__.__name__
    module_name = pbar_instance.__class__.__module__
    
    if "tqdm" in module_name or class_name == "tqdm":
        track_tqdm(pbar_instance)
    elif "rich" in module_name:
        # Rich progress bars need special handling
        print("Rich progress bars should use track_rich() directly")
    else:
        # Try generic tracking
        track_generic(pbar_instance)
    
    return pbar_instance


def track_tqdm(tqdm_instance):
    """
    Track a tqdm progress bar remotely with automatic nesting support.
    
    Example:
        from tqdm import tqdm
        from pbar_io import track_tqdm
        
        pbar = tqdm(range(100), desc="Processing")
        track_tqdm(pbar)
        
        for item in pbar:
            process(item)
    """
    # Get tqdm properties
    title = getattr(tqdm_instance, "desc", "Progress") or "Progress"
    total = getattr(tqdm_instance, "total", 100) or 100
    
    # Handle nested tqdm bars based on position
    parent_bar = None
    position = getattr(tqdm_instance, "pos", 0)  # tqdm uses 'pos' internally
    
    # Try to find parent bar based on position hierarchy
    # Position 0 = root, 1 = first child, 2 = second child, etc.
    if position > 0:
        # Look for parent in global tqdm instances
        try:
            from tqdm import tqdm as tqdm_class
            # Search for a tqdm instance at position-1 that has a _pbar_io attribute
            for instance in tqdm_class._instances:
                if instance and hasattr(instance, '_pbar_io'):
                    instance_pos = getattr(instance, 'pos', -1)
                    # Parent should be at position-1
                    if instance_pos == position - 1:
                        parent_bar = instance._pbar_io
                        break
        except:
            pass
    
    # Create remote progress bar with parent if found
    remote_bar = ProgressBar(
        title=title,
        total=total,
        current=0,
        unit=getattr(tqdm_instance, "unit", None),
        parent=parent_bar,  # This will handle nesting automatically
    )
    
    # Store reference in tqdm instance
    tqdm_instance._pbar_io = remote_bar
    
    # Monkey-patch the update method
    original_update = tqdm_instance.update
    
    def patched_update(n=1):
        result = original_update(n)
        if hasattr(tqdm_instance, "_pbar_io"):
            # Update remote bar
            tqdm_instance._pbar_io.set(
                tqdm_instance.n,
                metadata={
                    "rate": f"{tqdm_instance.format_dict.get('rate', 0):.2f} it/s" 
                           if tqdm_instance.format_dict.get('rate') else None,
                    "eta": tqdm_instance.format_dict.get('remaining_str', None),
                }
            )
        return result
    
    tqdm_instance.update = patched_update
    
    # Monkey-patch close method
    original_close = tqdm_instance.close
    
    def patched_close():
        if hasattr(tqdm_instance, "_pbar_io"):
            tqdm_instance._pbar_io.close()
        return original_close()
    
    tqdm_instance.close = patched_close
    
    return tqdm_instance


def track_rich(progress_instance, task_id):
    """
    Track a rich.progress task remotely.
    
    Example:
        from rich.progress import Progress
        from pbar_io import track_rich
        
        with Progress() as progress:
            task = progress.add_task("Processing...", total=100)
            track_rich(progress, task)
            
            for i in range(100):
                progress.update(task, advance=1)
    """
    # Get task info
    task = progress_instance.tasks[task_id]
    
    # Create remote progress bar
    remote_bar = ProgressBar(
        title=task.description or "Progress",
        total=task.total or 100,
        current=task.completed,
    )
    
    # Store reference
    if not hasattr(progress_instance, "_pbar_io_tasks"):
        progress_instance._pbar_io_tasks = {}
    progress_instance._pbar_io_tasks[task_id] = remote_bar
    
    # Monkey-patch update method
    original_update = progress_instance.update
    
    def patched_update(task_id, **kwargs):
        result = original_update(task_id, **kwargs)
        
        if hasattr(progress_instance, "_pbar_io_tasks") and task_id in progress_instance._pbar_io_tasks:
            task = progress_instance.tasks[task_id]
            remote_bar = progress_instance._pbar_io_tasks[task_id]
            remote_bar.set(
                task.completed,
                metadata={
                    "percentage": f"{task.percentage:.1f}%",
                    "elapsed": str(task.elapsed) if task.elapsed else None,
                    "remaining": str(task.time_remaining) if task.time_remaining else None,
                }
            )
        
        return result
    
    progress_instance.update = patched_update
    
    return progress_instance


def track_generic(pbar_instance):
    """
    Try to track a generic progress bar.
    Works with objects that have common progress bar attributes.
    """
    # Try to find common attributes
    title = None
    total = 100
    current = 0
    
    # Look for common attribute names
    for attr in ["description", "desc", "label", "title", "name"]:
        if hasattr(pbar_instance, attr):
            title = getattr(pbar_instance, attr)
            break
    
    for attr in ["total", "max", "maximum", "max_value"]:
        if hasattr(pbar_instance, attr):
            total = getattr(pbar_instance, attr) or 100
            break
    
    for attr in ["current", "n", "value", "position"]:
        if hasattr(pbar_instance, attr):
            current = getattr(pbar_instance, attr) or 0
            break
    
    # Create remote bar
    remote_bar = ProgressBar(
        title=title or "Progress",
        total=total,
        current=current,
    )
    
    # Store reference
    pbar_instance._pbar_io = remote_bar
    
    # Try to patch update/increment methods
    for method_name in ["update", "increment", "advance", "next"]:
        if hasattr(pbar_instance, method_name):
            original_method = getattr(pbar_instance, method_name)
            
            def create_patched_method(orig):
                def patched(*args, **kwargs):
                    result = orig(*args, **kwargs)
                    if hasattr(pbar_instance, "_pbar_io"):
                        # Try to get current value
                        current = 0
                        for attr in ["current", "n", "value", "position"]:
                            if hasattr(pbar_instance, attr):
                                current = getattr(pbar_instance, attr) or 0
                                break
                        pbar_instance._pbar_io.set(current)
                    return result
                return patched
            
            setattr(pbar_instance, method_name, create_patched_method(original_method))
            break
    
    return pbar_instance


def track(*args, **kwargs):
    """
    Convenience function that works like tqdm but with remote tracking.
    
    Example:
        from pbar_io import track
        
        for item in track(range(100), description="Processing"):
            process(item)
    """
    try:
        from tqdm import tqdm
        pbar = tqdm(*args, **kwargs)
        return register(pbar)
    except ImportError:
        raise ImportError("tqdm is required for track(). Install with: pip install tqdm")
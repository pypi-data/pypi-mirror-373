# pbar-io Python Client

Share your progress bars online with [pbar.io](https://pbar.io) - the universal progress bar service.

## Installation

```bash
pip install pbar-io
```

## Quick Start

### With tqdm (recommended)

```python
from tqdm import tqdm
from pbar_io import register

# One line to share your progress bar online
for item in register(tqdm(range(1000), desc="Training model")):
    # Your code here
    process(item)
# Automatically prints: Track progress at https://pbar.io/abc123
```

### Manual usage

```python
from pbar_io import ProgressBar

# Create a progress bar
bar = ProgressBar(title="Processing files", total=100)
print(f"Track at: {bar.url}")

# Update progress
for i in range(100):
    process_file(i)
    bar.update(1)  # or bar.increment()

# Set specific value
bar.set(50)

# Update with metadata
bar.update(1, metadata={"eta": "5 minutes", "rate": "10 files/sec"})
```

### Hierarchical progress bars

```python
from pbar_io import ProgressBar

# Create parent bar
parent = ProgressBar(title="Overall progress", total=3)

# Create child bars
task1 = ProgressBar(title="Task 1", total=100, parent=parent)
task2 = ProgressBar(title="Task 2", total=200, parent=parent)
task3 = ProgressBar(title="Task 3", total=150, parent=parent)

# Parent automatically updates as children progress
for i in range(100):
    task1.update(1)
```

### With rich

```python
from rich.progress import Progress
from pbar_io import track_rich

with Progress() as progress:
    task = progress.add_task("Processing...", total=100)
    
    # Enable remote tracking
    track_rich(progress, task)
    
    for i in range(100):
        progress.update(task, advance=1)
```

## Features

- 🌐 **Universal Access** - View progress in browser, terminal, or mobile
- 🚀 **Real-time Updates** - Live progress via WebSockets
- 🔒 **Privacy Options** - Public or private progress bars
- 📊 **Hierarchical Progress** - Parent-child progress tracking
- 🎨 **Beautiful Terminal Output** - ANSI colors in terminal
- ⚡ **Zero Config** - No account required for public bars

## Configuration

```python
from pbar_io import configure

# Set custom API endpoint (for self-hosted instances)
configure(api_url="https://your-instance.com/api")

# Use API key for private bars and higher limits
configure(api_key="your_api_key")

# Set default retention time
configure(retention_hours=24)
```

## CLI Usage

```bash
# Create a progress bar from command line
pbar create "Backup in progress" --total 100

# Update progress
pbar update <id> --increment 10

# View in terminal
pbar view <id>

# Watch progress with auto-refresh
pbar watch <id>
```

## API Reference

### ProgressBar

```python
class ProgressBar:
    def __init__(self, title: str, total: int = 100, parent: ProgressBar = None, 
                 unit: str = None, metadata: dict = None, public: bool = True)
    
    @property
    def url(self) -> str: ...
    @property
    def id(self) -> str: ...
    
    def update(self, n: int = 1, metadata: dict = None) -> None: ...
    def increment(self, n: int = 1) -> None: ...
    def set(self, value: int) -> None: ...
    def close(self) -> None: ...
```

### Integration Functions

```python
def register(pbar) -> Any:
    """Register any progress bar for remote tracking"""

def track_tqdm(tqdm_instance) -> None:
    """Track a tqdm progress bar"""

def track_rich(progress, task_id) -> None:
    """Track a rich progress task"""
```

## License

MIT License - see LICENSE file for details.
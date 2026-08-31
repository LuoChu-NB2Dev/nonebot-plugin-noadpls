# Migration Guide

## For Users

**Good news!** If you're using this plugin as-is, you don't need to change anything. The refactoring maintains full backward compatibility.

### What Still Works

All existing imports and functionality work exactly as before:

```python
# These still work (via compatibility shim)
from nonebot_plugin_noadpls.ban_judge import check_text
from nonebot_plugin_noadpls.ban_judge import update_words
```

## For Developers

If you're developing or extending this plugin, here's how to use the new structure.

### Recommended Imports

Use the new modular imports for better code organization:

```python
# Text detection (NEW - recommended)
from nonebot_plugin_noadpls.detectors import check_text, preprocess_text

# Word management (NEW - recommended)
from nonebot_plugin_noadpls.detectors import update_words

# Handler utilities (NEW)
from nonebot_plugin_noadpls.handlers import whether_is_admin, get_group_member_list
```

### Old vs New Import Paths

| Old Import | New Import | Status |
|------------|------------|--------|
| `from .ban_judge import check_text` | `from .detectors import check_text` | Both work |
| `from .ban_judge import update_words` | `from .detectors import update_words` | Both work |
| `from .__main__ import whether_is_admin` | `from .handlers import whether_is_admin` | New only |
| `from .__main__ import get_group_member_list` | `from .handlers import get_group_member_list` | New only |

### Adding New Features

#### Adding a New Handler

1. Create a new file in `handlers/` directory:

```python
# handlers/new_feature_handler.py
"""New feature handler description."""
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.typing import T_State

from ..data import data
from ..utils.log import log


async def handle_new_feature(event: GroupMessageEvent, state: T_State, bot: Bot):
    """Handle new feature logic."""
    # Your implementation here
    pass
```

2. Export it from `handlers/__init__.py`:

```python
from .new_feature_handler import handle_new_feature

__all__ = [
    # ... existing exports ...
    "handle_new_feature",
]
```

3. Register it in `__main__.py`:

```python
from .handlers import handle_new_feature

@group_message_matcher.handle()
async def _handle_new_feature(event: GroupMessageEvent, state, bot):
    """Handle new feature"""
    await handle_new_feature(event, state, bot)
```

#### Adding a New Detector

1. Create a new file in `detectors/` directory:

```python
# detectors/new_detector.py
"""New detector description."""
from ..utils.log import log


def detect_something(text: str) -> list:
    """Detect something in text.
    
    Args:
        text: Text to check
        
    Returns:
        List of detected items
    """
    # Your implementation here
    return []
```

2. Export it from `detectors/__init__.py`:

```python
from .new_detector import detect_something

__all__ = [
    # ... existing exports ...
    "detect_something",
]
```

3. Use it in handlers:

```python
from ..detectors import detect_something

# In your handler
results = detect_something(text)
```

### Extending Existing Features

#### Adding New Detection Layer

To add a new detection method to `text_detector.py`:

1. Add your detection function:

```python
def custom_detection_check(text: str) -> list:
    """Custom detection logic.
    
    Args:
        text: Text to check
        
    Returns:
        List of matches
    """
    matches = []
    # Your detection logic here
    return matches
```

2. Integrate it into `check_text()`:

```python
def check_text(text: str) -> list:
    """Multi-layer text detection."""
    # ... existing layers ...
    
    # New layer: Custom detection
    custom_matches = custom_detection_check(text)
    if custom_matches:
        return custom_matches
    
    return []
```

#### Adding New Command

1. Add command handler in `command_handler.py`:

```python
async def handle_new_command(bot: Bot, event, groupid: str, matcher):
    """Handle new command logic."""
    # Your implementation
    pass
```

2. Export from `handlers/__init__.py`:

```python
from .command_handler import handle_new_command

__all__ = [
    # ... existing exports ...
    "handle_new_command",
]
```

3. Register matcher in `__main__.py`:

```python
new_command_matcher = on_message(
    rule=command("new_command"),
    priority=env_config.priority,
    block=True,
    permission=GROUP | PRIVATE,
)

@new_command_matcher.handle()
async def _handle_new_command(bot, event, matcher, arg=CommandArg()):
    """Process new command"""
    await handle_new_command(bot, event, arg.extract_plain_text(), matcher)
```

### Testing Your Changes

#### Unit Testing Individual Modules

Each module can now be tested independently:

```python
# Test detector
from nonebot_plugin_noadpls.detectors import check_text

def test_check_text():
    result = check_text("test text")
    assert isinstance(result, list)
```

```python
# Test handler (with mocking)
from unittest.mock import Mock
from nonebot_plugin_noadpls.handlers import judge_and_ban

async def test_ban_handler():
    event = Mock()
    state = {"full_text": "test"}
    bot = Mock()
    
    await judge_and_ban(event, state, bot)
    # Add assertions
```

#### Integration Testing

Test the full flow through `__main__.py`:

```python
# Your integration test here
```

### Code Style Guidelines

1. **Module Docstrings**: Every module should have a docstring explaining its purpose
2. **Function Docstrings**: Document all public functions with Args and Returns
3. **Type Hints**: Use type hints for function parameters and return values
4. **Logging**: Use the centralized logger from `utils.log`
5. **Error Handling**: Handle exceptions gracefully with proper logging

### Best Practices

1. **Keep Modules Focused**: Each module should have a single, clear responsibility
2. **Avoid Circular Imports**: Import from lower-level modules (utils, config, data)
3. **Use Relative Imports**: Import from sibling packages using relative imports
4. **Document Your Code**: Add docstrings and comments where necessary
5. **Test Independently**: Write tests that can run without the full plugin context

### Common Pitfalls

❌ **Don't** import handlers in detectors (creates circular dependency)
❌ **Don't** put business logic in `__main__.py` (keep it thin)
❌ **Don't** modify the compatibility shim `ban_judge.py` (for backward compatibility)

✅ **Do** use the appropriate package (handlers for event handling, detectors for text analysis)
✅ **Do** export new functions from package `__init__.py`
✅ **Do** register new matchers in `__main__.py`
✅ **Do** follow the existing code style and patterns

## Need Help?

- Check `ARCHITECTURE.md` for structure overview
- Check `REFACTORING.md` for refactoring details
- Review existing handlers/detectors for patterns
- Open an issue on GitHub for questions

# Architecture Overview

## New Module Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         __main__.py                              │
│                   (Matcher Registration)                         │
│                          143 lines                               │
└─────────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┴───────────────┐
                │                              │
                ▼                              ▼
    ┌──────────────────────┐      ┌──────────────────────┐
    │      handlers/       │      │     detectors/       │
    │   (Event Handling)   │      │  (Text Detection)    │
    └──────────────────────┘      └──────────────────────┘
                │                              │
    ┌───────────┼────────────────┐             │
    │           │                │             │
    ▼           ▼                ▼             ▼
┌────────┐ ┌────────┐ ┌──────────────┐ ┌──────────────┐
│message │ │  ban   │ │    admin     │ │     text     │
│handler │ │handler │ │   handler    │ │   detector   │
│        │ │        │ │              │ │              │
│ 128L   │ │  98L   │ │     84L      │ │    308L      │
└────────┘ └────────┘ └──────────────┘ └──────────────┘
                │                              │
                ▼                              ▼
        ┌──────────────┐             ┌──────────────┐
        │   command    │             │     word     │
        │   handler    │             │   manager    │
        │              │             │              │
        │    218L      │             │    135L      │
        └──────────────┘             └──────────────┘
                │
                ▼
        ┌──────────────┐
        │    utils     │
        │              │
        │     78L      │
        └──────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Supporting Modules (Already Well-Organized)                 │
├──────────────────────────────────────────────────────────────┤
│  • ocr/        - Image text recognition (local & online)     │
│  • utils/      - Cache, logging, constants                   │
│  • config.py   - Configuration management                    │
│  • data.py     - Data persistence                            │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

### Message Processing Flow
```
Group Message
    │
    ▼
[message_handler]
    │ Extract text and OCR
    ▼
[ban_handler]
    │ Check for violations
    ├─ Uses [text_detector]
    │       ├─ DFA check
    │       ├─ Preprocess check
    │       ├─ Fuzzy match
    │       └─ Regex match
    │
    ├─ If violation found:
    │   ├─ Ban user
    │   ├─ Delete message
    │   └─ Update ban count
    │
    ▼
[admin_handler]
    ├─ Notify admins (if subscribed)
    └─ Notify member
```

### Command Flow
```
Command Message
    │
    ▼
[command_handler]
    ├─ "接收通知" / "关闭通知"
    │   └─ Update notification preferences
    │
    ├─ "nap_on" / "nap_off"
    │   └─ Update group detection state
    │
    └─ Uses [utils] for:
        ├─ Admin verification
        └─ Group member checks
```

## Module Responsibilities

### handlers/
| Module | Lines | Responsibility |
|--------|-------|----------------|
| message_handler.py | 128 | Extract text from messages, perform OCR on images |
| ban_handler.py | 98 | Detect violations, execute bans, update records |
| admin_handler.py | 84 | Send notifications to admins and members |
| command_handler.py | 218 | Handle all command interactions |
| utils.py | 78 | Shared utilities for handlers |

### detectors/
| Module | Lines | Responsibility |
|--------|-------|----------------|
| text_detector.py | 308 | Multi-layer text detection and preprocessing |
| word_manager.py | 135 | Manage ban word lists (add/remove/reload) |

## Import Graph

```
__main__.py
    ├─→ handlers/
    │       ├─→ message_handler → ocr/, utils/
    │       ├─→ ban_handler → detectors/, data, config
    │       ├─→ admin_handler → data
    │       ├─→ command_handler → data, handlers/utils
    │       └─→ utils → config, utils/
    │
    └─→ data

detectors/
    ├─→ text_detector → config, utils/
    └─→ word_manager → detectors/text_detector, config

ban_judge.py (compatibility shim)
    └─→ detectors/
```

## Benefits of This Structure

1. **Single Responsibility Principle**
   - Each module has one clear purpose
   - Easy to understand what each file does

2. **Low Coupling**
   - Modules depend on abstractions (config, data)
   - Handlers don't know about each other's internals

3. **High Cohesion**
   - Related functionality is grouped together
   - Easy to find where a feature is implemented

4. **Testability**
   - Each module can be tested independently
   - Mock dependencies easily

5. **Maintainability**
   - Changes are localized to specific modules
   - Reduced risk of breaking unrelated features

6. **Scalability**
   - Easy to add new handlers or detectors
   - Clear pattern to follow

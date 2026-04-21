---
name: "web-screenshot"
description: "Captures web page screenshots at multiple device resolutions for multimodal LLM analysis. Supports interactive actions (click, scroll, fill, etc.) before capture. Invoke when user needs webpage screenshots, visual UI capture, responsive layout verification, or interactive web page capture."
---

# Web Screenshot Skill

Captures high-quality web page screenshots at various device resolutions, with support for **interactive actions** (click, scroll, fill, hover, etc.) performed before capture. Designed for multimodal LLM visual analysis.

## When to Invoke

- User asks to capture a screenshot of a URL or local HTML file
- User needs responsive design verification across multiple devices
- User wants visual comparison of a page at different screen sizes
- User requests batch screenshot generation for LLM analysis
- User mentions "截图", "screenshot", "capture webpage", "设备兼容性测试"
- User asks "帮我截取这个网页在不同设备上的显示效果"
- User asks to "登录后再截图", "点击菜单后截图", "滚动到页面底部截图"

## Quick Start

```bash
# Single URL at default device (iPhone 14 Pro)
python web_screenshot.py --url "https://example.com"

# Local HTML file with multiple devices
python web_screenshot.py --file "./index.html" --devices "iphone_se,full_hd"

# All mobile devices, custom output directory
python web_screenshot.py --url "https://example.com" --devices "all_mobile" --output "./my-screenshots"

# Interactive actions: scroll and take screenshots at different positions
python web_screenshot.py --url "https://example.com" --actions "scroll:0,300;wait:500;screenshot;scroll:0,600;wait:500;screenshot"

# Click element then screenshot
python web_screenshot.py --url "https://example.com" --actions "click:#menu-btn;wait:300;screenshot:menu_open"

# Fill form then screenshot
python web_screenshot.py --url "https://example.com" --actions "fill:#search:hello;press:Enter;wait:1000;screenshot:search_result"
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--url` | No* | - | Target URL (http/https) |
| `--file` | No* | - | Local HTML file path |
| `--devices` | No | `iphone_14_pro` | Comma-separated device presets or groups |
| `--width` | No | - | Custom viewport width |
| `--height` | No | - | Custom viewport height |
| `--output` | No | `./screenshots` | **Output directory** (relative to current working directory) |
| `--full-page` | No | `false` | Capture full scrollable page |
| `--quality` | No | `90` | Image quality 1-100 (JPEG) |
| `--format` | No | `png` | Output format: `png` (lossless) or `jpeg` |
| `--wait` | No | `1000` | Wait after load in ms |
| `--timeout` | No | `30000` | Page load timeout in ms |
| `--dark-mode` | No | `false` | Enable dark mode color scheme |
| `--batch-file` | No | - | Text file with URLs (one per line, # for comments) |
| `--no-metadata` | No | `false` | Skip metadata JSON sidecar |
| `--no-headless` | No | `false` | Run browser visibly (debug) |
| `--actions` | No | - | **Interactive actions** (semicolon-separated) |

*One of `--url` or `--file` or `--batch-file` is required.

## Interactive Actions (`--actions`)

Perform a sequence of actions on the page before taking the final screenshot. Actions are separated by semicolons (`;`).

### Action Types

| Action | Syntax | Description |
|--------|--------|-------------|
| `click` | `click:<selector>` | Click element (CSS selector or text) |
| `fill` | `fill:<selector>:<value>` | Fill input field with value |
| `scroll` | `scroll:<x>,<y>` | Scroll to coordinates (in pixels) |
| `wait` | `wait:<ms>` | Wait milliseconds (default: 1000) |
| `hover` | `hover:<selector>` | Hover over element |
| `press` | `press:<selector>:<key>` | Press keyboard key on element (e.g., `Enter`, `Escape`) |
| `select` | `select:<selector>:<value>` | Select option in dropdown |
| `screenshot` | `screenshot[:<name>]` | Take screenshot at current state (with optional name) |
| `wait_for_selector` | `wait_for_selector:<selector>` | Wait for element to appear |
| `evaluate` | `evaluate:<js>` | Execute JavaScript code |
| `goto` | `goto:<url>` | Navigate to another URL |

### Action Examples

```bash
# Scroll to 300px and take screenshot
--actions "scroll:0,300;wait:500;screenshot"

# Scroll through page in 3 steps
--actions "scroll:0,300;wait:300;screenshot:top;scroll:0,800;wait:300;screenshot:middle;scroll:0,1500;wait:300;screenshot:bottom"

# Click menu button and screenshot
--actions "click:#menu-button;wait:500;screenshot:menu_opened"

# Fill login form
--actions "fill:#username:admin;fill:#password:secret;click:#login-btn;wait:1000;screenshot:dashboard"

# Hover and screenshot
--actions "hover:#dropdown;wait:300;screenshot:dropdown_open"

# Press keyboard
--actions "click:#search;fill:#search:test;press:Enter;wait:1000;screenshot:search_results"

# Wait for element then screenshot
--actions "wait_for_selector:#loading-complete;wait:500;screenshot:content_loaded"
```

### Naming Screenshots

Screenshots taken via `screenshot` action get a suffix in the filename:

```
--actions "scroll:0,300;screenshot:top;scroll:0,600;screenshot:bottom"
```

Output files:
- `example_com_full_hd_1920x1080_20260421_143025_top.png`
- `example_com_full_hd_1920x1080_20260421_143025_bottom.png`
- `example_com_full_hd_1920x1080_20260421_143025_2.png` (final screenshot without name)

## Device Presets

### Mobile (8 presets)

| Preset | Device | Viewport | DPR | Physical Pixels |
|--------|--------|----------|-----|-----------------|
| `iphone_se` | iPhone SE | 375×667 | 2.0 | 750×1334 |
| `iphone_14_pro` | iPhone 14 Pro | 390×844 | 3.0 | 1170×2532 |
| `iphone_14_plus` | iPhone 14 Plus | 428×926 | 3.0 | 1284×2778 |
| `iphone_xr` | iPhone XR / 11 | 414×896 | 2.0 | 828×1792 |
| `pixel_7` | Google Pixel 7 | 412×915 | 2.625 | 1082×2402 |
| `galaxy_s20` | Samsung Galaxy S20 | 360×800 | 3.0 | 1080×2400 |
| `ipad_mini` | iPad Mini | 768×1024 | 2.0 | 1536×2048 |
| `ipad_pro` | iPad Pro 11" | 834×1194 | 2.0 | 1668×2388 |

### Desktop (4 presets)

| Preset | Device | Viewport | DPR |
|--------|--------|----------|-----|
| `hd` | HD Laptop | 1366×768 | 1.0 |
| `full_hd` | Full HD Monitor | 1920×1080 | 1.0 |
| `2k` | 2K Display | 2560×1440 | 1.0 |
| `4k` | 4K UHD Display | 3840×2160 | 1.0 |

### Device Groups
- `all_mobile` - all 8 mobile devices
- `all_desktop` - all 4 desktop devices
- `all` - all 12 devices

## Output Location

**Default output directory**: `./screenshots/` (relative to current working directory)

```
./screenshots/
├── example_com_iphone_14_pro_390x844_20260421_143025.png
├── example_com_iphone_14_pro_390x844_20260421_143025.json
├── example_com_full_hd_1920x1080_20260421_143030_top.png
├── example_com_full_hd_1920x1080_20260421_143030_bottom.png
└── localhost_3000_iphone_se_375x667_20260421_143035.png
```

## Output File Naming

```
{sanitized_source}_{device}_{width}x{height}_{YYYYMMDD}_{HHMMSS}_{seq}.{format}
```

With optional step name suffix:
```
{sanitized_source}_{device}_{width}x{height}_{YYYYMMDD}_{HHMMSS}_{name}.{format}
```

**Examples:**
- `example_com_iphone_14_pro_390x844_20260421_143025.png` (final)
- `example_com_iphone_14_pro_390x844_20260421_143025_top.png` (after scroll)
- `localhost_3000_full_hd_1920x1080_20260421_143030_bottom.png` (named step)

## Metadata Sidecar (auto-generated JSON)

Each screenshot has a companion `.json` file with device info, actions executed, etc.:

```json
{
  "source": "https://example.com",
  "device": "iphone_14_pro",
  "device_label": "iPhone 14 Pro",
  "device_category": "mobile",
  "width": 390,
  "height": 844,
  "dpr": 3.0,
  "timestamp": "2026-04-21T14:30:25.123456",
  "full_page": false,
  "dark_mode": false,
  "format": "png",
  "file_size_kb": 245.6,
  "page_title": "Example Domain",
  "actions_executed": 6
}
```

**Metadata fields:**
| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Original URL or file path |
| `device` | string | Device preset name |
| `device_label` | string | Human-readable device name |
| `device_category` | string | `"mobile"` or `"desktop"` |
| `width` | int | Viewport width in CSS pixels |
| `height` | int | Viewport height in CSS pixels |
| `dpr` | float | Device pixel ratio |
| `timestamp` | string | ISO 8601 format capture time |
| `full_page` | bool | Whether full-page capture was enabled |
| `dark_mode` | bool | Whether dark mode was enabled |
| `format` | string | Image format (`png` or `jpeg`) |
| `file_size_kb` | float | Screenshot file size in kilobytes |
| `page_title` | string | Web page title at capture time |
| `actions_executed` | int | Number of interactive actions executed |

## Image Quality

- **PNG (default)**: Lossless compression, best for text clarity and LLM visual analysis
- **JPEG**: Configurable quality (1-100), smaller file size
- **DPR scaling**: Mobile presets use device pixel ratio for crisp rendering

## Programmatic Usage (Python)

```python
from web_screenshot import WebScreenshot, DevicePresets, Action, ActionType

capturer = WebScreenshot(output_dir="./screenshots")

# Actions as objects (recommended for complex use)
actions = [
    Action(type=ActionType.SCROLL, value={"x": 0, "y": 300}),
    Action(type=ActionType.WAIT, value=500),
    Action(type=ActionType.SCREENSHOT, name="scroll_300"),
    Action(type=ActionType.SCROLL, value={"x": 0, "y": 600}),
    Action(type=ActionType.WAIT, value=500),
    Action(type=ActionType.SCREENSHOT, name="scroll_600"),
]

result = capturer.capture(
    url="https://example.com",
    device=DevicePresets.FULL_HD,
    actions=actions
)

print(f"File: {result.file_path}")
print(f"Status: {result.status}")
print(f"Actions: {len(result.actions)}")
for i, act in enumerate(result.actions):
    print(f"  {i+1}. {act['type']} - {'OK' if act['success'] else 'FAIL'}")

# Batch with actions
results = capturer.capture_batch(
    urls=["https://a.com", "https://b.com"],
    devices=[DevicePresets.IPHONE_SE, DevicePresets.FULL_HD],
)
for r in results:
    print(f"{r.device}: {r.file_path}")
```

### Action Types (Python Enum)

```python
from web_screenshot import ActionType

ActionType.CLICK              # click element
ActionType.FILL               # fill input
ActionType.SCROLL             # scroll to x,y
ActionType.WAIT               # wait ms
ActionType.HOVER              # hover element
ActionType.PRESS              # press keyboard key
ActionType.SELECT             # select dropdown option
ActionType.SCREENSHOT         # take screenshot
ActionType.WAIT_FOR_SELECTOR  # wait element visible
ActionType.WAIT_FOR_NAVIGATION # wait for navigation
ActionType.EVALUATE           # execute JavaScript
ActionType.GOTO              # navigate to URL
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Invalid action type | Prints warning, skips that action, continues |
| Element not found | Reports timeout error, continues with next action |
| Invalid URL | Reports error, continues with next URL in batch |
| File not found | Prints error message, exits with code 2 |
| Network timeout | Retries once, then reports failure |
| Browser crash | Restarts browser, continues remaining tasks |

**Actions are non-fatal**: If an action fails, the script continues executing remaining actions and still captures the final screenshot.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All screenshots captured successfully |
| `1` | Partial failure (some screenshots failed) |
| `2` | Complete failure (no screenshots captured) |

## Requirements

- Python 3.9+
- Playwright (`pip install playwright && playwright install chromium`)

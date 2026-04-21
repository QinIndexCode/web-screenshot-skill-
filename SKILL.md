---
name: "web-screenshot"
description: "Captures web page screenshots at multiple device resolutions for multimodal LLM analysis. Invoke when user needs webpage screenshots, visual UI capture, or responsive layout verification."
---

# Web Screenshot Skill

Captures high-quality web page screenshots at various device resolutions, designed for multimodal LLM visual analysis.

## When to Invoke

- User asks to capture a screenshot of a URL or local HTML file
- User needs responsive design verification across multiple devices
- User wants visual comparison of a page at different screen sizes
- User requests batch screenshot generation for LLM analysis
- User mentions "截图", "screenshot", "capture webpage", "设备兼容性测试"
- User asks "帮我截取这个网页在不同设备上的显示效果"

## Quick Start

```bash
# Single URL at default device (iPhone 14 Pro), outputs to ./screenshots/
python web_screenshot.py --url "https://example.com"

# Local HTML file with multiple devices
python web_screenshot.py --file "./index.html" --devices "iphone_se,full_hd"

# All mobile devices, custom output directory
python web_screenshot.py --url "https://example.com" --devices "all_mobile" --output "./my-screenshots"

# Batch processing from URL list file
python web_screenshot.py --batch-file "./urls.txt" --devices "all"
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

*One of `--url` or `--file` or `--batch-file` is required.

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

Screenshot files and their companion metadata JSON files are saved to this directory. The directory is automatically created if it does not exist.

**Example structure:**
```
./screenshots/
├── example_com_iphone_14_pro_390x844_20260421_143025.png
├── example_com_iphone_14_pro_390x844_20260421_143025.json
├── example_com_full_hd_1920x1080_20260421_143030.png
├── example_com_full_hd_1920x1080_20260421_143030.json
└── localhost_3000_iphone_se_375x667_20260421_143035.png
    └── localhost_3000_iphone_se_375x667_20260421_143035.json
```

## Output File Naming

```
{sanitized_source}_{device}_{width}x{height}_{YYYYMMDD}_{HHMMSS}_{seq}.{format}
```

**Naming rules:**
- `sanitized_source`: URL domain + path (dots/cols replaced with `_`), or HTML filename
- `device`: Device preset name (e.g., `iphone_14_pro`)
- `width`×`height`: Viewport dimensions in pixels
- `YYYYMMDD`: Capture date
- `HHMMSS`: Capture time (24-hour)
- `seq`: Sequence number for uniqueness within same second
- `format`: `png` (default, lossless) or `jpeg`

**Examples:**
- `example_com_iphone_14_pro_390x844_20260421_143025.png`
- `localhost_3000_full_hd_1920x1080_20260421_143030.png`
- `index_html_ipad_pro_834x1194_20260421_143035.png`

## Metadata Sidecar (auto-generated JSON)

Each screenshot has a companion `.json` file with the same name, containing:

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
  "page_title": "Example Domain"
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
| `dpr` | float | Device pixel ratio (affects actual image resolution) |
| `timestamp` | string | ISO 8601 format capture time |
| `full_page` | bool | Whether full-page capture was enabled |
| `dark_mode` | bool | Whether dark mode was enabled |
| `format` | string | Image format (`png` or `jpeg`) |
| `file_size_kb` | float | Screenshot file size in kilobytes |
| `page_title` | string | Web page title at capture time |

## Image Quality

- **PNG (default)**: Lossless compression, best for text clarity and LLM visual analysis
- **JPEG**: Configurable quality (1-100), smaller file size, suitable for photos
- **DPR scaling**: Mobile presets use device pixel ratio for crisp rendering on high-DPI screens

## Programmatic Usage (Python)

```python
from web_screenshot import WebScreenshot, DevicePresets, CaptureOptions

# Initialize capturer with custom output directory
capturer = WebScreenshot(output_dir="./my-screenshots")

# Single capture
result = capturer.capture(
    url="https://example.com",
    device=DevicePresets.IPHONE_14_PRO,
    full_page=True
)
print(f"File: {result.file_path}")
print(f"Metadata: {result.metadata_path}")
print(f"Page title: {result.page_title}")
print(f"Size: {result.file_size_kb}KB")
print(f"Duration: {result.duration_ms}ms")

# Batch capture with options
options = CaptureOptions(
    full_page=False,
    dark_mode=True,
    format="png",
    wait_ms=2000
)
results = capturer.capture_batch(
    urls=["https://a.com", "https://b.com"],
    devices=[DevicePresets.IPHONE_SE, DevicePresets.FULL_HD],
    options=options
)
for r in results:
    print(f"[{r.status}] {r.device}: {r.file_path}")
```

## Error Handling

| Error | Behavior |
|-------|----------|
| Invalid URL | Reports error to stderr, continues with next URL in batch |
| File not found | Prints error message, exits with code 2 |
| Network timeout | Retries once after timeout, then reports failure |
| Render failure | Attempts to capture error-state screenshot, reports failure |
| Browser crash | Restarts browser, continues with remaining tasks |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All screenshots captured successfully |
| `1` | Partial failure (some screenshots failed) |
| `2` | Complete failure (no screenshots captured) |

## Requirements

- Python 3.9+
- Playwright (`pip install playwright && playwright install chromium`)

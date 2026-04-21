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
python web_screenshot.py --url "https://example.com"
python web_screenshot.py --file "./index.html" --devices "iphone_se,full_hd"
python web_screenshot.py --url "https://example.com" --devices "all_mobile"
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
| `--output` | No | `./screenshots` | Output directory |
| `--full-page` | No | `false` | Capture full scrollable page |
| `--quality` | No | `90` | Image quality 1-100 |
| `--format` | No | `png` | Output format: `png` or `jpeg` |
| `--wait` | No | `1000` | Wait after load in ms |
| `--timeout` | No | `30000` | Page load timeout in ms |
| `--dark-mode` | No | `false` | Enable dark mode |
| `--batch-file` | No | - | Text file with URLs (one per line) |
| `--no-metadata` | No | `false` | Skip metadata JSON sidecar |
| `--no-headless` | No | `false` | Run browser visibly (debug) |

*One of `--url` or `--file` or `--batch-file` is required.

## Device Presets

### Mobile (8 presets)
`iphone_se` (375×667), `iphone_14_pro` (390×844), `iphone_14_plus` (428×926), `iphone_xr` (414×896), `pixel_7` (412×915), `galaxy_s20` (360×800), `ipad_mini` (768×1024), `ipad_pro` (834×1194)

### Desktop (4 presets)
`hd` (1366×768), `full_hd` (1920×1080), `2k` (2560×1440), `4k` (3840×2160)

### Device Groups
`all_mobile` - all 8 mobile devices
`all_desktop` - all 4 desktop devices
`all` - all 12 devices

## Output File Naming

```
{source}_{device}_{width}x{height}_{timestamp}.png
```

Example: `example_com_iphone_14_pro_390x844_20260421_143025.png`

## Metadata Sidecar (auto-generated)

Companion `.json` file with device info, resolution, DPR, page title, timestamp.

## Programmatic Usage (Python)

```python
from web_screenshot import WebScreenshot, DevicePresets

capturer = WebScreenshot(output_dir="./screenshots")
result = capturer.capture(url="https://example.com", device=DevicePresets.IPHONE_14_PRO)
results = capturer.capture_batch(urls=["https://a.com", "https://b.com"], devices=[DevicePresets.IPHONE_SE, DevicePresets.FULL_HD])
```

## Error Handling

- Invalid URL → reports error, continues batch
- File not found → exits with code 2
- Network timeout → retries once, then reports failure
- Browser crash → restarts browser, continues

## Exit Codes
- `0`: All screenshots captured
- `1`: Partial failure
- `2`: Complete failure

## Requirements
- Python 3.9+
- Playwright (`pip install playwright && playwright install chromium`)

# Web Screenshot Skill

A high-quality web page screenshot capture tool designed for multimodal LLM visual analysis. Supports multiple device resolutions, batch processing, and metadata generation.

## Features

- **Multi-source capture**: URL, local HTML file, or batch file
- **12 device presets**: 8 mobile (iPhone SE/14 Pro/14 Plus/XR, Pixel 7, Galaxy S20, iPad Mini/Pro) + 4 desktop (HD, Full HD, 2K, 4K)
- **Device groups**: `all_mobile`, `all_desktop`, `all` for quick multi-device capture
- **Custom resolution**: Override any preset with `--width`/`--height`
- **Smart file naming**: `{source}_{device}_{width}x{height}_{timestamp}.png`
- **Metadata sidecar**: Auto-generated JSON with device info, resolution, DPR, page title, timestamp
- **High DPI rendering**: Mobile presets use device pixel ratio for crisp text
- **Full page mode**: Capture entire scrollable content
- **Dark mode support**: `--dark-mode` flag
- **Async batch processing**: Parallel capture across devices per URL
- **Robust error handling**: Invalid URLs, missing files, render failures, timeouts

## Quick Start

### Install

```bash
pip install playwright
playwright install chromium
```

### Usage

```bash
# Single URL screenshot at default device (iPhone 14 Pro)
python web_screenshot.py --url "https://example.com"

# Local HTML file with specific device
python web_screenshot.py --file "./index.html" --devices "iphone_14_pro"

# Multiple devices at once
python web_screenshot.py --url "https://example.com" --devices "iphone_se,iphone_14_pro,full_hd,4k"

# All mobile devices
python web_screenshot.py --url "https://example.com" --devices "all_mobile"

# All devices (mobile + desktop)
python web_screenshot.py --url "https://example.com" --devices "all"

# Custom resolution
python web_screenshot.py --url "https://example.com" --width 1440 --height 900

# Full page screenshot
python web_screenshot.py --url "https://example.com" --full-page --devices "full_hd"

# Batch URLs from file
python web_screenshot.py --batch-file "./urls.txt" --devices "all_mobile"

# Dark mode
python web_screenshot.py --url "https://example.com" --dark-mode

# JPEG format with quality setting
python web_screenshot.py --url "https://example.com" --format jpeg --quality 85
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--url` | No* | - | Target URL to screenshot (http/https) |
| `--file` | No* | - | Local HTML file path to screenshot |
| `--devices` | No | `iphone_14_pro` | Comma-separated device preset names or group names |
| `--width` | No | - | Custom viewport width (overrides device preset) |
| `--height` | No | - | Custom viewport height (overrides device preset) |
| `--output` | No | `./screenshots` | Output directory for screenshot files |
| `--full-page` | No | `false` | Capture full scrollable page |
| `--quality` | No | `90` | Image quality (1-100, PNG uses lossless) |
| `--format` | No | `png` | Output format: `png` or `jpeg` |
| `--wait` | No | `1000` | Milliseconds to wait after page load before capture |
| `--timeout` | No | `30000` | Page load timeout in milliseconds |
| `--dark-mode` | No | `false` | Enable dark mode color scheme |
| `--batch-file` | No | - | Text file with one URL per line for batch processing |
| `--no-metadata` | No | `false` | Skip metadata JSON sidecar generation |
| `--no-headless` | No | `false` | Run browser in visible mode (debugging) |

*One of `--url` or `--file` or `--batch-file` is required.

## Device Presets

### Mobile Devices

| Preset Name | Device | Resolution | DPR |
|-------------|--------|------------|-----|
| `iphone_se` | iPhone SE | 375×667 | 2 |
| `iphone_14_pro` | iPhone 14 Pro | 390×844 | 3 |
| `iphone_14_plus` | iPhone 14 Plus | 428×926 | 3 |
| `iphone_xr` | iPhone XR / 11 | 414×896 | 2 |
| `pixel_7` | Google Pixel 7 | 412×915 | 2.625 |
| `galaxy_s20` | Samsung Galaxy S20 | 360×800 | 3 |
| `ipad_mini` | iPad Mini | 768×1024 | 2 |
| `ipad_pro` | iPad Pro 11" | 834×1194 | 2 |

### Desktop Devices

| Preset Name | Device | Resolution |
|-------------|--------|------------|
| `hd` | HD Laptop | 1366×768 |
| `full_hd` | Full HD Monitor | 1920×1080 |
| `2k` | 2K Display | 2560×1440 |
| `4k` | 4K UHD Display | 3840×2160 |

### Device Groups

| Group Name | Includes |
|------------|----------|
| `all_mobile` | All 8 mobile device presets |
| `all_desktop` | All 4 desktop device presets |
| `all` | All 12 device presets |

## Output

### File Naming

Screenshots are automatically named with embedded metadata:

```
{source}_{device}_{width}x{height}_{timestamp}.png
```

Examples:
- `example_com_iphone_14_pro_390x844_20260421_143025.png`
- `localhost_3000_full_hd_1920x1080_20260421_143030.png`

### Metadata Sidecar

When metadata is enabled (default), a companion `.json` file is generated:

```json
{
  "source": "https://example.com",
  "device": "iphone_14_pro",
  "device_label": "iPhone 14 Pro",
  "device_category": "mobile",
  "width": 390,
  "height": 844,
  "dpr": 3,
  "timestamp": "2026-04-21T14:30:25.123456",
  "full_page": false,
  "dark_mode": false,
  "format": "png",
  "file_size_kb": 245,
  "page_title": "Example Domain"
}
```

## Programmatic Usage (Python)

```python
from web_screenshot import WebScreenshot, DevicePresets

capturer = WebScreenshot(output_dir="./screenshots")

# Single capture
result = capturer.capture(
    url="https://example.com",
    device=DevicePresets.IPHONE_14_PRO,
    full_page=True
)
print(result.file_path, result.metadata)

# Batch capture
results = capturer.capture_batch(
    urls=["https://example.com", "https://example.org"],
    devices=[DevicePresets.IPHONE_SE, DevicePresets.FULL_HD]
)
for r in results:
    print(f"{r.device}: {r.status} -> {r.file_path}")
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All screenshots captured successfully |
| `1` | Partial failure (some screenshots failed) |
| `2` | Complete failure (no screenshots captured) |

## Requirements

- Python 3.9+
- Playwright (`pip install playwright && playwright install chromium`)

## License

MIT

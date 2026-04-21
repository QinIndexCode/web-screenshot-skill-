"""
Web Screenshot Skill for Multimodal LLM
Captures high-quality web page screenshots at various device resolutions.
Supports URL, local HTML, batch processing, metadata generation, and interactive actions.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright is not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(2)


class DeviceCategory(Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"


@dataclass
class DevicePreset:
    name: str
    label: str
    width: int
    height: int
    dpr: float
    category: DeviceCategory
    user_agent: Optional[str] = None
    has_touch: bool = False
    is_mobile: bool = False


class DevicePresets:
    IPHONE_SE = DevicePreset("iphone_se", "iPhone SE", 375, 667, 2.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        has_touch=True, is_mobile=True)

    IPHONE_14_PRO = DevicePreset("iphone_14_pro", "iPhone 14 Pro", 390, 844, 3.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        has_touch=True, is_mobile=True)

    IPHONE_14_PLUS = DevicePreset("iphone_14_plus", "iPhone 14 Plus", 428, 926, 3.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        has_touch=True, is_mobile=True)

    IPHONE_XR = DevicePreset("iphone_xr", "iPhone XR / 11", 414, 896, 2.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        has_touch=True, is_mobile=True)

    PIXEL_7 = DevicePreset("pixel_7", "Google Pixel 7", 412, 915, 2.625, DeviceCategory.MOBILE,
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        has_touch=True, is_mobile=True)

    GALAXY_S20 = DevicePreset("galaxy_s20", "Samsung Galaxy S20", 360, 800, 3.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        has_touch=True, is_mobile=True)

    IPAD_MINI = DevicePreset("ipad_mini", "iPad Mini", 768, 1024, 2.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        has_touch=True, is_mobile=True)

    IPAD_PRO = DevicePreset("ipad_pro", "iPad Pro 11\"", 834, 1194, 2.0, DeviceCategory.MOBILE,
        "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        has_touch=True, is_mobile=True)

    HD = DevicePreset("hd", "HD Laptop", 1366, 768, 1.0, DeviceCategory.DESKTOP,
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

    FULL_HD = DevicePreset("full_hd", "Full HD Monitor", 1920, 1080, 1.0, DeviceCategory.DESKTOP,
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

    TWO_K = DevicePreset("2k", "2K Display", 2560, 1440, 1.0, DeviceCategory.DESKTOP,
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

    FOUR_K = DevicePreset("4k", "4K UHD Display", 3840, 2160, 1.0, DeviceCategory.DESKTOP,
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

    _ALL = None
    _BY_NAME = None

    @classmethod
    def get_all(cls) -> List[DevicePreset]:
        if cls._ALL is None:
            cls._ALL = [
                cls.IPHONE_SE, cls.IPHONE_14_PRO, cls.IPHONE_14_PLUS, cls.IPHONE_XR,
                cls.PIXEL_7, cls.GALAXY_S20, cls.IPAD_MINI, cls.IPAD_PRO,
                cls.HD, cls.FULL_HD, cls.TWO_K, cls.FOUR_K,
            ]
        return cls._ALL

    @classmethod
    def get_by_name(cls) -> dict:
        if cls._BY_NAME is None:
            cls._BY_NAME = {p.name: p for p in cls.get_all()}
        return cls._BY_NAME

    @classmethod
    def resolve(cls, device_spec: str) -> List[DevicePreset]:
        by_name = cls.get_by_name()
        specs = [s.strip().lower() for s in device_spec.split(",")]

        result = []
        for spec in specs:
            if spec == "all":
                result.extend(cls.get_all())
            elif spec == "all_mobile":
                result.extend([p for p in cls.get_all() if p.category == DeviceCategory.MOBILE])
            elif spec == "all_desktop":
                result.extend([p for p in cls.get_all() if p.category == DeviceCategory.DESKTOP])
            elif spec in by_name:
                result.append(by_name[spec])
            else:
                print(f"WARNING: Unknown device preset '{spec}', skipping. Available: {list(by_name.keys())}")
        return result


class ActionType(Enum):
    CLICK = "click"
    FILL = "fill"
    SCROLL = "scroll"
    WAIT = "wait"
    HOVER = "hover"
    PRESS = "press"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"
    GOTO = "goto"


@dataclass
class Action:
    type: ActionType
    selector: Optional[str] = None
    value: Optional[Any] = None
    options: Optional[Dict[str, Any]] = None
    name: Optional[str] = None

    def __repr__(self):
        parts = [self.type.value]
        if self.selector:
            parts.append(f"selector={self.selector[:50]}...")
        if self.value is not None:
            val_str = str(self.value)[:30]
            parts.append(f"value={val_str}")
        if self.name:
            parts.append(f"name={self.name}")
        return f"Action({' '.join(parts)})"


def parse_action_string(action_str: str) -> List[Action]:
    actions = []
    tokens = action_str.split(";")
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        parts = token.split(":", 1)
        action_type_str = parts[0].strip().lower()
        rest = parts[1].strip() if len(parts) > 1 else ""

        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            print(f"WARNING: Unknown action type '{action_type_str}', skipping")
            continue

        action = Action(type=action_type)

        if action_type == ActionType.SCREENSHOT:
            if rest:
                action.name = rest
        elif action_type == ActionType.WAIT:
            try:
                action.value = int(rest) if rest else 1000
            except ValueError:
                action.value = 1000
        elif action_type == ActionType.SCROLL:
            if rest:
                coords = rest.split(",")
                action.value = {
                    "x": int(coords[0].strip()) if len(coords) > 0 else 0,
                    "y": int(coords[1].strip()) if len(coords) > 1 else 0,
                }
            else:
                action.value = {"x": 0, "y": 0}
        elif action_type in (ActionType.CLICK, ActionType.HOVER, ActionType.WAIT_FOR_SELECTOR):
            action.selector = rest
        elif action_type == ActionType.FILL:
            if ":" in rest:
                sel, val = rest.split(":", 1)
                action.selector = sel.strip()
                action.value = val.strip()
            else:
                action.selector = rest
        elif action_type == ActionType.PRESS:
            if ":" in rest:
                sel, key = rest.split(":", 1)
                action.selector = sel.strip()
                action.value = key.strip()
            else:
                action.value = rest.strip()
        elif action_type == ActionType.SELECT:
            if ":" in rest:
                sel, val = rest.split(":", 1)
                action.selector = sel.strip()
                action.value = val.strip()
        elif action_type == ActionType.EVALUATE:
            action.value = rest
        elif action_type == ActionType.GOTO:
            action.value = rest

        actions.append(action)

    return actions


@dataclass
class ActionResult:
    action: Action
    success: bool
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
    duration_ms: int = 0


@dataclass
class StepResult:
    step_name: str
    file_path: Optional[str]
    metadata: Optional[Dict]
    status: str
    error: Optional[str] = None


@dataclass
class CaptureResult:
    source: str
    device: str
    width: int
    height: int
    dpr: float
    status: str
    file_path: Optional[str] = None
    metadata_path: Optional[str] = None
    error: Optional[str] = None
    file_size_kb: float = 0
    page_title: str = ""
    timestamp: str = ""
    duration_ms: int = 0
    steps: List[StepResult] = field(default_factory=list)
    actions: List[ActionResult] = field(default_factory=list)


def sanitize_source_name(source: str) -> str:
    if source.startswith(("http://", "https://")):
        parsed = urlparse(source)
        name = parsed.netloc.replace(".", "_").replace(":", "_")
        path_part = parsed.path.strip("/").replace("/", "_")
        if path_part:
            name = f"{name}_{path_part}"
        return name[:80]
    else:
        return Path(source).stem.replace(" ", "_")[:80]


def generate_filename(source: str, device: DevicePreset, timestamp: str, fmt: str, step_suffix: str = "") -> str:
    source_name = sanitize_source_name(source)
    ts = timestamp.replace(":", "").replace("-", "").replace("T", "_").replace(".", "_")[:17]
    suffix = f"_{step_suffix}" if step_suffix else ""
    return f"{source_name}_{device.name}_{device.width}x{device.height}_{ts}{suffix}.{fmt}"


@dataclass
class CaptureOptions:
    full_page: bool = False
    quality: int = 90
    format: str = "png"
    wait_ms: int = 1000
    timeout_ms: int = 30000
    dark_mode: bool = False
    metadata: bool = True
    headless: bool = True
    actions: Optional[List[Action]] = None


class ActionEngine:
    def __init__(self, page: Page, output_dir: Path, device: DevicePreset, options: CaptureOptions):
        self.page = page
        self.output_dir = output_dir
        self.device = device
        self.options = options
        self.action_results: List[ActionResult] = []
        self.step_count = 0
        self.step_suffix_map: Dict[str, int] = {}

    def _get_step_suffix(self, name: Optional[str]) -> str:
        if not name:
            self.step_count += 1
            return f"step{self.step_count}"
        if name not in self.step_suffix_map:
            self.step_suffix_map[name] = 0
        self.step_suffix_map[name] += 1
        count = self.step_suffix_map[name]
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name)[:20]
        return f"{safe_name}_{count}" if count > 1 else safe_name

    async def execute_action(self, action: Action) -> ActionResult:
        t0 = time.time()
        result = ActionResult(action=action, success=False, duration_ms=0)

        try:
            if action.type == ActionType.CLICK:
                selector = action.selector
                opts = action.options or {}
                opts.setdefault("timeout", self.options.timeout_ms)
                if action.options and "force" in action.options:
                    opts["force"] = action.options["force"]
                await self.page.click(selector, **opts)
                result.success = True

            elif action.type == ActionType.FILL:
                selector = action.selector
                value = str(action.value) if action.value is not None else ""
                await self.page.fill(selector, value)
                result.success = True

            elif action.type == ActionType.SCROLL:
                x = action.value.get("x", 0) if action.value else 0
                y = action.value.get("y", 0) if action.value else 0
                await self.page.evaluate(f"window.scrollTo({x}, {y})")
                result.success = True

            elif action.type == ActionType.WAIT:
                ms = action.value if action.value else self.options.wait_ms
                await self.page.wait_for_timeout(ms)
                result.success = True

            elif action.type == ActionType.HOVER:
                selector = action.selector
                await self.page.hover(selector)
                result.success = True

            elif action.type == ActionType.PRESS:
                selector = action.selector
                key = action.value
                if selector:
                    await self.page.press(selector, key)
                else:
                    await self.page.keyboard.press(key)
                result.success = True

            elif action.type == ActionType.SELECT:
                selector = action.selector
                value = action.value
                await self.page.select_option(selector, value)
                result.success = True

            elif action.type == ActionType.WAIT_FOR_SELECTOR:
                selector = action.selector
                opts = action.options or {}
                opts.setdefault("timeout", self.options.timeout_ms)
                await self.page.wait_for_selector(selector, **opts)
                result.success = True

            elif action.type == ActionType.WAIT_FOR_NAVIGATION:
                opts = action.options or {}
                opts.setdefault("timeout", self.options.timeout_ms)
                await self.page.wait_for_load_state("networkidle", timeout=opts["timeout"])
                result.success = True

            elif action.type == ActionType.EVALUATE:
                js_code = action.value
                await self.page.evaluate(js_code)
                result.success = True

            elif action.type == ActionType.GOTO:
                url = action.value
                await self.page.goto(url, wait_until="networkidle", timeout=self.options.timeout_ms)
                result.success = True

            elif action.type == ActionType.SCREENSHOT:
                timestamp = datetime.now().isoformat()
                suffix = self._get_step_suffix(action.name)
                filename = generate_filename(
                    getattr(self, '_source', 'interactive'),
                    self.device,
                    timestamp,
                    self.options.format,
                    suffix
                )
                filepath = self.output_dir / filename

                screenshot_args = {"path": str(filepath), "full_page": False}
                if self.options.format == "jpeg":
                    screenshot_args["quality"] = self.options.quality

                await self.page.screenshot(**screenshot_args)
                result.success = filepath.exists()
                result.screenshot_path = str(filepath)

        except Exception as e:
            result.success = False
            result.error = str(e)

        result.duration_ms = int((time.time() - t0) * 1000)
        return result

    async def execute_all(self, actions: List[Action], source: str) -> List[ActionResult]:
        self._source = source
        results = []
        for action in actions:
            result = await self.execute_action(action)
            results.append(result)
            self.action_results.append(result)
            if not result.success:
                print(f"  WARNING: Action {action.type.value} failed: {result.error}")
        return results


class WebScreenshot:
    def __init__(self, output_dir: str = "./screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _build_context_args(self, device: DevicePreset, options: CaptureOptions) -> dict:
        args = {
            "viewport": {"width": device.width, "height": device.height},
            "device_scale_factor": device.dpr,
        }
        if device.user_agent:
            args["user_agent"] = device.user_agent
        if device.has_touch:
            args["has_touch"] = True
        if device.is_mobile:
            args["is_mobile"] = True
        if options.dark_mode:
            args["color_scheme"] = "dark"
        return args

    async def _capture_single_async(
        self,
        browser: Browser,
        source: str,
        device: DevicePreset,
        options: CaptureOptions,
    ) -> CaptureResult:
        timestamp = datetime.now().isoformat()
        t0 = time.time()
        result = CaptureResult(
            source=source,
            device=device.name,
            width=device.width,
            height=device.height,
            dpr=device.dpr,
            status="pending",
            timestamp=timestamp,
        )

        context = None
        try:
            context_args = self._build_context_args(device, options)
            context = await browser.new_context(**context_args)
            page = await context.new_page()

            if source.startswith(("http://", "https://")):
                await page.goto(source, wait_until="networkidle", timeout=options.timeout_ms)
            else:
                file_path = Path(source).resolve()
                if not file_path.exists():
                    raise FileNotFoundError(f"Local HTML file not found: {file_path}")
                file_url = file_path.as_uri()
                await page.goto(file_url, wait_until="networkidle", timeout=options.timeout_ms)

            await page.wait_for_timeout(options.wait_ms)

            result.page_title = await page.title()

            engine = ActionEngine(page, self.output_dir, device, options)

            if options.actions:
                action_results = await engine.execute_all(options.actions, source)
                result.actions = [
                    {"type": ar.action.type.value, "success": ar.success, "error": ar.error, "duration_ms": ar.duration_ms}
                    for ar in action_results
                ]

            filename = generate_filename(source, device, timestamp, options.format)
            filepath = self.output_dir / filename

            screenshot_args = {"path": str(filepath), "full_page": options.full_page}
            if options.format == "jpeg":
                screenshot_args["quality"] = options.quality

            await page.screenshot(**screenshot_args)

            if filepath.exists():
                result.file_path = str(filepath)
                result.file_size_kb = round(filepath.stat().st_size / 1024, 1)
                result.status = "success"
            else:
                result.status = "failed"
                result.error = "Screenshot file was not created"

            if options.metadata:
                meta = {
                    "source": source,
                    "device": device.name,
                    "device_label": device.label,
                    "device_category": device.category.value,
                    "width": device.width,
                    "height": device.height,
                    "dpr": device.dpr,
                    "timestamp": timestamp,
                    "full_page": options.full_page,
                    "dark_mode": options.dark_mode,
                    "format": options.format,
                    "file_size_kb": result.file_size_kb,
                    "page_title": result.page_title,
                    "actions_executed": len(options.actions) if options.actions else 0,
                }
                meta_filename = filename.rsplit(".", 1)[0] + ".json"
                meta_filepath = self.output_dir / meta_filename
                with open(meta_filepath, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2, ensure_ascii=False)
                result.metadata_path = str(meta_filepath)

        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            try:
                if context:
                    error_pages = context.pages
                    if error_pages:
                        error_filename = f"error_{device.name}_{int(time.time())}.png"
                        error_path = self.output_dir / error_filename
                        await error_pages[0].screenshot(path=str(error_path))
            except Exception:
                pass
        finally:
            if context:
                try:
                    await context.close()
                except Exception:
                    pass

        result.duration_ms = int((time.time() - t0) * 1000)
        return result

    async def capture_async(
        self,
        url: Optional[str] = None,
        file: Optional[str] = None,
        devices: Optional[List[DevicePreset]] = None,
        options: Optional[CaptureOptions] = None,
    ) -> List[CaptureResult]:
        source = url or file
        if not source:
            raise ValueError("Either 'url' or 'file' must be provided")
        if file and not Path(file).exists():
            raise FileNotFoundError(f"File not found: {file}")

        if devices is None:
            devices = [DevicePresets.IPHONE_14_PRO]
        if options is None:
            options = CaptureOptions()

        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=options.headless)
            try:
                tasks = [
                    self._capture_single_async(browser, source, device, options)
                    for device in devices
                ]
                results = await asyncio.gather(*tasks)
            finally:
                await browser.close()

        return list(results)

    def capture(
        self,
        url: Optional[str] = None,
        file: Optional[str] = None,
        device: Optional[DevicePreset] = None,
        devices: Optional[List[DevicePreset]] = None,
        options: Optional[CaptureOptions] = None,
        actions: Optional[List[Action]] = None,
    ) -> Union[CaptureResult, List[CaptureResult]]:
        if device and not devices:
            devices = [device]
        elif not devices:
            devices = [DevicePresets.IPHONE_14_PRO]

        if options is None:
            options = CaptureOptions()
        if actions is not None:
            options.actions = actions

        results = asyncio.run(self.capture_async(url=url, file=file, devices=devices, options=options))

        if len(results) == 1:
            return results[0]
        return results

    async def capture_batch_async(
        self,
        urls: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        devices: Optional[List[DevicePreset]] = None,
        options: Optional[CaptureOptions] = None,
    ) -> List[CaptureResult]:
        sources = []
        if urls:
            sources.extend(urls)
        if files:
            for f in files:
                if not Path(f).exists():
                    print(f"WARNING: File not found, skipping: {f}")
                else:
                    sources.append(f)

        if not sources:
            raise ValueError("No valid sources provided (urls or files)")
        if devices is None:
            devices = [DevicePresets.IPHONE_14_PRO]
        if options is None:
            options = CaptureOptions()

        all_results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=options.headless)
            try:
                for source in sources:
                    tasks = [
                        self._capture_single_async(browser, source, device, options)
                        for device in devices
                    ]
                    results = await asyncio.gather(*tasks)
                    all_results.extend(results)
            finally:
                await browser.close()

        return all_results

    def capture_batch(
        self,
        urls: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        devices: Optional[List[DevicePreset]] = None,
        options: Optional[CaptureOptions] = None,
    ) -> List[CaptureResult]:
        return asyncio.run(
            self.capture_batch_async(urls=urls, files=files, devices=devices, options=options)
        )


def parse_batch_file(filepath: str) -> List[str]:
    urls = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def print_results(results: List[CaptureResult]):
    success = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status != "success"]

    print(f"\n{'='*70}")
    print(f"  SCREENSHOT RESULTS")
    print(f"{'='*70}")
    print(f"  Total: {len(results)} | Success: {len(success)} | Failed: {len(failed)}")
    if success:
        print(f"  Output: {Path(results[0].file_path).parent if success else 'N/A'}")
    print()

    for r in results:
        icon = "OK" if r.status == "success" else "FAIL"
        size_str = f"{r.file_size_kb}KB" if r.file_size_kb else "N/A"
        action_info = f" | {len(r.actions)} actions" if r.actions else ""
        print(f"  [{icon}] {r.device} ({r.width}x{r.height}) -> {size_str} | {r.duration_ms}ms{action_info}")
        if r.file_path:
            print(f"       {r.file_path}")
        if r.error:
            print(f"       Error: {r.error[:120]}")
        if r.actions:
            for i, act in enumerate(r.actions):
                act_icon = "OK" if act.get("success") else "FAIL"
                print(f"       [{act_icon}] {i+1}. {act.get('type')}: {act.get('duration_ms', 0)}ms")
                if not act.get("success") and act.get("error"):
                    print(f"            Error: {act.get('error')[:80]}")

    print(f"{'='*70}")

    if failed:
        print(f"\n  Failed captures ({len(failed)}):")
        for r in failed:
            print(f"    - {r.source} @ {r.device}: {r.error[:100]}")


def main():
    parser = argparse.ArgumentParser(
        description="Web Screenshot Skill - Capture web page screenshots at multiple device resolutions with interactive actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Device Presets:
  Mobile:  iphone_se, iphone_14_pro, iphone_14_plus, iphone_xr, pixel_7, galaxy_s20, ipad_mini, ipad_pro
  Desktop: hd, full_hd, 2k, 4k
  Groups:  all_mobile, all_desktop, all

Action Syntax (--actions):
  click:<selector>              Click element (CSS selector or text)
  fill:<selector>:<value>        Fill input field
  scroll:<x>,<y>                Scroll to coordinates
  wait:<ms>                     Wait milliseconds (default: 1000)
  hover:<selector>              Hover over element
  press:<selector>:<key>        Press keyboard key on element
  screenshot[:<name>]           Take screenshot with optional name
  wait_for_selector:<selector>  Wait for element to appear
  evaluate:<js>                 Execute JavaScript
  goto:<url>                     Navigate to URL

Action Examples:
  python web_screenshot.py --url "https://example.com" --actions "click:#menu;wait:500;screenshot:menu_open"
  python web_screenshot.py --url "https://example.com" --actions "fill:#username:test;fill:#password:123;screenshot"
  python web_screenshot.py --file "./index.html" --actions "scroll:0,500;wait:300;screenshot:scrolled"

CLI Examples:
  python web_screenshot.py --url "https://example.com"
  python web_screenshot.py --file "./index.html" --devices "iphone_se,full_hd"
  python web_screenshot.py --url "https://example.com" --devices "all_mobile" --full-page
  python web_screenshot.py --batch-file "./urls.txt" --devices "all"
        """,
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--url", help="URL to screenshot (http/https)")
    source_group.add_argument("--file", help="Local HTML file path to screenshot")
    source_group.add_argument("--batch-file", help="Text file with one URL per line")

    parser.add_argument("--devices", default="iphone_14_pro",
        help="Comma-separated device presets or groups (default: iphone_14_pro)")
    parser.add_argument("--width", type=int, help="Custom viewport width (overrides device preset)")
    parser.add_argument("--height", type=int, help="Custom viewport height (overrides device preset)")
    parser.add_argument("--output", default="./screenshots", help="Output directory (default: ./screenshots)")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--quality", type=int, default=90, help="Image quality 1-100 (default: 90)")
    parser.add_argument("--format", choices=["png", "jpeg"], default="png", help="Output format (default: png)")
    parser.add_argument("--wait", type=int, default=1000, help="Wait after load in ms (default: 1000)")
    parser.add_argument("--timeout", type=int, default=30000, help="Page load timeout in ms (default: 30000)")
    parser.add_argument("--dark-mode", action="store_true", help="Enable dark mode")
    parser.add_argument("--no-metadata", action="store_true", help="Skip metadata JSON sidecar")
    parser.add_argument("--no-headless", action="store_true", help="Run browser visibly (debug)")
    parser.add_argument("--actions", help="Interactive actions (semicolon-separated)")

    args = parser.parse_args()

    devices = DevicePresets.resolve(args.devices)

    if args.width and args.height:
        custom = DevicePreset(
            name=f"custom_{args.width}x{args.height}",
            label=f"Custom {args.width}x{args.height}",
            width=args.width,
            height=args.height,
            dpr=1.0,
            category=DeviceCategory.DESKTOP,
        )
        devices = [custom]

    if not devices:
        print("ERROR: No valid device presets specified")
        sys.exit(2)

    parsed_actions = None
    if args.actions:
        parsed_actions = parse_action_string(args.actions)
        if not parsed_actions:
            print("ERROR: No valid actions specified")
            sys.exit(2)
        print(f"Actions: {len(parsed_actions)} action(s) configured")

    options = CaptureOptions(
        full_page=args.full_page,
        quality=args.quality,
        format=args.format,
        wait_ms=args.wait,
        timeout_ms=args.timeout,
        dark_mode=args.dark_mode,
        metadata=not args.no_metadata,
        headless=not args.no_headless,
        actions=parsed_actions,
    )

    capturer = WebScreenshot(output_dir=args.output)

    try:
        if args.batch_file:
            urls = parse_batch_file(args.batch_file)
            if not urls:
                print("ERROR: No URLs found in batch file")
                sys.exit(2)
            print(f"Batch mode: {len(urls)} URLs x {len(devices)} devices = {len(urls) * len(devices)} screenshots")
            results = capturer.capture_batch(urls=urls, devices=devices, options=options)
        elif args.url:
            print(f"Capturing: {args.url} @ {len(devices)} device(s)")
            results = capturer.capture(url=args.url, devices=devices, options=options, actions=parsed_actions)
            if isinstance(results, CaptureResult):
                results = [results]
        elif args.file:
            print(f"Capturing: {args.file} @ {len(devices)} device(s)")
            results = capturer.capture(file=args.file, devices=devices, options=options, actions=parsed_actions)
            if isinstance(results, CaptureResult):
                results = [results]
        else:
            print("ERROR: No source specified")
            sys.exit(2)

        print_results(results)

        success_count = sum(1 for r in results if r.status == "success")
        fail_count = sum(1 for r in results if r.status != "success")

        if fail_count == 0:
            sys.exit(0)
        elif success_count > 0:
            sys.exit(1)
        else:
            sys.exit(2)

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(2)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()

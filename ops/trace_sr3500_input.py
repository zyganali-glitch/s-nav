from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

try:
    import keyboard
except Exception:  # pragma: no cover - best-effort optional runtime
    keyboard = None

try:
    import pywinusb.hid as hid
except Exception as error:  # pragma: no cover - import failure should stop the script
    raise SystemExit(f"pywinusb import edilemedi: {error}") from error


DEFAULT_TARGETS = ((0x0A41, 0x1004), (0x0461, 0x4DBF))


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class TraceWriter:
    def __init__(self, output_path: Path | None) -> None:
        self.output_path = output_path
        self.handle = None
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.handle = output_path.open("a", encoding="utf-8", buffering=1)

    def write(self, message: str) -> None:
        line = f"[{timestamp()}] {message}"
        print(line)
        if self.handle:
            self.handle.write(line + "\n")

    def close(self) -> None:
        if self.handle:
            self.handle.close()
            self.handle = None


@dataclass(frozen=True)
class HidTarget:
    vendor_id: int
    product_id: int

    @property
    def label(self) -> str:
        return f"VID_{self.vendor_id:04X}&PID_{self.product_id:04X}"


def parse_target(text: str) -> HidTarget:
    normalized = text.strip().replace("VID_", "").replace("PID_", "").replace("0x", "")
    for separator in (":", "&", ",", "/", " "):
        if separator in normalized:
            left, right = [part for part in normalized.split(separator) if part]
            return HidTarget(int(left, 16), int(right, 16))
    raise argparse.ArgumentTypeError(f"Hedef aygit formati gecersiz: {text}")


def describe_device(device: hid.HidDevice) -> str:
    vendor_name = getattr(device, "vendor_name", "") or "BilinmeyenVendor"
    product_name = getattr(device, "product_name", "") or "BilinmeyenAygit"
    usage_page = getattr(device, "usage_page", None)
    usage = getattr(device, "usage", None)
    path = getattr(device, "device_path", "") or "-"
    return (
        f"{vendor_name} | {product_name} | VID_{device.vendor_id:04X}&PID_{device.product_id:04X} | "
        f"usage_page={usage_page} usage={usage} | path={path}"
    )


def build_raw_handler(writer: TraceWriter, device_label: str, counters: dict[str, int]) -> Callable[[list[int]], None]:
    def handle_raw_data(data: list[int]) -> None:
        counters["hid"] += 1
        payload = " ".join(f"{byte:02X}" for byte in data)
        writer.write(f"HID_EVENT {device_label} payload={payload}")

    return handle_raw_data


def attach_hid_handlers(writer: TraceWriter, targets: list[HidTarget], counters: dict[str, int]) -> list[hid.HidDevice]:
    selected = []
    all_devices = hid.find_all_hid_devices()
    writer.write(f"Toplam HID aygit sayisi: {len(all_devices)}")

    target_pairs = {(item.vendor_id, item.product_id) for item in targets}
    matching = [device for device in all_devices if (device.vendor_id, device.product_id) in target_pairs]
    if not matching:
        writer.write("Hedef VID/PID icin eslesen HID aygit bulunamadi.")
        return selected

    writer.write("Eslesen HID aygitlar:")
    for device in matching:
        writer.write(f"  - {describe_device(device)}")

    for device in matching:
        try:
            device.open()
            device.set_raw_data_handler(build_raw_handler(writer, describe_device(device), counters))
            selected.append(device)
            writer.write(f"HID_LISTENING {describe_device(device)}")
        except Exception as error:  # pragma: no cover - device open depends on Windows driver state
            writer.write(f"HID_OPEN_FAIL {describe_device(device)} error={error}")

    return selected


def attach_keyboard_hook(writer: TraceWriter, counters: dict[str, int]):
    if keyboard is None:
        writer.write("keyboard kutuphanesi yuklenemedi; global keyboard event hook pas gecildi.")
        return None

    def handle_key(event) -> None:
        counters["keyboard"] += 1
        writer.write(
            f"KEY_EVENT type={event.event_type} name={event.name!r} scan_code={event.scan_code} device={getattr(event, 'device', None)!r}"
        )

    keyboard.hook(handle_key)
    writer.write("Global keyboard hook aktif.")
    return handle_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sekonic SR-3500 icin Windows seviyesinde keyboard ve ham HID event tracer",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=120,
        help="Dinleme suresi saniye cinsinden. Varsayilan: 120",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("C:/SecureExam/probe-output/sr3500-live-trace.log"),
        help="Log dosya yolu.",
    )
    parser.add_argument(
        "--target",
        type=parse_target,
        action="append",
        help="Ek VID:PID hedefi. Varsayilan hedefler SR-3500 icin bilinen 0A41:1004 ve 0461:4DBF ciftleridir.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    targets = args.target or [HidTarget(*pair) for pair in DEFAULT_TARGETS]
    counters = {"hid": 0, "keyboard": 0}
    writer = TraceWriter(args.output)

    writer.write("SR-3500 input trace basladi.")
    writer.write("Hedef aygitlar: " + ", ".join(target.label for target in targets))

    devices = []
    keyboard_hook = None
    try:
        devices = attach_hid_handlers(writer, targets, counters)
        keyboard_hook = attach_keyboard_hook(writer, counters)
        writer.write(
            "Simdi SR-3500 ile bir form okut. Bu sure boyunca gelen keyboard event veya ham HID raporlari loglanacak."
        )

        deadline = time.monotonic() + max(1, args.duration)
        while time.monotonic() < deadline:
            time.sleep(0.25)
    except KeyboardInterrupt:
        writer.write("Trace kullanici tarafindan kesildi.")
    finally:
        if keyboard is not None and keyboard_hook is not None:
            try:
                keyboard.unhook(keyboard_hook)
            except Exception:
                pass
        for device in devices:
            try:
                device.close()
            except Exception:
                pass
        writer.write(
            f"Trace bitti. keyboard_event={counters['keyboard']} hid_event={counters['hid']} output={args.output}"
        )
        writer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

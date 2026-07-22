"""MCU database — specs, peripherals, memory maps."""
from __future__ import annotations
from typing import Optional


class MCUInfo:
    def __init__(self, name: str, arch: str, core: str,
                 flash_kb: int, ram_kb: int, freq_mhz: int,
                 rtos_compat: Optional[list[str]] = None,
                 toolchain: str = "gcc",
                 has_fpu: bool = False,
                 has_dsp: bool = False,
                 vendor: str = "",
                 refs: Optional[list[str]] = None):
        self.name = name
        self.arch = arch
        self.core = core
        self.flash_kb = flash_kb
        self.ram_kb = ram_kb
        self.freq_mhz = freq_mhz
        self.rtos_compat = rtos_compat or []
        self.toolchain = toolchain
        self.has_fpu = has_fpu
        self.has_dsp = has_dsp
        self.vendor = vendor
        self.refs = refs or []


MCUS: dict[str, MCUInfo] = {}

def register(m: MCUInfo):
    MCUS[m.name.lower()] = m


# --- ESP32 series ---
register(MCUInfo("ESP32", "xtensa", "LX6", 4096, 520, 240,
    rtos_compat=["freertos", "esp-idf", "dso-tron"],
    has_fpu=False, has_dsp=True, vendor="Espressif",
    refs=["ESP32 Technical Reference Manual"]))

register(MCUInfo("ESP32-S3", "xtensa", "LX7", 512, 384, 240,
    rtos_compat=["freertos", "esp-idf"],
    has_fpu=False, has_dsp=True, vendor="Espressif"))

register(MCUInfo("ESP32-C3", "riscv", "RV32IMC", 384, 400, 160,
    rtos_compat=["freertos", "esp-idf"],
    has_fpu=False, has_dsp=False, vendor="Espressif"))

# --- ARM Cortex-M ---
register(MCUInfo("STM32F103", "arm", "Cortex-M3", 512, 64, 72,
    rtos_compat=["freertos", "toppers", "t-kernel"],
    has_fpu=False, has_dsp=False, vendor="ST"))

register(MCUInfo("STM32F407", "arm", "Cortex-M4F", 1024, 192, 168,
    rtos_compat=["freertos", "toppers", "t-kernel"],
    has_fpu=True, has_dsp=True, vendor="ST"))

register(MCUInfo("STM32H743", "arm", "Cortex-M7", 2048, 864, 480,
    rtos_compat=["freertos", "toppers"],
    has_fpu=True, has_dsp=True, vendor="ST"))

register(MCUInfo("RP2040", "arm", "Cortex-M0+", 2048, 264, 133,
    rtos_compat=["freertos", "toppers"],
    has_fpu=False, has_dsp=False, vendor="Raspberry Pi",
    refs=["RP2040 Datasheet"]))

# --- Linux-capable ---
register(MCUInfo("BCM2711", "arm", "Cortex-A72", 0, 0, 1500,
    rtos_compat=["linux", "freertos"],
    has_fpu=True, has_dsp=True, vendor="Broadcom",
    refs=["Raspberry Pi 4"]))  # flash/ram not applicable

register(MCUInfo("Intel 64", "x86", "x86-64", 0, 0, 0,
    rtos_compat=["linux", "dso-tron"],
    has_fpu=True, has_dsp=True, vendor="Intel"))

# --- Legacy / Academic ---
register(MCUInfo("TI-MSP430", "msp430", "MSP430", 128, 8, 16,
    rtos_compat=["toppers"],
    has_fpu=False, has_dsp=False, vendor="TI"))

register(MCUInfo("RL78", "rl78", "RL78", 256, 20, 32,
    rtos_compat=["toppers"],
    has_fpu=False, has_dsp=False, vendor="Renesas"))


def get_mcu(name: str) -> Optional[dict]:
    key = name.lower()
    if key in MCUS:
        return _to_dict(MCUS[key])
    for k, v in MCUS.items():
        if key in k or k in key:
            return _to_dict(v)
    return None

def list_mcus(vendor: str = "", arch: str = "") -> list[dict]:
    results = []
    for m in MCUS.values():
        if vendor and vendor.lower() not in m.vendor.lower():
            continue
        if arch and m.arch != arch:
            continue
        results.append(_to_dict(m))
    return sorted(results, key=lambda x: x["name"])

def _to_dict(m: MCUInfo) -> dict:
    return {
        "name": m.name,
        "arch": m.arch,
        "core": m.core,
        "flash_kb": m.flash_kb,
        "ram_kb": m.ram_kb,
        "freq_mhz": m.freq_mhz,
        "has_fpu": m.has_fpu,
        "has_dsp": m.has_dsp,
        "toolchain": m.toolchain,
        "rtos": m.rtos_compat,
        "vendor": m.vendor,
    }

"""sint-embed-mcp — embedded systems specialist (fastmcp, stdio).

MCU database, RTOS patterns, linker script generation,
startup code, and embedded build system helpers.

Tools:
  list_mcus(vendor, arch)      — catalogue MCUs
  get_mcu(name)                — detailed MCU specs
  list_rtoses()                — RTOS comparison
  get_rtos(name)               — RTOS details
  gen_linker_script(mcu, arch) — generate linker script
  gen_startup(arch, mcu)       — generate startup code
  recommend_rtos(arch, ram)    — suggest best RTOS for constraints
  compare_rtoses(names)        — side-by-side RTOS comparison
  embed_help()                 — usage guide

Run: python server.py (stdio)
"""
from __future__ import annotations

import json

from fastmcp import FastMCP

from config import NAME, VERSION, SUPPORTED_ARCHS, SUPPORTED_RTOS
from mcu_db.mcus import get_mcu, list_mcus, MCUS, MCUInfo
from rtos.patterns import get_rtos, list_rtoses, RTOSES
from gen.linker import generate_linker_script, generate_startup_code

mcp = FastMCP(NAME)


@mcp.tool()
def list_mcus_tool(vendor: str = "", arch: str = "") -> str:
    """List MCUs in the database.

    Args:
        vendor: filter by vendor (e.g. 'ST', 'Espressif', 'Raspberry')
        arch: filter by arch ('arm', 'xtensa', 'riscv', 'x86')
    Returns: JSON array of MCU summaries.
    """
    results = list_mcus(vendor=vendor, arch=arch)
    return json.dumps({
        "total": len(results),
        "mcus": results,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def get_mcu_info(name: str) -> str:
    """Get detailed information about a specific MCU.

    Args:
        name: MCU name (e.g. 'ESP32', 'STM32F103')
    Returns: JSON with full specs.
    """
    m = get_mcu(name)
    if not m:
        return json.dumps({"error": f"MCU '{name}' not found",
                           "suggestions": sorted(m.name for m in MCUS.values())})
    return json.dumps(m, ensure_ascii=False, indent=1)


@mcp.tool()
def list_rtoses_tool() -> str:
    """List all known RTOSes with their characteristics.

    Returns: JSON array of RTOS info.
    """
    results = list_rtoses()
    return json.dumps({
        "total": len(results),
        "rtoses": results,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def get_rtos_info(name: str) -> str:
    """Get detailed information about a specific RTOS.

    Args:
        name: RTOS name (e.g. 'ITRON', 'FreeRTOS', 'DSO-TRON')
    Returns: JSON with RTOS details.
    """
    r = get_rtos(name)
    if not r:
        return json.dumps({"error": f"RTOS '{name}' not found",
                           "available": sorted(r.name for r in RTOSES.values())})
    return json.dumps(r, ensure_ascii=False, indent=1)


@mcp.tool()
def recommend_rtos(arch: str, ram_kb: int = 64, flash_kb: int = 256,
                   hard_real_time: bool = False) -> str:
    """Suggest the best RTOS for given hardware constraints.

    Args:
        arch: target architecture ('arm', 'xtensa', 'riscv')
        ram_kb: available RAM in KB
        flash_kb: available flash in KB
        hard_real_time: if True, prefer deterministic scheduling
    Returns: JSON with recommendations.
    """
    candidates = []
    for r in RTOSES.values():
        if r.min_ram_kb > ram_kb:
            continue
        score = 0
        if r.name.lower() in ("dso-tron", "itron"):
            score += 2  # deterministic
        if hard_real_time and "time-triggered" in r.sched_policy.lower():
            score += 3
        if arch == "arm" and r.name in ("FreeRTOS", "TOPPERS", "Zephyr"):
            score += 1
        if arch == "xtensa" and r.name == "FreeRTOS":
            score += 1

        candidates.append({
            "rtos": r.name,
            "score": score,
            "api": r.api_lang,
            "scheduling": r.sched_policy,
            "ipc": r.ipc_primitives,
            "min_ram": r.min_ram_kb,
            "license": r.license,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return json.dumps({
        "constraints": {"arch": arch, "ram_kb": ram_kb,
                        "hard_real_time": hard_real_time},
        "recommendations": candidates,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def gen_linker(mcu_name: str, arch: str = "arm",
              ram_kb: int = 64, flash_kb: int = 512) -> str:
    """Generate a linker script for an MCU.

    Args:
        mcu_name: name of the MCU
        arch: architecture ('arm', 'xtensa', 'riscv')
        ram_kb: RAM size in KB
        flash_kb: flash size in KB
    Returns: linker script as text.
    """
    ld = generate_linker_script(mcu_name, ram_kb, flash_kb, arch)
    return json.dumps({
        "mcu": mcu_name,
        "arch": arch,
        "language": "linker-script",
        "code": ld,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def gen_startup(arch: str = "arm", mcu_name: str = "generic") -> str:
    """Generate minimal startup assembly code.

    Args:
        arch: architecture ('arm' only for now)
        mcu_name: MCU name for comments
    Returns: assembly startup code.
    """
    code = generate_startup_code(arch, mcu_name)
    return json.dumps({
        "mcu": mcu_name,
        "arch": arch,
        "language": "assembly",
        "code": code,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def compare_rtoses(rtos_names: str) -> str:
    """Compare multiple RTOS side by side.

    Args:
        rtos_names: comma-separated (e.g. 'ITRON,FreeRTOS,DSO-TRON')
    Returns: JSON comparison table.
    """
    names = [n.strip() for n in rtos_names.split(",")]
    results = []
    for name in names:
        r = get_rtos(name)
        if r:
            results.append(r)
        else:
            results.append({"name": name, "error": "not found"})
    return json.dumps({
        "comparison": results,
        "count": len(results),
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def embed_help() -> str:
    """Get usage guide for sint-embed-mcp."""
    return json.dumps({
        "description": "sint-embed-mcp — Embedded systems knowledge base",
        "tools": {
            "list_mcus_tool": "list_mcus_tool(vendor='ST') — STM32 MCUs",
            "get_mcu_info": "get_mcu_info('ESP32') — ESP32 specs",
            "list_rtoses_tool": "list_rtoses_tool() — all RTOSes",
            "recommend_rtos": "recommend_rtos('arm', 64, 256) — best RTOS",
            "gen_linker": "gen_linker('STM32F407', 'arm', 192, 1024) — linker script",
            "gen_startup": "gen_startup('arm') — startup code",
            "compare_rtoses": "compare_rtoses('ITRON,FreeRTOS')",
        },
        "supported_archs": SUPPORTED_ARCHS,
        "examples": [
            "Find MCU: get_mcu_info('ESP32')",
            "Generate linker: gen_linker('STM32F103', 'arm', 64, 512)",
            "Recommend RTOS: recommend_rtos('xtensa', 320, 4096)",
        ],
    }, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")

# sint-embed-mcp

Embedded systems specialist MCP server for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent ecosystem.

MCU database, RTOS patterns, linker script generation, and startup code helpers for working with resource-constrained targets.

## Features

- **MCU Database** — ESP32, STM32, RP2040, and more with full specs
- **RTOS Patterns** — ITRON, TOPPERS, T-Kernel, FreeRTOS, DSO-TRON
- **Code Generation** — linker scripts and startup code for any target
- **RTOS Recommendation** — suggest best RTOS for hardware constraints

## Tools

| Tool | Description |
|---|---|
| `list_mcus(vendor, arch)` | Catalogue MCUs by vendor/architecture |
| `get_mcu(name)` | Detailed MCU specifications |
| `list_rtoses()` | RTOS comparison overview |
| `get_rtos(name)` | RTOS details and patterns |
| `recommend_rtos(arch, ram, flash, hard_real_time)` | Best RTOS for constraints |
| `compare_rtoses(names)` | Side-by-side RTOS comparison |
| `gen_linker_script(mcu, arch)` | Generate linker script |
| `gen_startup(arch, mcu)` | Generate startup code |
| `embed_help()` | Usage guide |

## Supported Architectures

| Arch | MCUs | RTOSes |
|---|---|---|
| ARM Cortex-M | STM32F103, STM32F407, RP2040 | FreeRTOS, TOPPERS, ITRON |
| Xtensa | ESP32, ESP32-S3 | FreeRTOS |
| RISC-V | GD32VF103 | FreeRTOS, DSO-TRON |

## RTOS Patterns

### ITRON / TOPPERS / T-Kernel

Japanese real-time OS family for embedded systems. Deterministic, lightweight, proven in automotive and industrial.

- **ITRON**: Specification standard (TRON Project)
- **TOPPERS**: Open-source ITRON implementation
- **T-Kernel**: Successor to ITRON, adds memory protection

### FreeRTOS

Industry-standard open-source RTOS. Wide MCU support, active community.

### DSO-TRON

Deterministic task graph execution. Arena allocator, typed pools, WCET contracts.

## Code Generation

### Linker Script

```python
gen_linker_script(mcu="STM32F103", arch="arm")
# → Complete .ld file with flash/RAM sections, stack, heap
```

### Startup Code

```python
gen_startup(arch="arm", mcu="RP2040")
# → Vector table, Reset_Handler, SystemInit, .data/.bss init
```

## Setup

```bash
pip install fastmcp
```

## Run

```bash
python server.py    # stdio mode
```

## Integration

Use when:
- Choosing MCU + RTOS for a new embedded project
- Generating boilerplate (linker scripts, startup code)
- Comparing RTOS options for specific constraints

## License

MIT

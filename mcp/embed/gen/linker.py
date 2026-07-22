"""Linker script generator for embedded projects."""
from __future__ import annotations


def generate_linker_script(mcu_name: str, ram_kb: int = 64,
                           flash_kb: int = 512, arch: str = "arm") -> str:
    """Generate a minimal linker script for an MCU."""
    if arch == "arm":
        return _arm_ld(mcu_name, ram_kb, flash_kb)
    elif arch == "xtensa":
        return _xtensa_ld(mcu_name, ram_kb, flash_kb)
    elif arch == "riscv":
        return _riscv_ld(mcu_name, ram_kb, flash_kb)
    else:
        return f"/* No linker template for {arch} */"


def _arm_ld(name: str, ram: int, flash: int) -> str:
    return f"""/* Linker script for {name} — ARM Cortex-M */
/* RAM: {ram}K, Flash: {flash}K */

MEMORY
{{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = {flash}K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = {ram}K
}}

SECTIONS
{{
    .text : {{
        KEEP(*(.isr_vector))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
        _etext = .;
    }} > FLASH

    .data : {{
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    }} > RAM AT > FLASH

    .bss : {{
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    }} > RAM

    .heap : {{
        . = ALIGN(8);
        _heap_start = .;
        . += {max(4, ram // 4)}K;
        _heap_end = .;
    }} > RAM

    .stack : {{
        . = ALIGN(8);
        _stack_top = .;
        . += 2K;
    }} > RAM
}}
"""


def _xtensa_ld(name: str, ram: int, flash: int) -> str:
    return f"""/* Linker script for {name} — Xtensa LX6/LX7 */
/* RAM: {ram}K, Flash: {flash}K */

MEMORY
{{
    IROM (rx)   : ORIGIN = 0x40000000, LENGTH = {flash}K
    DROM (r)    : ORIGIN = 0x3F400000, LENGTH = 4K
    DRAM (rw)   : ORIGIN = 0x3FF80000, LENGTH = {max(ram - 64, 4)}K
    IRAM (rwx)  : ORIGIN = 0x40080000, LENGTH = 64K
}}

SECTIONS
{{
    .text : {{ *(.text*) *(.literal*) }} > IROM
    .rodata : {{ *(.rodata*) }} > DROM
    .data : {{ *(.data*) }} > DRAM
    .bss : {{ *(.bss*) *(COMMON) }} > DRAM
}}
"""


def _riscv_ld(name: str, ram: int, flash: int) -> str:
    return f"""/* Linker script for {name} — RISC-V RV32 */
/* RAM: {ram}K, Flash: {flash}K */

MEMORY
{{
    FLASH (rx)  : ORIGIN = 0x20000000, LENGTH = {flash}K
    RAM   (rwx) : ORIGIN = 0x80000000, LENGTH = {ram}K
}}

SECTIONS
{{
    .text : {{ *(.text*) *(.rodata*) }} > FLASH
    .data : {{ *(.data*) }} > RAM AT > FLASH
    .bss  : {{ *(.bss*) *(COMMON) }} > RAM
}}
"""


def generate_startup_code(arch: str, mcu_name: str) -> str:
    """Generate minimal startup code (reset handler + vector table)."""
    if arch == "arm":
        return _arm_startup(mcu_name)
    return f"/* No startup template for {arch} */"


def _arm_startup(name: str) -> str:
    return f"""/* Minimal startup code for {name} — ARM Cortex-M */
.syntax unified
.cpu cortex-m3
.thumb

.global _start
.global _estack

.word _stack_top
.word _start
.word _nmi_handler
.word _hardfault_handler

.thumb_func
_start:
    ldr r1, =_sbss
    ldr r2, =_ebss
    movs r0, 0
bss_loop:
    cmp r1, r2
    bge data_copy
    str r0, [r1], #4
    b bss_loop

data_copy:
    ldr r1, =_sdata
    ldr r2, =_edata
    ldr r3, =_etext
copy_loop:
    cmp r1, r2
    bge main_call
    ldr r0, [r3], #4
    str r0, [r1], #4
    b copy_loop

main_call:
    bl main
    b .

.thumb_func
_nmi_handler:
    b .

.thumb_func
_hardfault_handler:
    b .
"""

"""RTOS pattern library — ITRON, TOPPERS, T-Kernel, FreeRTOS, DSO-TRON."""
from __future__ import annotations


class RTOSInfo:
    def __init__(self, name: str, api_lang: str, task_model: str,
                 ipc_primitives: list[str], sched_policy: str,
                 min_ram_kb: int = 4, license: str = "",
                 refs: Optional[list[str]] = None):
        self.name = name
        self.api_lang = api_lang
        self.task_model = task_model
        self.ipc_primitives = ipc_primitives
        self.sched_policy = sched_policy
        self.min_ram_kb = min_ram_kb
        self.license = license
        self.refs = refs or []


RTOSES: dict[str, RTOSInfo] = {}

def register(r: RTOSInfo):
    RTOSES[r.name.lower()] = r


register(RTOSInfo("ITRON", "C", "task+semaphore+eventflag",
    ["semaphore", "eventflag", "mailbox", "dataqueue", "mutex"],
    "fixed-priority preemptive", 8, "Open (TRON)", ["ITRON 4.0 Spec"]))

register(RTOSInfo("TOPPERS", "C", "task+alarm+cyclic",
    ["semaphore", "eventflag", "dataqueue", "mailbox"],
    "fixed-priority preemptive", 8, "TOPPERS License",
    ["TOPPERS FMP Kernel"]))

register(RTOSInfo("T-Kernel", "C", "task+event+cyclic",
    ["semaphore", "eventflag", "mailbox", "mutex", "message_buffer"],
    "fixed-priority + round-robin", 16, "T-Engine License",
    ["T-Kernel 2.0 Spec"]))

register(RTOSInfo("FreeRTOS", "C", "task+queue",
    ["queue", "semaphore", "mutex", "event_group", "stream_buffer"],
    "fixed-priority + round-robin", 4, "MIT",
    ["FreeRTOS Reference"]))

register(RTOSInfo("DSO-TRON", "C", "task+level+epoch",
    ["spsc_queue", "flag", "seqlock"],
    "time-triggered + priority", 8, "MIT",
    ["dso-tron spec", "ITRON-inspired"]))

register(RTOSInfo("Zephyr", "C", "thread+queue",
    ["fifo", "lifo", "stack", "message_queue", "mutex", "semaphore"],
    "preemptive + cooperative", 8, "Apache 2.0",
    ["Zephyr Project"]))

register(RTOSInfo("NuttX", "C", "task+pthread",
    ["mq", "sem", "mutex", "cond", "signal"],
    "fixed-priority preemptive", 8, "BSD",
    ["Apache NuttX"]))


def get_rtos(name: str) -> Optional[dict]:
    key = name.lower()
    if key in RTOSES:
        return _to_dict(RTOSES[key])
    for k, v in RTOSES.items():
        if key in k or k in key:
            return _to_dict(v)
    return None

def list_rtoses() -> list[dict]:
    return sorted([_to_dict(r) for r in RTOSES.values()],
                  key=lambda x: x["name"])

def _to_dict(r: RTOSInfo) -> dict:
    return {
        "name": r.name,
        "api_lang": r.api_lang,
        "task_model": r.task_model,
        "ipc": r.ipc_primitives,
        "scheduling": r.sched_policy,
        "min_ram_kb": r.min_ram_kb,
        "license": r.license,
        "refs": r.refs,
    }

---
name: state
description: Use for session management, project status tracking, continuation prompts. Session working memory: current focus, active projects, pending decisions, verified patterns, session log. Read at session start.
---

> Persistent working memory. Updated by agent at end of every session.
> Read this at the start of every session before doing anything else.

## CURRENT FOCUS
> What is actively being worked on right now. Max 3 items.

1. **DSA** — add DSP chain + 3D spatialization to mixer; then git init + push to GitHub
2. **DataTrace** — taint engine + live taint tracking working; then git init + push + README
3. **100 Orange Juice** — `data.ojd` = encrypted SQLite 3.49.1; recover `logiovfs` xRead key to decrypt full DB offline

## ACTIVE PROJECTS

### DSO — Deterministic Streaming OS
### MPTC — Memory Allocator
### DataTrace — LD_PRELOAD + eBPF Taint Tracker
  - Path: /home/lain/datatrace/dtrace/
  - `taint.py`: TaintEngine — 64-bit bitmask labels (T_NETWORK/T_FILE/T_ARGV/T_HEAP...),
    interval-map shadow memory, L_union/L_intersect, sinks, TaintReport, flow_dot
  - Integrated into tracer.py (ProcessTracer.taint), collector.py (feed_events + run_live),
    cli.py (subcommands `taint --dot`, `run --taint --emit flow:out.dot`)
  - preload.c: LD_PRELOAD agent hooks malloc/free/memcpy/recvfrom/sendto -> EV_* JSONL on stderr
  - VERIFIED live: recvfrom->memcpy->sendto flagged UNTRUSTED; const memcpy->sendto clean
  - PUSHED to GitHub: https://github.com/kostyk348/datatrace
### DSA — Data-oriented Streaming Audio
  - Open FMOD replacement at /home/lain/dsa/
  - ALSA output, 275 C++ ABI symbols exported (205 core + 70 studio const)
  - SONAME: libfmod.so.14 / libfmodstudio.so.14 with versioned symlinks
  - Verified: GodotFmod + both DSA .so load clean via RPATH
  - DONE: 15 DSP effects in mixer.c + DSA_DSPState (dsa_internal.h), per-DSP alloc/free
  - DONE: real 3D spatialization (inverse-rolloff attenuation + azimuth pan by listener vectors);
    min/max_distance SoA fields; DSA_Channel_Set3DMinMaxDistance wired
  - DONE: pitch resample via linear interp; hash-chain audit already in arena.c
  - Verified: make rc=0, example rc=0, DSP smoke 0 failures, 3D attenuation near=0.25 far=0.0025
  - PUSHED to GitHub: https://github.com/kostyk348/dsa

## PENDING DECISIONS
> Questions that are open and need a decision before proceeding.

- **100 OJ RE approach**: what order to reverse subsystems? (pak format → asset loading → audio → rendering → gameplay)
- **AGT scope**: just audio, or full board-game constructor engine?
- **data.ojd full content**: (a) RE `logiovfs` VFS `xRead` to extract key/algorithm → decrypt the full 1,339,392-B ciphertext offline (no display needed); OR (b) run game to a state that reads all 327 pages (needs Xvfb/display — not installed). Option (a) preferred.

## VERIFIED THIS WEEK
> Patterns confirmed in recent sessions. Agent moves these to dso.md after verification.

- **Arena + SoA for audio mixer**: DSA uses per-type bump arena + SoA channel layout. Tick-boundary bulk-free. Works.
- **C function for C++ ABI symbols**: defining `_ZN4FMOD*` and `_ZNK4FMOD*` symbols as plain C functions (name = exact mangled symbol) is the simplest way to export C++ ABI without a C++ compiler. Verified: 275 symbols (205 core + 70 studio const), STS2 GodotFmod loads.
- **FMOD Studio C ABI → DSA mapping**: Studio Create/Release/GetCoreSystem all route to DSA_System. Studio C++ ABI symbols just call C ABI functions.
- **SONAME for versioned FMOD**: GodotFmod DT_NEEDED is libfmod.so.14 / libfmodstudio.so.14. Setting `-Wl,-soname,libfmod.so.14` + .so.14 symlinks resolves RPATH+LD_LIBRARY_PATH.
- **DSA 3D attenuation inverse-rolloff**: near peak=0.25, far(200m)=0.0025 — matches expected curve.
- **DataTrace live taint (sendto bug fixed)**: sendto sink must query the BUFFER addr, not the socket fd. Preload emits `addr=buf, addr2=sockfd`; engine now queries both `addr` and `addr2` and unions (convention-independent). recvfrom->memcpy->sendto flagged UNTRUSTED=1; const memcpy->sendto stays clean (0). Synthetic /tmp/taint_test.py assertions pass.

## OPEN EXPERIMENTS
> Things being tested but not yet verified.

- **LD_PRELOAD with multiple .so files**: libfmod.so + libfmodstudio.so intercepted simultaneously. Works on STS2.
- **DataTrace eBPF mode**: currently LD_PRELOAD-only; eBPF backend not yet wired.

## SESSION LOG
> Last 5 sessions. Agent appends, old entries drop off.

1. **2026-07-13c**: 100 OJ `data.ojd` IDENTITY SOLVED. It is an **encrypted SQLite 3.49.1** DB (327 pages × 4096 B, 1,339,392 B) stored uncompressed in strings.pak as entry `data.ojd`; `{}str/data.ojd` = encryption marker. Decryption is in custom SQLite VFS `logiovfs` (`sqlitevfs::SQLiteVfsImpl<LogIOFileShim>`); loader `0x1426830` (from `0x1434bf0`) parses the already-decrypted DB. CORRECTION to 2026-07-13b: the `call *0x18(%r14)` at 0x1426820 was std::string internals, NOT the decrypt; loader `0x1426830` is a C++-struct parser, NOT a std::hash integrity check. LD_PRELOAD memcpy/memmove trap captured page 1 plaintext ("SQLite format 3") + 264/324 pages (schema overflow pages in gaps; headless game lazy-reads). Full ciphertext + partial schema + reusable preload tooling saved under dsa/100OJ/extracted/ and dsa/100OJ/tools/. Cipher = stream cipher (keystream page0 known: be bf ca 0b …); full decrypt needs `xRead` key/algorithm RE.
2. **2026-07-13b (superseded)**: earlier wrong theory — data.ojd decrypt = vtable dispatch, loader = std::hash check. WRONG; see 2026-07-13c.
3. **2026-07-13a**: 100 OJ RE via DataTrace tracer. Engine = LUNA (raylib fork) + RmlUi + Lua 5.4.6; .pak=ZIP; Lua card-model = layered render pipeline; .fld = LE uint32. data.ojd = high-entropy (not zlib/gzip). Pushed.
4. **2026-07-11**: DataTrace taint engine sendto bug fixed; synthetic tests pass.
5. **2026-07-11**: DSA + DataTrace pushed to GitHub with READMEs. DSA: 15 DSP + 3D + pitch.

## CONTINUATION PROMPTS
> Agent fills these at end of session. Used to resume next time.

100 Orange Juice RE — next targets:
1. **data.ojd full decrypt**: RE `logiovfs` VFS `xRead` (registered under name "logiovfs"; sqlitevfs::SQLiteVfsImpl<LogIOFileShim>) to extract keystream/key/algorithm, then decrypt the full 1,339,392-B ciphertext offline (saved at dsa/100OJ/extracted/data_ojd_full_ciphertext.bin). Alternative: hook `xRead` at runtime and dump all 327 pages; needs the game to read every page (display/Xvfb).
2. **.fld parser**: confirm cell/connection struct layout across all 80 fields.
3. **Lua C bindings** (LUNA/raylib + Lua 5.4.6): identify tolua++ vs custom; recover binding signatures.
4. Wire DataTrace eBPF backend as alternative to LD_PRELOAD.

---
description: Query memory system. Search blocks, show stats, check chain.
agent: sint-scribe
---

Query the memory system with the provided arguments.

$ARGUMENTS

## Query Types

Based on arguments, perform one of:

### Search
If arguments contain keywords: search blocks matching those keywords
```
Use `memory_search` with the query terms
Present matching blocks
```

### Stats
If arguments = "stats" or "status": show memory statistics
```
Use `memory_stats` 
Present: total blocks, chain length, sessions, blocks by register
```

### Recent
If arguments = "recent" or "last": show recent activity
```
Use `memory_get_chain_tail` with n=10
Present last 10 chain entries
```

### Block lookup
If arguments contain a 4-digit number: read that specific block
```
Use `memory_read_block` with the ID
Present block contents
```

### Chain check
If arguments = "verify" or "chain": verify hash chain integrity
```
Use `memory_verify_chain`
Present results
```

### Default
If no specific arguments: show full memory status
```
Use `memory_stats` + `memory_read_state` + `memory_get_chain_tail` with n=5
Present comprehensive overview
```

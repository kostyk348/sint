/**
 * sint-hooks — OpenCode plugin for SINT-UA v2.1 agent system.
 * 
 * Hooks:
 * - tool.execute.after: Auto-log significant tool results as SENSE blocks
 * - experimental.chat.system.transform: Inject memory context into system prompt
 * - experimental.session.compacting: Preserve memory summary across compaction
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFileSync, appendFileSync, existsSync, mkdirSync } from "fs"
import { join } from "path"
import { createHash } from "crypto"

const MEMORY_DIR = join(process.env.HOME || "/home/lain", ".opencode", "memory")
const BLOCKS_DIR = join(MEMORY_DIR, "blocks")
const CHAIN_FILE = join(MEMORY_DIR, "chain.jsonl")
const STATE_FILE = join(MEMORY_DIR, "state.json")
const SESSIONS_DIR = join(MEMORY_DIR, "sessions")

function computeHash(blockId: string, register: string, content: string, prevHash: string): string {
  const payload = `${blockId}:${register}:${content}:${prevHash}`
  return createHash("sha256").update(payload).digest("hex").slice(0, 16)
}

function getLastChainEntry(): { id: string; hash: string } | null {
  if (!existsSync(CHAIN_FILE)) return null
  const content = readFileSync(CHAIN_FILE, "utf-8")
  const lines = content.trim().split("\n").filter(l => l.trim())
  if (lines.length === 0) return null
  try {
    return JSON.parse(lines[lines.length - 1])
  } catch {
    return null
  }
}

function writeBlock(register: string, content: string, project: string = "SYSTEM"): string {
  const last = getLastChainEntry()
  const prevHash = last?.hash || "0".repeat(16)
  const nextId = last ? String(parseInt(last.id) + 1).padStart(4, "0") : "0000"
  
  const block = {
    id: nextId,
    register,
    prev_hash: prevHash,
    hash: "",
    timestamp: new Date().toISOString(),
    project,
    content,
    source: "sint-hooks-plugin",
    confidence: 0.9,
    tags: ["auto-logged"],
    links: []
  }
  
  block.hash = computeHash(block.id, block.register, block.content, block.prev_hash)
  
  // Ensure directories exist
  if (!existsSync(BLOCKS_DIR)) mkdirSync(BLOCKS_DIR, { recursive: true })
  if (!existsSync(SESSIONS_DIR)) mkdirSync(SESSIONS_DIR, { recursive: true })
  
  // Write block file
  const blockFile = join(BLOCKS_DIR, `${block.id}.${register.toLowerCase()}.json`)
  const { writeFileSync } = require("fs")
  writeFileSync(blockFile, JSON.stringify(block, null, 2))
  
  // Append to chain
  appendFileSync(CHAIN_FILE, JSON.stringify(block) + "\n")
  
  return block.id
}

function logSessionEvent(event: string, details?: Record<string, any>) {
  if (!existsSync(SESSIONS_DIR)) mkdirSync(SESSIONS_DIR, { recursive: true })
  
  const today = new Date().toISOString().split("T")[0]
  const sessionFile = join(SESSIONS_DIR, `${today}.jsonl`)
  
  const entry: Record<string, any> = {
    time: new Date().toISOString().split("T")[1].slice(0, 5),
    event
  }
  if (details) Object.assign(entry, details)
  
  appendFileSync(sessionFile, JSON.stringify(entry) + "\n")
}

function getState(): Record<string, any> | null {
  if (!existsSync(STATE_FILE)) return null
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf-8"))
  } catch {
    return null
  }
}

// Tool results that are significant enough to auto-log
const SIGNIFICANT_TOOLS = new Set([
  "bash", "edit", "write", "task"
])

// Patterns that indicate a finding worth recording
const FINDING_PATTERNS = [
  /verified/i,
  /confirmed/i,
  /bug fixed/i,
  /working/i,
  /success/i,
  /result[s]?\s*[:=]/i,
]

export default (async ({ client, project, directory, $ }) => {
  let sessionStartTime = Date.now()
  let messageCount = 0
  
  return {
    // Log session start
    "chat.message": async (input) => {
      messageCount++
      
      // First message = session start
      if (messageCount === 1) {
        logSessionEvent("session_start", {
          agent: "sint-main",
          project: project?.name || "unknown"
        })
      }
    },
    
    // Auto-log significant tool results
    "tool.execute.after": async (input, output) => {
      const toolName = input.tool
      const result = typeof output === "string" ? output : JSON.stringify(output)
      
      // Only log significant tools
      if (!SIGNIFICANT_TOOLS.has(toolName)) return
      
      // Check if result contains findings
      const isFinding = FINDING_PATTERNS.some(p => p.test(result))
      if (!isFinding) return
      
      // Log as SENSE block
      const content = `[${toolName}] ${result.slice(0, 500)}`
      const blockId = writeBlock("SENSE", content, project?.name || "UNKNOWN")
      
      logSessionEvent("auto_log", {
        tool: toolName,
        block_id: blockId,
        finding: true
      })
    },
    
    // Inject memory context into system prompt
    "experimental.chat.system.transform": async (input) => {
      const state = getState()
      if (!state) return input
      
      const memoryContext = `
## MEMORY CONTEXT (auto-injected by sint-hooks)
Current focus: ${JSON.stringify(state.focus || [])}
Pending decisions: ${JSON.stringify(state.pending_decisions || [])}
Last session: ${state.last_session || "unknown"}
Session count: ${state.session_count || 0}
      
Read .opencode/memory/state.json for full state.
Use memory_* tools from sint-memory MCP server for memory operations.
`
      return input + memoryContext
    },
    
    // Preserve memory summary across compaction
    "experimental.session.compacting": async (input) => {
      // Before compaction, write a summary block
      const state = getState()
      if (state) {
        writeBlock("SENSE", 
          `Session compacted. Focus: ${JSON.stringify(state.focus)}. Messages before compaction: ${messageCount}`,
          state.focus?.[0]?.project || "SYSTEM"
        )
      }
      return input
    },
    
    // Log config on init
    "config": async (cfg) => {
      // Ensure memory directory structure
      if (!existsSync(MEMORY_DIR)) mkdirSync(MEMORY_DIR, { recursive: true })
      if (!existsSync(BLOCKS_DIR)) mkdirSync(BLOCKS_DIR, { recursive: true })
      if (!existsSync(SESSIONS_DIR)) mkdirSync(SESSIONS_DIR, { recursive: true })
      
      return cfg
    }
  }
}) satisfies Plugin

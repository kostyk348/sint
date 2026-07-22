"""sint-portfolio-mcp server (fastmcp, stdio).

Project portfolio manager with cross-project knowledge links.

The agent tracks all projects, their tech stacks, and
what knowledge transfers where. "What applies to what."

Tools:
  add_project(name, tech, status)     — register a project
  list_projects(status, tech)         — list projects
  update_project(name, tech, status)  — update fields
  add_link(source, target, relation)  — knowledge link
  find_transfer(project)              — what knowledge applies elsewhere
  add_note(project, note)             — project note
  get_portfolio_summary()             — full overview

Run: python server.py (stdio)
"""
from __future__ import annotations

import json

from fastmcp import FastMCP

from config import NAME
from state import (
    add_project, get_project, list_projects, update_project,
    add_link, get_links, get_related_projects, find_knowledge_transfer,
    add_note, get_notes, get_portfolio_summary,
)

mcp = FastMCP(NAME)


# ═══════════════════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_project_tool(name: str, description: str = "",
                     tech: list = None, repo: str = "",
                     status: str = "planning",
                     priority: str = "medium") -> str:
    """Add or update a project in the portfolio.

    Args:
        name: project name (unique identifier)
        description: what it does
        tech: list of technologies/languages used
        repo: GitHub repo URL or name
        status: planning|research|active|paused|done|archived
        priority: low|medium|high|critical
    """
    result = add_project(name=name, description=description,
                        tech=tech or [], repo=repo,
                        status=status, priority=priority)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def list_projects_tool(status: str = "", tech: str = "") -> str:
    """List projects, optionally filtered by status or tech."""
    result = list_projects(status=status, tech=tech)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def update_project_tool(name: str, status: str = "", priority: str = "",
                        add_tech: str = "", add_tag: str = "") -> str:
    """Update project fields."""
    result = update_project(name=name, status=status, priority=priority,
                           add_tech=add_tech, add_tag=add_tag)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_project_tool(name: str) -> str:
    """Get full details for a single project."""
    result = get_project(name=name)
    if result is None:
        return json.dumps({"error": f"project '{name}' not found"})
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# CROSS-LINKS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_link_tool(source: str, target: str, relation: str,
                  description: str = "") -> str:
    """Add a knowledge link between projects.

    Args:
        source: project that references
        target: project being referenced
        relation: uses|inspired_by|shares_pattern|conflicts|dependency|similar
        description: why the link exists
    """
    result = add_link(source_project=source, target_project=target,
                     relation=relation, description=description)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_links_tool(project: str = "", relation: str = "") -> str:
    """Get knowledge links, optionally filtered."""
    result = get_links(project=project, relation=relation)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_related_projects_tool(project: str) -> str:
    """Get all projects related to the given one."""
    result = get_related_projects(project=project)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def find_transfer_tool(project: str) -> str:
    """What knowledge from this project could apply elsewhere?

    Analyzes tech overlap and links to suggest knowledge transfers.
    """
    result = find_knowledge_transfer(from_project=project)
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# NOTES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_note_tool(project: str, note: str, tags: list = None) -> str:
    """Add a note to a project."""
    result = add_note(project=project, note=note, tags=tags or [])
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_notes_tool(project: str = "", tag: str = "", limit: int = 10) -> str:
    """Get notes, optionally filtered."""
    result = get_notes(project=project, tag=tag, limit=limit)
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_portfolio_summary_tool() -> str:
    """Full portfolio overview.

    Shows: project counts by status/priority,
    tech stack coverage, most connected projects,
    active work.
    """
    result = get_portfolio_summary()
    return json.dumps(result, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")

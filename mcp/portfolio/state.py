"""Project portfolio: track all projects, cross-links, shared knowledge.

Every project is a node. Knowledge links connect them.
Agent knows what you're working on and what transfers where.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import PROJECTS_FILE, LINKS_FILE, NOTES_FILE


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _today() -> str:
    return time.strftime("%Y-%m-%d")


def _load(path: Path, default=None) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return default if default is not None else {}


def _save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════════════════

def add_project(name: str, description: str = "",
                tech: List[str] = None, repo: str = "",
                status: str = "planning",
                priority: str = "medium") -> dict:
    """Add or update a project."""
    data = _load(PROJECTS_FILE, {"projects": []})

    # Check if exists
    for p in data["projects"]:
        if p["name"] == name:
            if description: p["description"] = description
            if tech: p["tech"] = tech
            if repo: p["repo"] = repo
            if status: p["status"] = status
            if priority: p["priority"] = priority
            p["updated"] = _now()
            _save(PROJECTS_FILE, data)
            return p

    # New project
    project = {
        "name": name,
        "description": description,
        "tech": tech or [],
        "repo": repo,
        "status": status,  # planning|research|active|paused|done|archived
        "priority": priority,  # low|medium|high|critical
        "created": _now(),
        "updated": _now(),
        "tags": [],
    }

    data["projects"].append(project)
    _save(PROJECTS_FILE, data)
    return project


def get_project(name: str) -> Optional[dict]:
    """Get a project by name."""
    data = _load(PROJECTS_FILE, {"projects": []})
    for p in data["projects"]:
        if p["name"] == name:
            return p
    return None


def list_projects(status: str = "", tech: str = "") -> dict:
    """List all projects, optionally filtered."""
    data = _load(PROJECTS_FILE, {"projects": []})
    projects = data.get("projects", [])

    if status:
        projects = [p for p in projects if p.get("status") == status]
    if tech:
        projects = [p for p in projects if tech.lower() in [t.lower() for t in p.get("tech", [])]]

    return {
        "total": len(projects),
        "projects": projects,
    }


def update_project(name: str, status: str = "", priority: str = "",
                   add_tech: str = "", add_tag: str = "") -> dict:
    """Update project fields."""
    data = _load(PROJECTS_FILE, {"projects": []})
    for p in data["projects"]:
        if p["name"] == name:
            if status: p["status"] = status
            if priority: p["priority"] = priority
            if add_tech and add_tech not in p.get("tech", []):
                p.setdefault("tech", []).append(add_tech)
            if add_tag and add_tag not in p.get("tags", []):
                p.setdefault("tags", []).append(add_tag)
            p["updated"] = _now()
            _save(PROJECTS_FILE, data)
            return p
    return {"error": f"project '{name}' not found"}


# ═══════════════════════════════════════════════════════════════════
# CROSS-LINKS
# ═══════════════════════════════════════════════════════════════════

def add_link(source_project: str, target_project: str,
             relation: str, description: str = "") -> dict:
    """Add a knowledge link between projects.

    relation types:
    - "uses" — project A uses project B
    - "inspired_by" — A was inspired by B
    - "shares_pattern" — A and B share a common pattern
    - "conflicts" — A and B have conflicting approaches
    - "dependency" — A depends on B
    - "similar" — A and B are structurally similar
    """
    data = _load(LINKS_FILE, {"links": []})

    link = {
        "source": source_project,
        "target": target_project,
        "relation": relation,
        "description": description,
        "created": _now(),
    }

    # Dedup
    for existing in data["links"]:
        if (existing["source"] == source_project
                and existing["target"] == target_project
                and existing["relation"] == relation):
            existing["description"] = description or existing["description"]
            existing["updated"] = _now()
            _save(LINKS_FILE, data)
            return existing

    data["links"].append(link)
    _save(LINKS_FILE, data)
    return link


def get_links(project: str = "", relation: str = "") -> dict:
    """Get all links, optionally filtered."""
    data = _load(LINKS_FILE, {"links": []})
    links = data.get("links", [])

    if project:
        links = [l for l in links if l["source"] == project or l["target"] == project]
    if relation:
        links = [l for l in links if l["relation"] == relation]

    return {"total": len(links), "links": links}


def get_related_projects(project: str) -> dict:
    """Get all projects related to the given one (both directions)."""
    data = _load(LINKS_FILE, {"links": []})
    related = []
    for l in data.get("links", []):
        if l["source"] == project:
            related.append({"project": l["target"], "relation": l["relation"],
                           "direction": "uses/references"})
        elif l["target"] == project:
            related.append({"project": l["source"], "relation": l["relation"],
                           "direction": "referenced_by"})

    return {"project": project, "related": related, "total": len(related)}


def find_knowledge_transfer(from_project: str) -> dict:
    """What knowledge from this project could apply elsewhere?

    Analyzes tech stack and links to suggest transfers.
    """
    proj = get_project(from_project)
    if not proj:
        return {"error": f"project '{from_project}' not found"}

    tech = proj.get("tech", [])
    links_data = _load(LINKS_FILE, {"links": []})

    # Find projects with overlapping tech
    all_projects = _load(PROJECTS_FILE, {"projects": []}).get("projects", [])
    transfers = []

    for other in all_projects:
        if other["name"] == from_project:
            continue

        overlap = set(t.lower() for t in tech) & set(t.lower() for t in other.get("tech", []))
        if overlap:
            transfers.append({
                "to_project": other["name"],
                "shared_tech": list(overlap),
                "their_status": other.get("status", ""),
                "suggestion": f"Knowledge about {', '.join(overlap)} may transfer to {other['name']}",
            })

    return {"from": from_project, "transfers": transfers, "total": len(transfers)}


# ═══════════════════════════════════════════════════════════════════
# PROJECT NOTES
# ═══════════════════════════════════════════════════════════════════

def add_note(project: str, note: str, tags: List[str] = None) -> dict:
    """Add a note to a project."""
    data = _load(NOTES_FILE, {"notes": []})

    n = {
        "id": f"N{len(data['notes']) + 1:04d}",
        "project": project,
        "note": note,
        "tags": tags or [],
        "date": _today(),
        "timestamp": _now(),
    }

    data["notes"].append(n)
    _save(NOTES_FILE, data)
    return n


def get_notes(project: str = "", tag: str = "", limit: int = 10) -> dict:
    """Get notes, optionally filtered."""
    data = _load(NOTES_FILE, {"notes": []})
    notes = data.get("notes", [])

    if project:
        notes = [n for n in notes if n["project"] == project]
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]

    notes.sort(key=lambda n: n.get("timestamp", ""), reverse=True)
    return {"total": len(notes), "notes": notes[:limit]}


# ═══════════════════════════════════════════════════════════════════
# PORTFOLIO SUMMARY
# ═══════════════════════════════════════════════════════════════════

def get_portfolio_summary() -> dict:
    """Full portfolio overview."""
    projects = _load(PROJECTS_FILE, {"projects": []}).get("projects", [])
    links = _load(LINKS_FILE, {"links": []}).get("links", [])

    by_status = {}
    for p in projects:
        s = p.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1

    by_priority = {}
    for p in projects:
        pr = p.get("priority", "medium")
        by_priority[pr] = by_priority.get(pr, 0) + 1

    # Most connected projects
    connection_count = {}
    for l in links:
        connection_count[l["source"]] = connection_count.get(l["source"], 0) + 1
        connection_count[l["target"]] = connection_count.get(l["target"], 0) + 1

    most_connected = sorted(connection_count.items(), key=lambda x: x[1], reverse=True)[:5]

    # All unique tech
    all_tech = set()
    for p in projects:
        all_tech.update(p.get("tech", []))

    return {
        "total_projects": len(projects),
        "total_links": len(links),
        "by_status": by_status,
        "by_priority": by_priority,
        "all_tech": sorted(all_tech),
        "most_connected": [{"project": n, "connections": c} for n, c in most_connected],
        "active_projects": [
            p["name"] for p in projects if p.get("status") in ("active", "research")
        ],
    }

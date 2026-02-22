#!/usr/bin/env python3
"""
ClubDesk — Workflow Builder

Injects the current system prompts + knowledge base into the n8n workflow
JSON templates, producing ready-to-import files in n8n-workflows/dist/.

Run this before every n8n import, or whenever prompts or the knowledge
base change.

Usage:
    python scripts/build-workflows.py

Output:
    n8n-workflows/dist/email-responder.json
    n8n-workflows/dist/messenger-responder.json
"""

import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS_DIR = os.path.join(BASE, "n8n-workflows")
DIST_DIR = os.path.join(WORKFLOWS_DIR, "dist")
PROMPTS_DIR = os.path.join(BASE, "prompts")
KB_FILE = os.path.join(BASE, "knowledge-base", "club-knowledge.md")

BUILDS = [
    ("email-responder.json",    "email-system.md"),
    ("messenger-responder.json", "chat-system.md"),
]


def load_combined_prompt(prompt_filename: str) -> str:
    """Load a system prompt file and append the full knowledge base."""
    prompt_path = os.path.join(PROMPTS_DIR, prompt_filename)
    with open(prompt_path, encoding="utf-8") as f:
        raw = f.read()

    # Strip the file header (title + "Used in..." line + first --- divider)
    prompt = re.sub(r"^.*?---\n", "", raw, count=1, flags=re.DOTALL).strip()

    with open(KB_FILE, encoding="utf-8") as f:
        kb = f.read().strip()

    return prompt + "\n\n---\n\n## Knowledge Base\n\n" + kb


def build(workflow_filename: str, prompt_filename: str) -> None:
    src = os.path.join(WORKFLOWS_DIR, workflow_filename)
    dst = os.path.join(DIST_DIR, workflow_filename)

    with open(src, encoding="utf-8") as f:
        raw = f.read()

    if "SYSTEM_PROMPT_PLACEHOLDER" not in raw:
        print(f"  WARNING: no SYSTEM_PROMPT_PLACEHOLDER found in {workflow_filename} — skipping injection")
    else:
        prompt_content = load_combined_prompt(prompt_filename)

        # json.dumps gives us a properly escaped JSON string (with surrounding quotes).
        # We strip the quotes and use the inner content as the replacement — this
        # is safe to drop directly into the raw JSON file where the placeholder sits
        # inside a JSON string value.
        escaped = json.dumps(prompt_content)[1:-1]

        raw = raw.replace("SYSTEM_PROMPT_PLACEHOLDER", escaped)

    # Validate the result is valid JSON before writing
    try:
        json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  ERROR: resulting JSON is invalid for {workflow_filename}: {e}")
        sys.exit(1)

    os.makedirs(DIST_DIR, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(raw)

    prompt_tokens = len(load_combined_prompt(prompt_filename).split()) * 1.3  # rough estimate
    print(f"  ✓  {workflow_filename}  →  dist/{workflow_filename}  (~{int(prompt_tokens)} prompt tokens, cached)")


def main() -> None:
    print("\nClubDesk Workflow Builder")
    print("=" * 40)

    for workflow_file, prompt_file in BUILDS:
        build(workflow_file, prompt_file)

    print()
    print("Done. Import the files from n8n-workflows/dist/ into n8n.")
    print("If prompts or knowledge base change, re-run this script and re-import.\n")


if __name__ == "__main__":
    main()

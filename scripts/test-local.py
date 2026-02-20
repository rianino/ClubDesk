#!/usr/bin/env python3
"""
ClubDesk local interactive test runner.

Usage:
    python scripts/test-local.py          # defaults to email channel
    python scripts/test-local.py email
    python scripts/test-local.py chat

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Type messages as if you were an inbound contact. Ctrl+C to quit.
"""

import sys
import os
import re
import anthropic

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_system_prompt(channel: str) -> str:
    prompt_file = "email-system.md" if channel == "email" else "chat-system.md"

    with open(os.path.join(BASE, "prompts", prompt_file)) as f:
        raw = f.read()
    # Strip the file header (title line, "Used in..." line, and the --- divider)
    prompt = re.sub(r"^.*?---\n", "", raw, count=1, flags=re.DOTALL).strip()

    with open(os.path.join(BASE, "knowledge-base", "club-knowledge.md")) as f:
        kb = f.read().strip()

    return prompt + "\n\n---\n\n## Knowledge Base\n\n" + kb


def parse_response(text: str) -> tuple[str, str]:
    reply_match = re.search(r"---REPLY---\n(.*?)(?=---META---|$)", text, re.DOTALL)
    meta_match  = re.search(r"---META---\n(.*?)$", text, re.DOTALL)

    reply = reply_match.group(1).strip() if reply_match else text.strip()
    meta  = meta_match.group(1).strip()  if meta_match  else "(no META block found)"
    return reply, meta


def main():
    channel = sys.argv[1] if len(sys.argv) > 1 else "email"
    if channel not in ("email", "chat"):
        print("Usage: python test-local.py [email|chat]")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nError: ANTHROPIC_API_KEY environment variable not set.")
        print("Run: export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    system_prompt = load_system_prompt(channel)
    client = anthropic.Anthropic(api_key=api_key)

    channel_label = "EMAIL" if channel == "email" else "CHAT (Messenger/Instagram)"
    print(f"\n{'='*60}")
    print(f"  ClubDesk Local Test — {channel_label}")
    print(f"  Model: claude-haiku-4-5-20251001")
    print(f"  Type a message as an inbound contact. Ctrl+C to quit.")
    print(f"{'='*60}\n")

    while True:
        try:
            user_input = input("Incoming message: ").strip()
            if not user_input:
                continue

            print("Thinking...", end="\r")

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                system=system_prompt,
                messages=[{"role": "user", "content": user_input}],
            )

            raw = response.content[0].text
            reply, meta = parse_response(raw)

            print(f"\n{'─'*60}")
            print(f"REPLY:\n\n{reply}")
            print(f"\nACTION: {meta}")
            print(f"{'─'*60}\n")

        except KeyboardInterrupt:
            print("\n\nDone.")
            break


if __name__ == "__main__":
    main()

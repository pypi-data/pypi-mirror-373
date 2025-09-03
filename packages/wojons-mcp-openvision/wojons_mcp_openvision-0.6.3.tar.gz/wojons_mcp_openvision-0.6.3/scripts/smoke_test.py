#!/usr/bin/env python3
"""
Smoke test for mcp-openvision vision pipeline.

- Runs two tests with a real vision model endpoint:
  1) Local repository image: sample_image.jpg
  2) Public image URL

- Forces the model via function param to avoid env pitfalls.
- Writes detailed output to smoke_test_output.txt for inspection.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Ensure local import works when run via `PYTHONPATH=src`
try:
    from mcp_openvision.server import image_analysis
except Exception as e:
    print(f"[SMOKE] Failed to import mcp_openvision.server: {e}", file=sys.stderr)
    sys.exit(1)

OUTPUT_FILE = "smoke_test_output.txt"

DEFAULT_MODEL = os.environ.get(
    "SMOKE_TEST_MODEL",
    "qwen/qwen2.5-vl-32b-instruct:free",  # known vision-capable endpoint on OpenRouter
)

TESTS = [
    {
        "name": "local_file_sample_image",
        "image": "sample_image.png",
        "project_root": ".",
        "query": "Quick vision smoke test: list the main objects visible.",
        "model": DEFAULT_MODEL,
    },
    {
        "name": "public_url_png_demo",
        "image": "https://picsum.photos/seed/visiondemo/256/256",
        "project_root": None,
        "query": "Describe the contents and any visible text/logo.",
        "model": DEFAULT_MODEL,
    },
]


async def run_one(test):
    try:
        result = await image_analysis(
            image=test["image"],
            project_root=test["project_root"],
            query=test["query"],
            model=test["model"],
        )
        return {"name": test["name"], "ok": True, "response": result}
    except Exception as e:
        return {
            "name": test["name"],
            "ok": False,
            "error": str(e),
        }


async def main():
    # Basic pre-check
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("[SMOKE] OPENROUTER_API_KEY is not set in the environment.", file=sys.stderr)
        sys.exit(2)

    results = []
    for t in TESTS:
        res = await run_one(t)
        results.append(res)

    summary = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "model": DEFAULT_MODEL,
        "results": results,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SMOKE] Failed to write {OUTPUT_FILE}: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())

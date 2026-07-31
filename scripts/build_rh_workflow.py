from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def _scrub_upload_session_state(node: dict[str, Any]) -> None:
    """Remove machine/user-specific media state without changing workflow behavior."""
    if node["type"] == "MultiImageLoader":
        node["widgets_values"][0] = ""
    elif node["type"] == "VHS_LoadVideo":
        widgets = node["widgets_values"]
        widgets["video"] = ""
        widgets.pop("videopreview", None)
    elif node["type"] == "VHS_VideoCombine":
        node["widgets_values"].pop("videopreview", None)


def _rh_compatibility_snapshot(workflow: dict[str, Any]) -> dict[str, Any]:
    """Normalize only machine/user-specific media state.

    Workflow frontend and core-node version fields are deliberately preserved from
    V4.3. They describe the serializer that produced the RH-compatible JSON, not the
    separately tested ComfyUI runtime.
    """
    normalized = copy.deepcopy(workflow)

    for node in normalized["nodes"]:
        if node["type"] == "MultiImageLoader":
            node["widgets_values"][0] = "<UPLOAD>"
        elif node["type"] == "VHS_LoadVideo":
            node["widgets_values"]["video"] = "<UPLOAD>"
            node["widgets_values"].pop("videopreview", None)
        elif node["type"] == "VHS_VideoCombine":
            node["widgets_values"].pop("videopreview", None)

    return normalized


def build_workflow(source: dict[str, Any]) -> dict[str, Any]:
    workflow = copy.deepcopy(source)

    for node in workflow["nodes"]:
        _scrub_upload_session_state(node)

    if _rh_compatibility_snapshot(workflow) != _rh_compatibility_snapshot(source):
        raise AssertionError("V5 build changed the V4.3 RH-compatible workflow")
    return workflow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8-sig"))
    workflow = build_workflow(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(workflow, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()

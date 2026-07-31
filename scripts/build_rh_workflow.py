from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


CORE_VERSION = "0.29.2"
FRONTEND_VERSION = "1.47.11"


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


def _functional_snapshot(workflow: dict[str, Any]) -> dict[str, Any]:
    """Normalize the only fields V5 is allowed to change from the V4.3 baseline."""
    normalized = copy.deepcopy(workflow)
    normalized.get("extra", {}).pop("frontendVersion", None)
    normalized.get("extra", {}).pop("scail2_v5", None)

    for node in normalized["nodes"]:
        if node.get("properties", {}).get("cnr_id") == "comfy-core":
            node["properties"]["ver"] = "<CORE_VERSION>"
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
        if node.get("properties", {}).get("cnr_id") == "comfy-core":
            node["properties"]["ver"] = CORE_VERSION
        _scrub_upload_session_state(node)

    workflow.setdefault("extra", {})
    workflow["extra"]["frontendVersion"] = FRONTEND_VERSION
    workflow["extra"]["scail2_v5"] = {
        "workflow_version": "5.0.1",
        "tested_core": CORE_VERSION,
        "base": "V4.3 RH exact functional clone",
    }

    if _functional_snapshot(workflow) != _functional_snapshot(source):
        raise AssertionError("V5 build changed the V4.3 workflow graph or behavior")
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

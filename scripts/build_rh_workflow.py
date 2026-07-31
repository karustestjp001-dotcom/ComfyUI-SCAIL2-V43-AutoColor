from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


CORE_VERSION = "0.29.0"
FRONTEND_VERSION = "1.47.10"
V43_REPOSITORY_ID = "karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor"
V43_REGISTRY_ID = "comfyui-scail2-v43-autocolor"
V43_PACKAGE_VERSION = "2.0.0"
UPSTREAM_SCAIL_COMMIT = "aac331566ea0fa23af89b63bfc83e533577b05e6"
GIMM_COMMIT = "4c9a3123762af85e7c796e41737da0b70c75d72d"
VHS_COMMIT = "4ee72c065db22c9d96c2427954dc69e7b908444b"
GIMM_NODE_TYPES = {"DownloadAndLoadGIMMVFIModel", "GIMMVFI_interpolate"}
VHS_NODE_TYPES = {"VHS_LoadVideo", "VHS_VideoInfo", "VHS_VideoCombine"}

REMOVE_NODE_TYPES = {
    "SetNode",
    "GetNode",
    "Label (rgthree)",
    "Fast Groups Bypasser (rgthree)",
    "FilmGrain",
}


def _core_properties(node_name: str, *, models: list[dict[str, str]] | None = None):
    properties: dict[str, Any] = {
        "Node name for S&R": node_name,
        "cnr_id": "comfy-core",
        "ver": CORE_VERSION,
    }
    if models:
        properties["models"] = models
    return properties


def _model(name: str, url: str, directory: str) -> dict[str, str]:
    return {"name": name, "url": url, "directory": directory}


def _transform_unet_loader(node: dict[str, Any]) -> None:
    name = "wan2.1_14B_SCAIL_2_fp8_scaled.safetensors"
    node.update(
        {
            "type": "UNETLoader",
            "size": [420, 82],
            "inputs": [
                {
                    "name": "unet_name",
                    "type": "COMBO",
                    "widget": {"name": "unet_name"},
                    "link": None,
                },
                {
                    "name": "weight_dtype",
                    "type": "COMBO",
                    "widget": {"name": "weight_dtype"},
                    "link": None,
                },
            ],
            "outputs": [{"name": "MODEL", "type": "MODEL", "links": []}],
            "properties": _core_properties(
                "UNETLoader",
                models=[
                    _model(
                        name,
                        "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/"
                        f"diffusion_models/{name}",
                        "diffusion_models",
                    )
                ],
            ),
            "widgets_values": [name, "default"],
        }
    )


def _transform_image_scale(node: dict[str, Any]) -> None:
    node.update(
        {
            "type": "ImageScale",
            "size": [320, 174],
            "inputs": [
                {"name": "image", "type": "IMAGE", "link": None},
                {
                    "name": "upscale_method",
                    "type": "COMBO",
                    "widget": {"name": "upscale_method"},
                    "link": None,
                },
                {
                    "name": "width",
                    "type": "INT",
                    "widget": {"name": "width"},
                    "link": None,
                },
                {
                    "name": "height",
                    "type": "INT",
                    "widget": {"name": "height"},
                    "link": None,
                },
                {
                    "name": "crop",
                    "type": "COMBO",
                    "widget": {"name": "crop"},
                    "link": None,
                },
            ],
            "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": []}],
            "properties": _core_properties("ImageScale"),
            "widgets_values": ["lanczos", 720, 1280, "center"],
        }
    )


def _transform_reference_loader(node: dict[str, Any]) -> None:
    node.update(
        {
            "type": "LoadImage",
            "size": [330, 315],
            "inputs": [
                {
                    "name": "image",
                    "type": "COMBO",
                    "widget": {"name": "image"},
                    "link": None,
                },
                {
                    "name": "upload",
                    "type": "IMAGEUPLOAD",
                    "widget": {"name": "upload"},
                    "link": None,
                },
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": []},
                {"name": "MASK", "type": "MASK", "links": None},
            ],
            "properties": _core_properties("LoadImage"),
            "widgets_values": ["RH_請上傳參考圖.png", "image"],
        }
    )


def _refresh_core_model_loaders(by_id: dict[int, dict[str, Any]]) -> None:
    model_specs = {
        5: (
            "VAELoader",
            "wan_2.1_vae.safetensors",
            "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/"
            "resolve/main/split_files/vae/wan_2.1_vae.safetensors",
            "vae",
        ),
        6: (
            "CLIPVisionLoader",
            "clip_vision_h.safetensors",
            "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/"
            "resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
            "clip_vision",
        ),
        14: (
            "CLIPLoader",
            "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
            "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/"
            "resolve/main/split_files/text_encoders/"
            "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
            "text_encoders",
        ),
        24: (
            "CheckpointLoaderSimple",
            "sam3.1_multiplex_fp16.safetensors",
            "https://huggingface.co/Comfy-Org/sam3.1/resolve/main/checkpoints/"
            "sam3.1_multiplex_fp16.safetensors",
            "checkpoints",
        ),
    }
    for node_id, (node_name, model_name, url, directory) in model_specs.items():
        by_id[node_id]["properties"] = _core_properties(
            node_name,
            models=[_model(model_name, url, directory)],
        )


def _replace_links(workflow: dict[str, Any]) -> None:
    existing_ids = {int(node["id"]) for node in workflow["nodes"]}
    drop_link_ids = {
        6,
        48,
        70,
        71,
        72,
        73,
        74,
        141,
        142,
        143,
        147,
        153,
        163,
        164,
        177,
    }
    replacement_links = {
        48: [48, 8, 0, 9, 0, "IMAGE"],
        70: [70, 1, 0, 2, 0, "MODEL"],
        71: [71, 14, 0, 65, 1, "CLIP"],
        72: [72, 5, 0, 65, 2, "VAE"],
        73: [73, 6, 0, 65, 5, "CLIP_VISION"],
        153: [153, 24, 0, 65, 7, "MODEL"],
        177: [177, 74, 0, 65, 9, "IMAGE"],
    }

    links = []
    for link in workflow["links"]:
        link_id, source_id, _, target_id, _, _ = link
        if int(source_id) not in existing_ids or int(target_id) not in existing_ids:
            continue
        if int(link_id) in drop_link_ids:
            continue
        links.append(link)
    links.extend(replacement_links.values())
    workflow["links"] = sorted(links, key=lambda link: int(link[0]))


def _rebuild_node_link_state(workflow: dict[str, Any]) -> None:
    nodes = {int(node["id"]): node for node in workflow["nodes"]}
    for node in nodes.values():
        for input_spec in node.get("inputs") or []:
            input_spec["link"] = None
        for output_spec in node.get("outputs") or []:
            output_spec["links"] = []

    for link_id, source_id, source_slot, target_id, target_slot, _ in workflow["links"]:
        source = nodes[int(source_id)]
        target = nodes[int(target_id)]
        source["outputs"][int(source_slot)]["links"].append(int(link_id))
        target["inputs"][int(target_slot)]["link"] = int(link_id)

    for node in nodes.values():
        for output_spec in node.get("outputs") or []:
            if not output_spec["links"]:
                output_spec["links"] = None


def _sanitize_widgets(node: dict[str, Any]) -> None:
    if node["type"] == "VHS_LoadVideo":
        widgets = copy.deepcopy(node["widgets_values"])
        widgets["video"] = "RH_請上傳驅動影片.mp4"
        widgets.pop("videopreview", None)
        node["widgets_values"] = widgets
    elif node["type"] == "VHS_VideoCombine":
        widgets = copy.deepcopy(node["widgets_values"])
        widgets.pop("videopreview", None)
        widgets["filename_prefix"] = "SCAIL2_V5_RH"
        node["widgets_values"] = widgets
    elif node["type"] == "LoraLoaderModelOnly":
        node["widgets_values"][0] = (
            "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors"
        )
        node["properties"] = _core_properties(
            "LoraLoaderModelOnly",
            models=[
                _model(
                    "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
                    "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/"
                    "Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
                    "loras",
                )
            ],
        )


def build_workflow(source: dict[str, Any]) -> dict[str, Any]:
    workflow = copy.deepcopy(source)
    by_id = {int(node["id"]): node for node in workflow["nodes"]}

    _transform_unet_loader(by_id[13])
    _transform_image_scale(by_id[17])
    _transform_reference_loader(by_id[74])
    _refresh_core_model_loaders(by_id)

    workflow["nodes"] = [
        node for node in workflow["nodes"] if node["type"] not in REMOVE_NODE_TYPES
    ]
    _replace_links(workflow)

    for node in workflow["nodes"]:
        _sanitize_widgets(node)
        if node["type"] == "SCAIL2SegmentPlanBuilder":
            node["properties"].update(
                {
                    "aux_id": "TTPlanetPig/comfyui_scail2_multi_cond",
                    "cnr_id": "comfyui_scail2_multi_cond",
                    "ver": UPSTREAM_SCAIL_COMMIT,
                }
            )
        elif node["type"] == "SCAIL2ScheduledLongVideoWithSAMV43":
            node["properties"].update(
                {
                    "aux_id": V43_REPOSITORY_ID,
                    "cnr_id": V43_REGISTRY_ID,
                    "ver": V43_PACKAGE_VERSION,
                }
            )
            node["title"] = "SCAIL-2 V5 長影片（V4.3 校色／RH）"
            if not any(
                input_spec["name"] == "cache_mode"
                for input_spec in node.get("inputs") or []
            ):
                node["inputs"].append(
                    {
                        "name": "cache_mode",
                        "type": "COMBO",
                        "widget": {"name": "cache_mode"},
                        "link": None,
                    }
                )
            if "disk" not in node["widgets_values"]:
                insert_at = (
                    len(node["widgets_values"]) - 1
                    if node["widgets_values"] and node["widgets_values"][-1] is None
                    else len(node["widgets_values"])
                )
                node["widgets_values"].insert(insert_at, "disk")
        elif node["type"] in GIMM_NODE_TYPES:
            node["properties"].update(
                {
                    "aux_id": "kijai/ComfyUI-GIMM-VFI",
                    "cnr_id": "ComfyUI-GIMM-VFI",
                    "ver": GIMM_COMMIT,
                }
            )
        elif node["type"] in VHS_NODE_TYPES:
            node["properties"].update(
                {
                    "aux_id": "Kosinkadink/ComfyUI-VideoHelperSuite",
                    "cnr_id": "comfyui-videohelpersuite",
                    "ver": VHS_COMMIT,
                }
            )
        elif node["id"] == 50:
            node["widgets_values"] = [
                "SCAIL-2 V5.0 RH 直用版\n\n"
                "Tested: ComfyUI 0.29.0 / frontend 1.47.10\n"
                "Required Git repositories:\n"
                "https://github.com/karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor\n"
                "https://github.com/TTPlanetPig/comfyui_scail2_multi_cond\n"
                "https://github.com/kijai/ComfyUI-GIMM-VFI\n"
                "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite\n\n"
                "Upload one reference image and one driving video before queueing.\n"
                "Relighting LoRA is for replacement mode and is intentionally not enabled "
                "in this animation workflow."
            ]
        elif node["id"] == 75:
            node["widgets_values"] = [
                "V5.0 keeps V4.3 chunk color correction (v43/original/off) while "
                "removing UI-only and local-only node dependencies for RunningHub. "
                "Default: v43, residual_strength=0.2, max_offset=0.02."
            ]

    workflow.setdefault("extra", {})
    workflow["extra"]["frontendVersion"] = FRONTEND_VERSION
    workflow["extra"]["scail2_v5"] = {
        "workflow_version": "5.0.0",
        "tested_core": CORE_VERSION,
        "purpose": "RunningHub portable long-video animation",
    }
    workflow["last_link_id"] = max(int(link[0]) for link in workflow["links"])
    _rebuild_node_link_state(workflow)
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
        json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output)


if __name__ == "__main__":
    main()

import copy
import hashlib
import json
from pathlib import Path
import tomllib
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = (
    REPO_ROOT
    / "workflows"
    / "ComfyUI SCAIL 2 極簡長視頻生成_V5.0_RH直用版.json"
)
DEPENDENCY_PATH = REPO_ROOT / "rh_dependencies.json"
V43_FUNCTIONAL_DIGEST = (
    "c417d31fb63c7c7ba013addccd56ffc5cc5f78b3fea1752d7df64955795b8864"
)


def _functional_digest(workflow):
    """Ignore only version metadata and upload/preview session state."""
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

    payload = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class RunningHubWorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(WORKFLOW_PATH.is_file(), f"Missing RH workflow: {WORKFLOW_PATH}")
        self.assertTrue(
            DEPENDENCY_PATH.is_file(), f"Missing RH dependency manifest: {DEPENDENCY_PATH}"
        )
        self.workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
        self.dependencies = json.loads(DEPENDENCY_PATH.read_text(encoding="utf-8"))

    def test_v5_is_functionally_identical_to_the_v43_rh_baseline(self):
        self.assertEqual(_functional_digest(self.workflow), V43_FUNCTIONAL_DIGEST)
        self.assertEqual(len(self.workflow["nodes"]), 42)
        self.assertEqual(len(self.workflow["links"]), 32)
        self.assertEqual(len(self.workflow["groups"]), 5)
        self.assertEqual(self.workflow["last_node_id"], 75)
        self.assertEqual(self.workflow["last_link_id"], 177)

    def test_only_core_and_frontend_versions_are_updated(self):
        self.assertEqual(self.dependencies["comfyui"]["version"], "0.29.2")
        self.assertEqual(self.workflow["extra"]["frontendVersion"], "1.47.11")
        core_nodes = [
            node
            for node in self.workflow["nodes"]
            if node.get("properties", {}).get("cnr_id") == "comfy-core"
        ]
        self.assertTrue(core_nodes)
        for node in core_nodes:
            with self.subTest(node=node["id"]):
                self.assertEqual(node["properties"]["ver"], "0.29.2")

    def test_kjnodes_resize_and_all_four_links_are_preserved(self):
        node = next(node for node in self.workflow["nodes"] if int(node["id"]) == 17)
        self.assertEqual(node["type"], "ImageResizeKJv2")
        self.assertEqual(
            [item["name"] for item in node["inputs"]],
            [
                "image",
                "mask",
                "width",
                "height",
                "upscale_method",
                "keep_proportion",
                "pad_color",
                "crop_position",
                "divisible_by",
                "device",
            ],
        )
        self.assertEqual(
            [item["name"] for item in node["outputs"]],
            ["IMAGE", "width", "height", "mask"],
        )
        self.assertEqual(
            node["widgets_values"],
            [720, 1280, "lanczos", "crop", "0, 0, 0", "center", 32, "cpu"],
        )
        touching_links = [
            link for link in self.workflow["links"] if int(link[1]) == 17 or int(link[3]) == 17
        ]
        self.assertEqual(
            touching_links,
            [
                [12, 12, 0, 17, 0, "IMAGE"],
                [146, 17, 0, 65, 6, "IMAGE"],
                [163, 17, 1, 74, 1, "INT"],
                [164, 17, 2, 74, 2, "INT"],
            ],
        )

    def test_original_reference_loader_and_interpolation_switch_are_preserved(self):
        reference = next(node for node in self.workflow["nodes"] if int(node["id"]) == 74)
        self.assertEqual(reference["type"], "MultiImageLoader")
        self.assertEqual(
            [item["name"] for item in reference["outputs"]],
            ["multi_output", "image_1"],
        )
        self.assertIn([177, 74, 1, 65, 9, "IMAGE"], self.workflow["links"])

        bypasser = next(
            node
            for node in self.workflow["nodes"]
            if node["type"] == "Fast Groups Bypasser (rgthree)"
        )
        self.assertEqual(bypasser["properties"]["matchTitle"], "Frame Interpolation 插帧")
        self.assertIn(
            "Frame Interpolation 插帧",
            [group["title"] for group in self.workflow["groups"]],
        )

    def test_all_original_custom_node_families_remain_in_the_graph(self):
        node_types = {node["type"] for node in self.workflow["nodes"]}
        self.assertTrue(
            {
                "DiffusionModelLoaderKJ",
                "ImageResizeKJv2",
                "SetNode",
                "GetNode",
                "Label (rgthree)",
                "FilmGrain",
                "MultiImageLoader",
                "SCAIL2SegmentPlanBuilder",
                "SCAIL2ScheduledLongVideoWithSAMV43",
                "DownloadAndLoadGIMMVFIModel",
                "GIMMVFI_interpolate",
                "VHS_LoadVideo",
                "VHS_VideoInfo",
                "VHS_VideoCombine",
            }.issubset(node_types)
        )

    def test_links_reference_existing_nodes_and_slots(self):
        nodes = {int(node["id"]): node for node in self.workflow["nodes"]}
        for link_id, source_id, source_slot, target_id, target_slot, _ in self.workflow["links"]:
            with self.subTest(link=link_id):
                self.assertIn(int(source_id), nodes)
                self.assertIn(int(target_id), nodes)
                self.assertLess(int(source_slot), len(nodes[int(source_id)]["outputs"]))
                self.assertLess(int(target_slot), len(nodes[int(target_id)]["inputs"]))

    def test_workflow_does_not_leak_local_or_previous_rh_preview_state(self):
        raw = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertNotIn('"fullpath"', raw)
        self.assertNotIn('"cos_url"', raw)
        self.assertNotIn("F:\\\\0_ComfyUI", raw)
        self.assertNotIn("摩多摩多.mp4", raw)
        self.assertNotIn("146981507_p0_master1200.jpg", raw)

    def test_manifest_covers_every_required_custom_node_type(self):
        workflow_types = {node["type"] for node in self.workflow["nodes"]}
        manifest_types = {
            node_type
            for dependency in self.dependencies["custom_nodes"]
            for node_type in dependency["required_nodes"]
        }
        non_core_types = {
            node["type"]
            for node in self.workflow["nodes"]
            if node["type"] not in {"Note"}
            and node.get("properties", {}).get("cnr_id") != "comfy-core"
        }
        self.assertTrue(non_core_types.issubset(manifest_types))
        self.assertTrue(manifest_types.issubset(workflow_types))

    def test_custom_node_package_version_matches_the_manifest(self):
        project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        custom_node = next(
            item
            for item in self.dependencies["custom_nodes"]
            if item["name"] == "SCAIL2 V4.3 Auto Color"
        )
        self.assertEqual(project["project"]["version"], custom_node["version"])
        self.assertEqual(self.dependencies["workflow_version"], "5.0.1")

    def test_every_manifest_model_is_selected_by_the_workflow(self):
        widget_strings = {
            value.replace("\\\\", "/")
            for node in self.workflow["nodes"]
            for value in (
                node.get("widgets_values", [])
                if isinstance(node.get("widgets_values", []), list)
                else node.get("widgets_values", {}).values()
            )
            if isinstance(value, str)
        }
        for model in self.dependencies["models"]:
            with self.subTest(model=model["name"]):
                self.assertTrue(
                    any(value.endswith(model["name"]) for value in widget_strings),
                    f"Model is not selected by any workflow node: {model['name']}",
                )

    def test_sam31_manifest_uses_the_official_checkpoint_path(self):
        sam_model = next(
            model
            for model in self.dependencies["models"]
            if model["name"] == "sam3.1_multiplex_fp16.safetensors"
        )
        self.assertEqual(
            sam_model["url"],
            "https://huggingface.co/Comfy-Org/sam3.1/resolve/main/checkpoints/"
            "sam3.1_multiplex_fp16.safetensors",
        )


if __name__ == "__main__":
    unittest.main()

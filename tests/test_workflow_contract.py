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


class RunningHubWorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(WORKFLOW_PATH.is_file(), f"Missing RH workflow: {WORKFLOW_PATH}")
        self.assertTrue(
            DEPENDENCY_PATH.is_file(), f"Missing RH dependency manifest: {DEPENDENCY_PATH}"
        )
        self.workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
        self.dependencies = json.loads(DEPENDENCY_PATH.read_text(encoding="utf-8"))

    def test_workflow_targets_the_tested_core_and_frontend(self):
        self.assertEqual(self.dependencies["comfyui"]["version"], "0.29.0")
        self.assertEqual(self.workflow["extra"]["frontendVersion"], "1.47.10")

    def test_workflow_uses_rh_portable_nodes_only(self):
        node_types = {node["type"] for node in self.workflow["nodes"]}
        self.assertTrue(
            {
                "UNETLoader",
                "ImageScale",
                "MultiImageLoader",
                "SCAIL2SegmentPlanBuilder",
                "SCAIL2ScheduledLongVideoWithSAMV43",
            }.issubset(node_types)
        )
        self.assertTrue(
            {
                "DiffusionModelLoaderKJ",
                "ImageResizeKJv2",
                "SetNode",
                "GetNode",
                "Label (rgthree)",
                "FilmGrain",
            }.isdisjoint(node_types)
        )

    def test_reference_loader_supports_runninghub_batch_upload(self):
        reference_node = next(
            node for node in self.workflow["nodes"] if int(node["id"]) == 74
        )
        self.assertEqual(reference_node["type"], "MultiImageLoader")
        self.assertEqual(
            reference_node["properties"]["cnr_id"], "WhatDreamsCost-ComfyUI"
        )
        self.assertIn(
            "image_paths",
            [input_spec["name"] for input_spec in reference_node["inputs"]],
        )
        self.assertIn(
            "multi_output",
            [output_spec["name"] for output_spec in reference_node["outputs"]],
        )
        self.assertEqual(reference_node["widgets_values"][1:3], [720, 1280])
        self.assertEqual(reference_node["widgets_values"][4], "crop")
        reference_link = next(
            link
            for link in self.workflow["links"]
            if int(link[1]) == 74 and int(link[3]) == 65
        )
        self.assertEqual(int(reference_link[2]), 0)

    def test_frame_interpolation_has_a_visible_group_bypass_switch(self):
        bypassers = [
            node
            for node in self.workflow["nodes"]
            if node["type"] == "Fast Groups Bypasser (rgthree)"
        ]
        self.assertEqual(len(bypassers), 1)
        self.assertEqual(
            bypassers[0]["properties"]["matchTitle"],
            "Frame Interpolation 插帧",
        )
        self.assertIn(
            "Frame Interpolation 插帧",
            [group["title"] for group in self.workflow["groups"]],
        )

    def test_v43_node_points_to_the_rh_installable_repository(self):
        node = next(
            node
            for node in self.workflow["nodes"]
            if node["type"] == "SCAIL2ScheduledLongVideoWithSAMV43"
        )
        self.assertEqual(
            node["properties"]["aux_id"],
            "karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor",
        )
        self.assertEqual(
            node["properties"]["cnr_id"], "comfyui-scail2-v43-autocolor"
        )
        input_names = [input_spec["name"] for input_spec in node["inputs"]]
        self.assertIn("cache_mode", input_names)
        self.assertIn("disk", node["widgets_values"])

    def test_workflow_and_custom_node_versions_are_independent_and_consistent(self):
        project = tomllib.loads(
            (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        package_version = project["project"]["version"]
        custom_node = next(
            item
            for item in self.dependencies["custom_nodes"]
            if item["name"] == "SCAIL2 V4.3 Auto Color"
        )
        workflow_node = next(
            node
            for node in self.workflow["nodes"]
            if node["type"] == "SCAIL2ScheduledLongVideoWithSAMV43"
        )

        self.assertEqual(self.dependencies["workflow_version"], "5.0.0")
        self.assertEqual(package_version, "2.0.0")
        self.assertEqual(custom_node["version"], package_version)
        self.assertEqual(
            workflow_node["properties"]["ver"], package_version
        )

    def test_links_only_reference_existing_nodes_and_slots(self):
        nodes = {int(node["id"]): node for node in self.workflow["nodes"]}
        for link_id, source_id, source_slot, target_id, target_slot, _ in self.workflow[
            "links"
        ]:
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

    def test_manifest_lists_every_non_core_node_family(self):
        repos = {item["repository"] for item in self.dependencies["custom_nodes"]}
        self.assertEqual(
            repos,
            {
                "https://github.com/karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor",
                "https://github.com/TTPlanetPig/comfyui_scail2_multi_cond",
                "https://github.com/kijai/ComfyUI-GIMM-VFI",
                "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite",
                "https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI",
                "https://github.com/rgthree/rgthree-comfy",
            },
        )

    def test_custom_node_versions_match_the_manifest(self):
        workflow_nodes = {
            node["type"]: node
            for node in self.workflow["nodes"]
        }
        for dependency in self.dependencies["custom_nodes"]:
            expected_version = dependency.get("commit", dependency.get("version"))
            for node_type in dependency["required_nodes"]:
                with self.subTest(node_type=node_type):
                    self.assertIn(node_type, workflow_nodes)
                    self.assertEqual(
                        workflow_nodes[node_type]["properties"]["ver"],
                        expected_version,
                    )

    def test_every_manifest_model_is_embedded_for_rh_download(self):
        expected = {
            (model["folder"], model["name"], model["url"])
            for model in self.dependencies["models"]
        }
        embedded = {
            (model["directory"], model["name"], model["url"])
            for node in self.workflow["nodes"]
            for model in node.get("properties", {}).get("models", [])
        }
        self.assertEqual(embedded, expected)

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

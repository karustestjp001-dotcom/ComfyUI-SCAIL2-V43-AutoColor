import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

import torch


MODULE_PATH = Path(__file__).resolve().parents[1] / "nodes.py"
SPEC = importlib.util.spec_from_file_location("scail2_v43_nodes_under_test", MODULE_PATH)
SC = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SC)


class RecordingV43:
    last_call = None

    def correct(self, images, **kwargs):
        type(self).last_call = {"images": images.clone(), **kwargs}
        info = json.dumps({"mode": kwargs["mode"], "overlap": kwargs["overlap_count"]})
        return images + 0.01, f"details\n\n{info}"


class ColorModeTests(unittest.TestCase):
    def setUp(self):
        self.previous_nodes = sys.modules.get("nodes")
        sys.modules["nodes"] = types.SimpleNamespace(
            NODE_CLASS_MAPPINGS={"AutoColorDriftCorrection": RecordingV43}
        )
        RecordingV43.last_call = None

    def tearDown(self):
        if self.previous_nodes is None:
            sys.modules.pop("nodes", None)
        else:
            sys.modules["nodes"] = self.previous_nodes

    def test_input_schema_exposes_three_modes_and_upstream_default(self):
        required = SC.SCAIL2ScheduledLongVideoWithSAM.INPUT_TYPES()["required"]
        self.assertEqual(required["color_correction"][0], ["v43", "original", "off"])
        self.assertEqual(required["color_correction"][1]["default"], "v43")
        self.assertEqual(required["residual_strength"][1]["default"], 0.2)

    def test_legacy_boolean_modes_are_normalized(self):
        self.assertEqual(SC._normalize_color_correction_mode(True), "v43")
        self.assertEqual(SC._normalize_color_correction_mode(False), "off")

    def test_v43_receives_actual_overlap_and_selected_residual_strength(self):
        frames = torch.zeros((3, 2, 2, 3), dtype=torch.float32)
        current_overlap = torch.zeros((1, 2, 2, 3), dtype=torch.float32)
        reference_overlap = torch.ones((5, 2, 2, 3), dtype=torch.float32)

        corrected, info = SC._match_chunk_color_v43(
            frames, current_overlap, reference_overlap, residual_strength=0.2
        )

        self.assertEqual(RecordingV43.last_call["overlap_count"], 1)
        self.assertEqual(RecordingV43.last_call["prev_frames"].shape[0], 1)
        self.assertEqual(RecordingV43.last_call["residual_strength"], 0.2)
        self.assertEqual(info["overlap_frames"], 1)
        self.assertEqual(info["method"], "AutoColorDriftCorrectionV43")
        self.assertTrue(torch.allclose(corrected, torch.full_like(frames, 0.01)))

    def test_v43_does_not_silently_fall_back(self):
        sys.modules["nodes"] = types.SimpleNamespace(NODE_CLASS_MAPPINGS={})
        frames = torch.zeros((3, 2, 2, 3), dtype=torch.float32)
        overlap = torch.zeros((1, 2, 2, 3), dtype=torch.float32)
        with self.assertRaisesRegex(RuntimeError, "not registered"):
            SC._match_chunk_color_v43(frames, overlap, overlap, residual_strength=0.2)


if __name__ == "__main__":
    unittest.main()

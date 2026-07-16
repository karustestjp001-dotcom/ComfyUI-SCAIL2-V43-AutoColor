from .color_drift_correction import AutoColorDriftCorrection
from .nodes import NODE_CLASS_MAPPINGS as _SCAIL_NODE_CLASS_MAPPINGS


SCHEDULER_NODE_KEY = "SCAIL2ScheduledLongVideoWithSAMV43"

NODE_CLASS_MAPPINGS = {
    "AutoColorDriftCorrection": AutoColorDriftCorrection,
    SCHEDULER_NODE_KEY: _SCAIL_NODE_CLASS_MAPPINGS[SCHEDULER_NODE_KEY],
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoColorDriftCorrection": "Auto Color Drift Correction V4.3 (two-pass)",
    SCHEDULER_NODE_KEY: "SCAIL-2 Scheduled Long Video (Internal SAM + V4.3 Color)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

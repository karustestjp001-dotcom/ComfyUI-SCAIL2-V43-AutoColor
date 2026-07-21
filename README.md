# ComfyUI SCAIL-2 V4.3 Auto Color

This ComfyUI custom-node package provides the exact node type required by the
SCAIL-2 V4.3 auto-color workflow:

```text
SCAIL2ScheduledLongVideoWithSAMV43
```

It combines the SCAIL-2 scheduled long-video Internal SAM scheduler with
`Auto Color Drift Correction V4.3`. Color correction runs inside the scheduler
after every generated chunk. The correction receives the actual overlap for
that chunk, including a reduced `boundary_overlap` when a reference changes.

The scheduler exposes three deterministic color modes:

- `v43`: CustomNodeKit V4.3 auto correction;
- `original`: the original scheduler `ColorTransfer` / RGB overlap correction;
- `off`: no post-decode color correction.

## RunningHub installation

1. Open `Manager` in the RunningHub cloud workspace.
2. Select `Install via Git URL`.
3. Enter this repository URL:

   ```text
   https://github.com/karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor
   ```

4. Restart the ComfyUI workspace when installation completes.
5. Reload the workflow and verify that
   `SCAIL2ScheduledLongVideoWithSAMV43` is no longer reported as missing.

The package is self-contained for the V4.3 integration. Installing the full
`ComfyUI-CustomNodeKit` separately is not required for this workflow.

## Integrated color settings

```text
color_correction = v43 | original | off
residual_strength = 0.2 (adjustable from 0.0 to 1.0; V4.3 only)
V4.3 mode = auto
V4.3 max_offset = 0.02
overlap_count = actual chunk overlap
```

Do not add a second color-correction node after the final frames; this scheduler
already performs correction inside its chunk loop.

V4.3 failures are reported as errors instead of silently falling back to the
original correction, so A/B tests always reflect the selected mode.

## Credits

- Scheduled long-video implementation derived from
  [TTPlanetPig/comfyui_scail2_multi_cond](https://github.com/TTPlanetPig/comfyui_scail2_multi_cond).
- V4.3 correction implementation derived from
  [user2318/ComfyUI-CustomNodeKit](https://github.com/user2318/ComfyUI-CustomNodeKit).
- Workflow method demonstrated by Bilibili creator
  [iceage26107](https://space.bilibili.com/26889268/).

Both upstream projects declare the MIT license in their package metadata.

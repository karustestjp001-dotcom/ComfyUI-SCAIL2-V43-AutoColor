# ComfyUI SCAIL-2 V5.0 RH Workflow + V4.3 Auto Color

This repository contains the RunningHub-portable V5.0 long-video workflow and
the exact custom node required to keep V4.3 color correction inside the
SCAIL-2 chunk scheduler:

```text
SCAIL2ScheduledLongVideoWithSAMV43
```

It combines the SCAIL-2 scheduled long-video Internal SAM scheduler with
`Auto Color Drift Correction V4.3`. Color correction runs inside the scheduler
after every generated chunk. The correction receives the actual overlap for
that chunk, including a reduced `boundary_overlap` when a reference changes.

V5.0 rebases the scheduler on
`TTPlanetPig/comfyui_scail2_multi_cond@aac3315`, targets ComfyUI `0.29.0`, and
removes KJNodes and post-processing dependencies from the RH workflow graph.
It keeps WhatDreamsCost's batch image loader and rgthree's visible group
bypasser because they are user-facing workflow controls. The V4.3 correction
algorithm itself is unchanged.

## Workflow

```text
workflows/ComfyUI SCAIL 2 極簡長視頻生成_V5.0_RH直用版.json
```

The workflow uses the official core `UNETLoader` and `ImageScale` nodes, plus
`MultiImageLoader` for uploading multiple reference images. Upload the reference
images and a driving video before queueing.

The scheduler exposes three deterministic color modes:

- `v43`: CustomNodeKit V4.3 auto correction;
- `original`: the original scheduler `ColorTransfer` / RGB overlap correction;
- `off`: no post-decode color correction.

## RunningHub installation

1. Use a RunningHub workspace with ComfyUI `0.29.0` or a compatible newer
   version.
2. Open `Manager` and install these repositories through `Install via Git URL`:

   ```text
   https://github.com/karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor
   https://github.com/TTPlanetPig/comfyui_scail2_multi_cond
   https://github.com/kijai/ComfyUI-GIMM-VFI
   https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
   https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI
   https://github.com/rgthree/rgthree-comfy
   ```

3. Restart the cloud workspace when installation completes.
4. Import the V5.0 JSON from the `workflows` folder.
5. Confirm that `SCAIL2ScheduledLongVideoWithSAMV43` and
   `SCAIL2SegmentPlanBuilder` are not reported as missing.
6. Resolve the model files listed in `rh_dependencies.json`, then use
   `MultiImageLoader` to batch-upload reference images and upload the driving
   video. Reference images are center-cropped to `720x1280` so mixed source
   dimensions still form a valid image batch. Use the visible
   `Frame Interpolation 插帧` group switch to enable or bypass GIMM frame
   interpolation.

The V4.3 integration is self-contained; installing the full
`ComfyUI-CustomNodeKit` is not required. The separate upstream
`comfyui_scail2_multi_cond` repository supplies the segment-plan builder.

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

The official SCAIL-2 Relighting LoRA is intended for replacement mode and is
not enabled in this animation workflow.

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

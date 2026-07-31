# ComfyUI SCAIL-2 V5.0.1 RH Workflow + V4.3 Auto Color

這個版本是「ComfyUI SCAIL 2 極簡長視頻生成 V4.3 自動校色 RH
上傳版」的功能完整複製版。V5.0.1 只更新 ComfyUI 核心／前端版本資訊，
不再替換節點、不刪除相依、不修改參數，也不重接工作流。

## 工作流

```text
workflows/ComfyUI SCAIL 2 極簡長視頻生成_V5.0_RH直用版.json
```

已驗證的結構：

- ComfyUI `0.29.2`、frontend `1.47.11`
- 42 個節點、32 條連線、5 個群組
- `ImageResizeKJv2` 完整 10 輸入／4 輸出
- 寬高輸出仍連到 `MultiImageLoader`
- 原有多圖載入介面、V4.3 自動校色、FilmGrain 與 GIMM 補幀全數保留
- `Fast Groups Bypasser` 仍是「Frame Interpolation 插帧」群組的啟用／
  略過開關

生成器內建功能指紋檢查；若未來任何修改使圖結構偏離 V4.3，建置會直接
失敗。

## RunningHub 必裝自訂節點

透過 Manager 的 `Install via Git URL` 安裝：

```text
https://github.com/karustestjp001-dotcom/ComfyUI-SCAIL2-V43-AutoColor
https://github.com/TTPlanetPig/comfyui_scail2_multi_cond
https://github.com/kijai/ComfyUI-KJNodes
https://github.com/EllangoK/ComfyUI-post-processing-nodes
https://github.com/kijai/ComfyUI-GIMM-VFI
https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI
https://github.com/rgthree/rgthree-comfy
```

安裝完成後重啟 RunningHub 工作空間，再匯入 JSON。模型檔名、下載位置與
本機驗證版本列在 `rh_dependencies.json`。

## 使用重點

- 參考圖：使用原本的 `MultiImageLoader`；其動態多圖輸出與 V4.3 行為未改。
- 驅動影片：在原本 `VHS_LoadVideo` 上傳。
- 增幀：使用「Frame Interpolation 插帧」群組的 rgthree 開關；開啟才走
  GIMM-VFI，略過則直接輸出原始幀序列。
- V4.3 校色已整合在長影片分段排程器內，不要再接第二個末端校色節點。

## 驗證

```powershell
python -m unittest discover -s tests -v
```

工作流契約測試會確認它與 V4.3 功能一致，並逐項檢查節點 17 的插槽及
四條連線，避免再次出現「只有核心 Upscale Image 四個選項」的退化。

## Credits

- [TTPlanetPig/comfyui_scail2_multi_cond](https://github.com/TTPlanetPig/comfyui_scail2_multi_cond)
- [user2318/ComfyUI-CustomNodeKit](https://github.com/user2318/ComfyUI-CustomNodeKit)
- [iceage26107](https://space.bilibili.com/26889268/)

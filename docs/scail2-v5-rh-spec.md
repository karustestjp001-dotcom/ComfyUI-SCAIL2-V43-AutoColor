# SCAIL-2 V5.0.1 RunningHub 直用版規格

## 唯一改版原則

V5.0.1 以「ComfyUI SCAIL 2 極簡長視頻生成 V4.3 自動校色 RH
上傳版」為唯一基準，工作流功能必須原樣保留。允許的差異只有：

- ComfyUI 核心節點版本更新為 `0.29.2`。
- 前端版本更新為 `1.47.11`。
- 清除來源電腦的圖片檔名、影片檔名與影片預覽暫存。
- 在 `extra.scail2_v5` 記錄非功能性的版本說明。

不得替換、刪除、增加或重新接線任何功能節點，也不得修改節點參數、
群組、版面、輸入／輸出插槽或自訂節點版本資訊。

## 必須完整保留

- V4.3 分段自動校色及原有三種校色模式。
- KJNodes 的 `DiffusionModelLoaderKJ`、`ImageResizeKJv2`、`SetNode`、
  `GetNode`。
- `ImageResizeKJv2` 的 `width`、`height` 輸出至 `MultiImageLoader` 的兩條
  尺寸連線。
- WhatDreamsCost `MultiImageLoader` 原有多圖介面與動態輸出。
- rgthree 的 `Label` 與 `Fast Groups Bypasser` 補幀群組開關。
- GIMM-VFI 補幀、Video Helper Suite 輸入／輸出與 FilmGrain。
- 原始 42 個節點、32 條連線、5 個群組及所有節點參數。

## 驗收條件

- 正規化後的工作流功能 SHA-256 必須為
  `c417d31fb63c7c7ba013addccd56ffc5cc5f78b3fea1752d7df64955795b8864`。
- 節點 17 必須是 `ImageResizeKJv2`，保有 10 個輸入、4 個輸出及 4 條
  相連連線。
- 所有連線引用的節點與插槽都存在。
- `rh_dependencies.json` 必須涵蓋工作流使用的所有非核心節點。
- JSON 不得包含來源電腦絕對路徑、RH 預覽網址或測試素材名稱。
- 本機 ComfyUI `0.29.2` 必須能註冊所有後端節點。

完整長影片生成不屬於結構驗收；避免為了確認 JSON 而消耗大量本機或
RunningHub 算力。

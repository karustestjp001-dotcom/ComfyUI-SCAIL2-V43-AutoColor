# SCAIL-2 V5.0.2 RunningHub 直用版規格

## 唯一改版原則

V5.0.2 以「ComfyUI SCAIL 2 極簡長視頻生成 V4.3 自動校色 RH
上傳版」為唯一基準，工作流功能與 RH 序列化相容資訊都必須原樣保留。
允許的差異只有：

- 清除來源電腦的圖片檔名、影片檔名與影片預覽暫存。
- 將 `LoraLoaderModelOnly` 與 `DiffusionModelLoaderKJ` 的本機 `wan\\`
  子資料夾前綴移除，使用 RunningHub 模型清單中的扁平檔名。

實際執行環境另由 `rh_dependencies.json` 指定並驗證為 ComfyUI `0.29.2`、
frontend `1.47.11`。工作流 JSON 仍保留 V4.3 的 frontend `1.45.15` 與原始
核心節點版本標記；不得加入 `extra.scail2_v5` 等 RH 未知欄位。

不得替換、刪除、增加或重新接線任何功能節點，也不得修改節點參數、
群組、版面、輸入／輸出插槽或自訂節點版本資訊。

## 已知 RunningHub 相容問題

- V4.3 曾出現過相同的模型驗證錯誤：本機工作流把模型保存成
  `wan\\檔名`，但 RunningHub 的模型 combo 使用扁平檔名。
- 典型訊息為 `Prompt outputs failed validation`，並在
  `LoraLoaderModelOnly` 或 `DiffusionModelLoaderKJ` 顯示
  `Value not in list`。
- RH 建置時必須移除這兩個節點模型值的 `wan\\` 前綴；不得把這個問題
  誤判為接線、登入或瀏覽器故障。

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
  `208be32926cc620be2c977019891c5c06255d06112c9acada341e8c4913be337`。
- 節點 17 必須是 `ImageResizeKJv2`，保有 10 個輸入、4 個輸出及 4 條
  相連連線。
- 所有連線引用的節點與插槽都存在。
- `rh_dependencies.json` 必須涵蓋工作流使用的所有非核心節點。
- JSON 不得包含來源電腦絕對路徑、RH 預覽網址或測試素材名稱。
- JSON 的 `extra.frontendVersion` 必須是 V4.3 原值 `1.45.15`，且不得包含
  `extra.scail2_v5`。
- LoRA 與 SCAIL-2 diffusion model 的 combo 值必須與
  `rh_dependencies.json` 的模型檔名完全一致，不得包含 `wan\\` 前綴。
- 本機 ComfyUI `0.29.2` 必須能註冊所有後端節點。

完整長影片生成不屬於結構驗收；避免為了確認 JSON 而消耗大量本機或
RunningHub 算力。

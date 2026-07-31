# SCAIL-2 V5.0 RunningHub 直用版規格

## 目標

以既有「ComfyUI SCAIL 2 極簡長視頻生成 V4.3 自動校色 RH
上傳版」為基礎，更新到 2026-07-31 的穩定 ComfyUI 核心與相依節點，
產出一份可匯入 RunningHub 的 V5.0 工作流。

## 必要條件

- 對齊 ComfyUI 0.29.0 與前端 1.47.10。
- 保留整合在長影片分段排程器內的 V4.3 自動校色。
- 使用官方核心節點取代可移除的 KJNodes、rgthree、
  WhatDreamsCost 與 post-processing 相依。
- 保留 SCAIL-2 分段規劃、GIMM 補幀與 Video Helper Suite
  影片輸入／輸出能力。
- 工作流不得包含本機絕對路徑、舊 RH 預覽網址或使用者測試素材檔名。
- 列出 RunningHub 必裝的自訂節點、固定驗證版本及模型下載位置。
- 官方 Relighting LoRA 只支援 replacement 模式，不納入 animation
  長影片預設路徑。

## 驗收條件

- JSON 可由 ComfyUI 0.29.0 載入。
- 工作流中所有節點類型都能在更新後的本機環境註冊。
- 所有連線引用的節點與插槽存在。
- RunningHub 匯入後不出現缺失節點；模型與兩個使用者輸入可依清單補齊。
- 自訂節點單元測試與工作流契約測試全部通過。
- 不在驗證階段啟動會消耗大量本機時間或 RH 算力的完整長影片生成。


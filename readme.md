# 期貨未平倉量變化通知機器人

## 專案說明
這是一個 Telegram 機器人，用於通知期貨未平倉量的變化情況。機器人會定期檢查數據並透過 Telegram 發送通知。

## 功能特點
- 自動抓取期貨未平倉量數據
- 自動排程發送變化通知每天的 6:05(夜盤), 14:05(日盤), 15:05(日盤)
- 6:05, 14:05 透過前一天資料試算新未平倉資料，15:05 是期交所公佈資料

## 安裝需求
- Python 3.11.7

## 環境設定
1. 建立 `.env` 檔案並設定以下環境變數：
```
TELEGRAM_BOT_TOKEN=你的機器人Token
```

2. 安裝相依套件：
```sh
pip install -r requirements.txt
```

## 使用方式
1. 執行主程式：
```sh
python main.py
```

2. 前往 Telegram 頻道在聊天室輸入任何文字，讓機器人註冊聊天室

## 專案結構
```
bot_fwbtin_notify/
├── main.py            # 主程式
├── fwbtin_daily.py    # 資料抓取
├── chat_ids.json      # 已註冊了聊天室清單
└── telegram_bot/      # 機器人核心模組
    ├── bot_core.py    # 機器人主要功能
    └── scheduler.py   # 排程設定
    
history_data/tw/
├── fwbtin/            # 15:00 抓的資料
├── fwbtin_raw_6/      # 6:00 抓的資料
├── fwbtin_raw_14/     # 14:00 抓的資料
└── fwbtin_tx/    
    ├── announced_data.csv    # 公佈的資料
    └── calculated_data.csv   # 試算的資料、包含日、夜盤   
```

## 資料來源
- 期貨未平倉量資料來自台灣期貨交易所

## 授權條款
本專案採用 MIT 授權條款
import os
import json
from pathlib import Path
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_RECORD_FILE = Path("bot_fwbtin_notify/chat_ids.json")
bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
bot = Bot(token=TELEGRAM_TOKEN)

def load_chat_ids():
    if CHAT_RECORD_FILE.exists():
        return set(json.loads(CHAT_RECORD_FILE.read_text()))
    return set()

def save_chat_ids(chat_ids):
    CHAT_RECORD_FILE.write_text(json.dumps(list(chat_ids)))

# ✅ 註冊聊天室
async def auto_register_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        chat_ids.add(chat_id)
        save_chat_ids(chat_ids)
        print(f"✅ 新聊天室加入：{chat_id}")

# ✅ 廣播
async def broadcast(text):
    chat_ids = load_chat_ids()
    for cid in chat_ids:
        try:
            await bot.send_message(chat_id=cid, text=text)
        except Exception as e:
            print(f"❌ 傳送錯誤 {cid}: {e}")

# ✅ 手動 hello 指令
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 Hello {update.effective_user.first_name}")

bot_app.add_handler(CommandHandler("hello", hello))
bot_app.add_handler(MessageHandler(filters.ALL, auto_register_chat))
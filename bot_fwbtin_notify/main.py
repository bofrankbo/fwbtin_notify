# main.py ✅ 正確寫法
from telegram_bot.bot_core import bot_app
from telegram_bot.scheduler import setup_schedule
import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_schedule())  # 啟動排程（需要 async 執行）
    bot_app.run_polling()  # 由 telegram bot 自己開 event loop
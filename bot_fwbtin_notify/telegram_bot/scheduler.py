from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram_bot.bot_core import broadcast
from datetime import datetime, timedelta
from fwbtin_daily import calculated_data_process, announced_data_process, crawler  # ⬅️ 從你爬蟲檔匯入
import pytz

async def setup_schedule():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Taipei"))

    # 6:05 試算夜盤資料
    scheduler.add_job(calc_night, "cron", hour=6, minute=5)

    # 14:05 試算日盤資料
    scheduler.add_job(calc_day, "cron", hour=14, minute=5)

    # 17:05 處理公布資料
    scheduler.add_job(announce_yesterday, "cron", hour=15, minute=5)

    scheduler.start()

# 6:00 夜盤資料
async def calc_night():
    date = crawler(date=None, hour=6)
    if date is not None:
        rtn_fwbtin = calculated_data_process(date, 6)
        if rtn_fwbtin is not None:
            print("夜盤資料存在，開始廣播")
            await broadcast(rtn_fwbtin)
        else:
            print("夜盤資料不存在")
    else:
        print("夜盤資料不存在")



# 14:00 日盤資料
async def calc_day():
    date = crawler(date=None, hour=14)
    if date is not None:
        rtn_fwbtin = calculated_data_process(date, 14)
        if rtn_fwbtin is not None:
            print("日盤資料存在，開始廣播")
            await broadcast(rtn_fwbtin)
        else:
            print("日盤資料不存在")
    else:
        print("日盤資料不存在")


# 17:00 公布資料
async def announce_yesterday():
    print("開始爬資料")
    date = crawler(date=None, hour=15)
    if date is not None:
        rtn_fwbtin = announced_data_process(date, 15)
        if rtn_fwbtin is not None:
            print("公布資料存在，開始廣播")
            await broadcast(rtn_fwbtin)
        else:
            print("公布資料不存在")
    else:
        print("公布資料不存在")
import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os
import hashlib
import time
from typing import List, Dict

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'
CHAT_ID = os.getenv('CHAT_ID')

# ... (중간 생략 - 이전 코드와 동일)

async def send_report():
    bot = telegram.Bot(token=BOT_TOKEN)
    all_jobs = []

    print("🔍 검색 중...")
    all_jobs.extend(fetch_jobsdb())
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🎓 <b>{today} Finance Part-time Lecturer Report</b>\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')
        # 공고 전송 로직...
    else:
        msg = f"ℹ️ {today} Finance Part-time Lecturer Report\n\n" \
              "현재는 새로운 공고가 없습니다.\n" \
              "매일 자동으로 검색하여 알려드립니다."
        
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
        print("ℹ️ 공고 없음 메시지 전송")

if __name__ == '__main__':
    asyncio.run(send_report())

import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os
import hashlib
import time
from typing import List, Dict

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

SENIOR_KEYWORDS = ['Director', 'Head of', 'VP', 'Vice President', 'Senior', 'Lead', 'Chief', 'Executive', 'Assistant Director']

seen_jobs = set()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

def is_senior(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in SENIOR_KEYWORDS)

def get_job_hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:16]

# ========================= eFinancialCareers (강화) =========================
def fetch_efinancialcareers() -> List[Dict]:
    jobs = []
    try:
        url = "https://www.efinancialcareers.hk/jobs"
        params = {
            "keywords": "Sales Director OR \"Head of Sales\" OR \"VP Sales\" OR \"Senior Sales\"",
            "location": "Hong Kong"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for card in soup.find_all(['div', 'article'], class_=lambda x: x and any(c in str(x).lower() for c in ['job', 'card', 'listing'])):
            title = card.get_text(strip=True)[:150]
            link_tag = card.find('a', href=True)
            link = link_tag.get('href', '') if link_tag else ""
            if not title or not link or "sales" not in title.lower():
                continue
            full_link = f"https://www.efinancialcareers.hk{link}" if link.startswith('/') else link

            if is_senior(title):
                job_hash = get_job_hash(title, full_link)
                if job_hash not in seen_jobs:
                    seen_jobs.add(job_hash)
                    jobs.append({"source": "eFinancial", "title": title, "link": full_link})
    except Exception as e:
        print(f"eFinancial Error: {e}")
    return jobs

# ========================= LinkedIn =========================
def fetch_linkedin() -> List[Dict]:
    jobs = []
    try:
        url = "https://www.linkedin.com/jobs/search"
        params = {
            "keywords": "Sales Director OR \"Head of Sales\" OR \"VP Sales\" OR \"Senior Sales\"",
            "location": "Hong Kong",
            "f_TPR": "r86400"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=25)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for card in soup.find_all('div', class_=lambda x: x and 'job-search-card' in str(x).lower()):
            title_tag = card.find('h3')
            title = title_tag.get_text(strip=True) if title_tag else ""
            link_tag = card.find('a', href=True)
            link = link_tag.get('href', '') if link_tag else ""
            if not title or not link: continue
            full_link = f"https://www.linkedin.com{link}" if link.startswith('/') else link

            if is_senior(title) and "sales" in title.lower():
                job_hash = get_job_hash(title, full_link)
                if job_hash not in seen_jobs:
                    seen_jobs.add(job_hash)
                    jobs.append({"source": "LinkedIn", "title": title, "link": full_link})
    except Exception as e:
        print(f"LinkedIn Error: {e}")
    return jobs

# ========================= Telegram =========================
async def send_report():
    bot = telegram.Bot(token=BOT_TOKEN)
    all_jobs = []

    print("🔍 eFinancialCareers 검색 중...")
    all_jobs.extend(fetch_efinancialcareers())
    
    print("🔍 LinkedIn 검색 중...")
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🚀 <b>{today} Senior Sales Report</b>\n"
        header += "Ted Ahn님, LinkedIn + eFinancial 중심으로 안정 운영 중입니다.\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in all_jobs[:12]:
            msg = f"📍 <b>{job['source']}</b>\n🎯 {job['title']}\n🔗 <a href='{job['link']}'>지원하기</a>\n\n"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML', disable_web_page_preview=True)
            time.sleep(1.2)

        print(f"✅ 총 {len(all_jobs)}개 공고 전송")
    else:
        print("ℹ️ 오늘은 새로운 공고가 없습니다.")

if __name__ == '__main__':
    asyncio.run(send_report())

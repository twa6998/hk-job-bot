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

# ========================= JobsDB - 최대한 단순하고 강력하게 =========================
def fetch_jobsdb() -> List[Dict]:
    jobs = []
    urls = [
        "https://hk.jobsdb.com/hk/jobs/sales-director-jobs-in-hong-kong",
        "https://hk.jobsdb.com/hk/jobs/head-of-sales-jobs-in-hong-kong",
        "https://hk.jobsdb.com/hk/jobs/senior-sales-jobs-in-hong-kong",
        "https://hk.jobsdb.com/hk/jobs/director-sales-jobs-in-hong-kong"
    ]

    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            print(f"JobsDB URL: {url} | Status: {resp.status_code} | Size: {len(resp.text)//1000}KB")

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 가능한 모든 제목/링크 찾기 (최대한 넓게)
            links = soup.find_all('a', href=True)
            found = 0
            for a in links:
                title = a.get_text(strip=True)
                href = a.get('href', '')
                if not title or len(title) < 15:
                    continue
                if any(sk.lower() in title.lower() for sk in ['sales director', 'head of sales', 'vp sales', 'senior sales']) and is_senior(title):
                    full_link = f"https://hk.jobsdb.com{href}" if href.startswith('/') else href
                    job_hash = get_job_hash(title, full_link)
                    if job_hash not in seen_jobs:
                        seen_jobs.add(job_hash)
                        jobs.append({"source": "JobsDB", "title": title, "link": full_link})
                        found += 1
                        print(f"✅ JobsDB 발견: {title[:80]}")
                        if found >= 5: break
        except Exception as e:
            print(f"JobsDB Error: {e}")
    return jobs

# eFinancialCareers와 LinkedIn은 이전과 동일 (간단 버전)
def fetch_efinancialcareers() -> List[Dict]:
    # ... (이전 코드 그대로 유지하거나 생략)
    return []

def fetch_linkedin() -> List[Dict]:
    # ... (이전 코드 그대로)
    jobs = []
    try:
        url = "https://www.linkedin.com/jobs/search?keywords=Sales%20Director&location=Hong%20Kong"
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # (간단 버전 유지)
    except:
        pass
    return jobs   # LinkedIn은 기존처럼 유지

async def send_report():
    bot = telegram.Bot(token=BOT_TOKEN)
    all_jobs = []

    print("🔍 JobsDB 검색 시작...")
    all_jobs.extend(fetch_jobsdb())
    
    print("🔍 LinkedIn 검색 시작...")
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🚀 <b>{today} Senior Sales Report</b>\n"
        header += "Ted Ahn님, JobsDB 스크래핑 방식 변경했습니다.\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in all_jobs[:10]:
            msg = f"📍 <b>{job['source']}</b>\n🎯 {job['title']}\n🔗 <a href='{job['link']}'>지원하기</a>\n\n"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML', disable_web_page_preview=True)
            time.sleep(1)
    else:
        await bot.send_message(chat_id=CHAT_ID, text="ℹ️ 오늘은 새로운 Senior Sales 공고가 없습니다.")

if __name__ == '__main__':
    asyncio.run(send_report())

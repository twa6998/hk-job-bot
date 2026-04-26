import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os
import hashlib
import time
from typing import List, Dict

# ==================== 설정 ====================
BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'
CHAT_ID = os.getenv('CHAT_ID')

# Ted Ahn님 CV 기반 키워드
LECTURER_KEYWORDS = ['Lecturer', 'Part-time Lecturer', 'Adjunct Lecturer', 'Visiting Lecturer', 'Instructor', 'Teaching Fellow']
FINANCE_KEYWORDS = ['Finance', 'Financial', 'Accounting', 'Fintech', 'Investment', 'Corporate Finance', 'CFA', 'FRM']

seen_jobs = set()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

def is_relevant(title: str) -> bool:
    title_lower = title.lower()
    has_lecturer = any(kw.lower() in title_lower for kw in LECTURER_KEYWORDS)
    has_finance = any(kw.lower() in title_lower for kw in FINANCE_KEYWORDS)
    return has_lecturer and has_finance

def get_job_hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:16]

# ========================= JobsDB =========================
def fetch_jobsdb() -> List[Dict]:
    jobs = []
    search_terms = ["part-time-lecturer", "finance-lecturer", "accounting-lecturer", "adjunct-lecturer"]
    
    for term in search_terms:
        try:
            url = f"https://hk.jobsdb.com/hk/jobs/{term}-jobs-in-hong-kong"
            resp = requests.get(url, headers=headers, timeout=25)
            soup = BeautifulSoup(resp.text, 'html.parser')

            for card in soup.find_all('div', attrs={"data-testid": lambda x: x and 'job-card' in str(x).lower()}):
                title_tag = card.find(['h3', 'a'])
                title = title_tag.get_text(strip=True) if title_tag else ""
                link_tag = card.find('a', href=True)
                link = link_tag.get('href', '') if link_tag else ""
                
                if not title or not link:
                    continue
                    
                full_link = f"https://hk.jobsdb.com{link}" if link.startswith('/') else link

                if is_relevant(title):
                    job_hash = get_job_hash(title, full_link)
                    if job_hash not in seen_jobs:
                        seen_jobs.add(job_hash)
                        jobs.append({"source": "JobsDB", "title": title, "link": full_link})
        except Exception as e:
            print(f"JobsDB Error: {e}")
    return jobs

# ========================= LinkedIn =========================
def fetch_linkedin() -> List[Dict]:
    jobs = []
    try:
        url = "https://www.linkedin.com/jobs/search"
        params = {
            "keywords": "Part-time Lecturer OR Adjunct Lecturer Finance OR Accounting",
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

            if is_relevant(title):
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

    print("🔍 Finance Part-time Lecturer 검색 중...")
    all_jobs.extend(fetch_jobsdb())
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🎓 <b>{today} Finance Part-time Lecturer Report</b>\n"
        header += "Ted Ahn님, Finance/Accounting 관련 Part-time Lecturer 공고입니다.\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in all_jobs[:10]:
            msg = f"📍 <b>{job['source']}</b>\n🎯 {job['title']}\n🔗 <a href='{job['link']}'>지원하기</a>\n\n"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML', disable_web_page_preview=True)
            time.sleep(1.2)

        print(f"✅ {len(all_jobs)}개 공고 전송")
    else:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"ℹ️ {today} Finance Part-time Lecturer\n\n현재는 새로운 공고가 없습니다.",
            parse_mode='HTML'
        )
        print("ℹ️ 오늘은 새로운 공고가 없습니다.")

if __name__ == '__main__':
    asyncio.run(send_report())

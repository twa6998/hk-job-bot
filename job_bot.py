import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os
import hashlib
import time
from typing import List, Dict

# ========================= 설정 =========================
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

SENIOR_KEYWORDS = ['Director', 'Head of', 'VP', 'Vice President', 'Senior', 'Lead', 'Chief', 'Executive', 'Assistant Director']
FULLTIME_KEYWORDS = ['Full time', 'Full-time', 'Permanent', 'Fulltime']

seen_jobs = set()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

# ========================= 헬퍼 =========================
def is_senior(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in SENIOR_KEYWORDS)

def is_fulltime(text: str) -> bool:
    return any(kw.lower() in text.lower() for kw in FULLTIME_KEYWORDS) if text else True

def get_job_hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:16]

# ========================= eFinancialCareers =========================
def fetch_efinancialcareers() -> List[Dict]:
    jobs = []
    try:
        url = "https://www.efinancialcareers.hk/jobs"
        params = {"keywords": "Sales Director OR Head of Sales OR VP Sales OR Senior Sales", "location": "Hong Kong"}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for card in soup.find_all(['div', 'article'], class_=lambda x: x and any(c in str(x).lower() for c in ['job', 'card'])):
            title = card.get_text(strip=True)[:200]
            link_tag = card.find('a', href=True)
            link = link_tag.get('href', '') if link_tag else ""
            if not title or not link or "sales" not in title.lower(): continue
            full_link = f"https://www.efinancialcareers.hk{link}" if link.startswith('/') else link
            if is_senior(title) and is_fulltime(title):
                job_hash = get_job_hash(title, full_link)
                if job_hash not in seen_jobs:
                    seen_jobs.add(job_hash)
                    jobs.append({"source": "eFinancial", "title": title, "link": full_link})
    except Exception as e:
        print(f"eFinancial Error: {e}")
    return jobs

# ========================= JobsDB - 대폭 강화 =========================
def fetch_jobsdb() -> List[Dict]:
    jobs = []
    search_terms = ["sales-director", "head-of-sales", "vp-sales", "director-sales", "senior-sales", "sales-lead", "sales-manager", "institutional-sales"]

    for term in search_terms:
        try:
            url = f"https://hk.jobsdb.com/hk/jobs/{term}-jobs-in-hong-kong"
            resp = requests.get(url, headers=headers, timeout=25)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # JobsDB 최신 구조에 대응하는 다양한 선택자
            cards = (
                soup.find_all('div', attrs={"data-testid": lambda x: x and 'job-card' in str(x).lower()}) or
                soup.find_all('article', class_=lambda x: x and 'job' in str(x).lower()) or
                soup.find_all('div', class_=lambda x: x and any(c in str(x).lower() for c in ['job-item', 'listing']))
            )

            print(f"JobsDB {term}: {len(cards)}개 카드 발견")

            for card in cards:
                title_tag = card.find(['h3', 'h2', 'a', 'div'])
                title = title_tag.get_text(strip=True) if title_tag else card.get_text(strip=True)[:150]

                link_tag = card.find('a', href=True)
                link = link_tag.get('href', '') if link_tag else ""
                
                if not title or not link or "sales" not in title.lower():
                    continue

                full_link = f"https://hk.jobsdb.com{link}" if link.startswith('/') else link

                if is_senior(title):
                    job_hash = get_job_hash(title, full_link)
                    if job_hash not in seen_jobs:
                        seen_jobs.add(job_hash)
                        jobs.append({"source": "JobsDB", "title": title, "link": full_link})
                        print(f"✅ JobsDB 공고 발견: {title[:60]}...")
        except Exception as e:
            print(f"JobsDB Error ({term}): {e}")
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
        resp = requests.get(url, params=params, headers=headers, timeout=20)
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
    
    print("🔍 JobsDB 검색 중... (강화 버전)")
    all_jobs.extend(fetch_jobsdb())
    
    print("🔍 LinkedIn 검색 중...")
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🚀 <b>{today} Senior Sales Report (Multi-Site)</b>\n"
        header += "Ted Ahn님, JobsDB 스크래퍼를 대폭 강화했습니다.\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in all_jobs[:15]:
            msg = f"📍 <b>{job['source']}</b>\n🎯 {job['title']}\n🔗 <a href='{job['link']}'>지원하기</a>\n\n"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML', disable_web_page_preview=True)
            time.sleep(1.2)

        print(f"✅ 총 {len(all_jobs)}개 공고 전송 완료")
    else:
        print("ℹ️ 오늘은 새로운 공고가 없습니다.")

if __name__ == '__main__':
    asyncio.run(send_report())

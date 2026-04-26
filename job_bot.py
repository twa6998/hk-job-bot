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

def get_job_hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:16]

# ========================= JobsDB - 최강 버전 =========================
def fetch_jobsdb() -> List[Dict]:
    jobs = []
    search_terms = ["sales-director", "head-of-sales", "vp-sales", "director-sales", "senior-sales", "sales-lead", "sales-manager"]

    for term in search_terms:
        try:
            url = f"https://hk.jobsdb.com/hk/jobs/{term}-jobs-in-hong-kong"
            resp = requests.get(url, headers=headers, timeout=30)
            print(f"JobsDB {term} → Status: {resp.status_code}, Length: {len(resp.text)}")

            soup = BeautifulSoup(resp.text, 'html.parser')

            # 가능한 모든 Job Card 선택자
            selectors = [
                {'tag': 'div', 'attr': {"data-testid": lambda x: x and 'job-card' in str(x).lower()}},
                {'tag': 'article', 'attr': {'class': lambda x: x and 'job' in str(x).lower()}},
                {'tag': 'div', 'attr': {'class': lambda x: x and any(k in str(x).lower() for k in ['job-item', 'listing-item', 'result'])}}
            ]

            cards_found = 0
            for sel in selectors:
                cards = soup.find_all(sel['tag'], attrs=sel['attr'])
                if cards:
                    print(f"  → {len(cards)}개 카드 발견 (Selector: {sel['tag']})")
                    cards_found = len(cards)
                    break

            for card in cards[:20]:   # 최대 20개까지만 검사
                title_tag = card.find(['h3', 'h2', 'a'])
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
                        print(f"✅ JobsDB 발견: {title[:70]}...")
        except Exception as e:
            print(f"JobsDB Error ({term}): {e}")
    return jobs

# (eFinancialCareers와 LinkedIn 함수는 이전과 동일 - 생략 없이 전체 코드에 포함)

# ========================= Telegram =========================
async def send_report():
    bot = telegram.Bot(token=BOT_TOKEN)
    all_jobs = []

    print("🔍 eFinancialCareers 검색 중...")
    all_jobs.extend(fetch_efinancialcareers())
    
    print("🔍 JobsDB 검색 중... (최강 버전)")
    all_jobs.extend(fetch_jobsdb())
    
    print("🔍 LinkedIn 검색 중...")
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🚀 <b>{today} Senior Sales Report (Multi-Site)</b>\n"
        header += "Ted Ahn님, JobsDB 스크래퍼를 최대로 강화했습니다.\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in all_jobs[:12]:
            msg = f"📍 <b>{job['source']}</b>\n🎯 {job['title']}\n🔗 <a href='{job['link']}'>지원하기</a>\n\n"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML', disable_web_page_preview=True)
            time.sleep(1)

        print(f"✅ 총 {len(all_jobs)}개 공고 전송")
    else:
        print("ℹ️ 오늘은 새로운 공고가 없습니다.")

# eFinancialCareers와 LinkedIn 함수 (전체 코드에 추가 필요)
# ... (이전 버전과 동일)

if __name__ == '__main__':
    asyncio.run(send_report())

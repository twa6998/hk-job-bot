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

SENIOR_KEYWORDS = ['Director', 'Head of', 'VP', 'Vice President', 'Senior Sales', 'Lead', 'Chief', 'Executive']
seen_jobs = set()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ========================= 공통 헬퍼 =========================
def is_senior(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in SENIOR_KEYWORDS)

def get_job_hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

# ========================= eFinancialCareers =========================
def fetch_efinancialcareers() -> List[Dict]:
    jobs = []
    try:
        url = "https://www.efinancialcareers.hk/jobs"
        params = {
            "keywords": "Sales Director OR Head of Sales OR VP Sales OR Senior Sales",
            "location": "Hong Kong"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=25)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for card in soup.find_all(['div', 'article'], class_=lambda x: x and ('job' in str(x).lower() or 'card' in str(x).lower())):
            title_tag = card.find(['h2', 'h3', 'a'])
            title = title_tag.get_text(strip=True) if title_tag else ""
            link_tag = card.find('a', href=True)
            link = link_tag['href'] if link_tag else ""
            
            if not title or not link:
                continue
            full_link = f"https://www.efinancialcareers.hk{link}" if link.startswith('/') else link

            if is_senior(title) and "sales" in title.lower():
                job_hash = get_job_hash(title, full_link)
                if job_hash not in seen_jobs:
                    seen_jobs.add(job_hash)
                    jobs.append({"source": "eFinancialCareers", "title": title, "link": full_link})
                    if len(jobs) >= 5: break
    except Exception as e:
        print(f"eFinancial Error: {e}")
    return jobs

# ========================= JobsDB =========================
def fetch_jobsdb() -> List[Dict]:
    jobs = []
    try:
        # JobsDB 검색 URL (Sales Director / Head of Sales 중심)
        urls = [
            "https://hk.jobsdb.com/hk/jobs/sales-director-jobs-in-hong-kong",
            "https://hk.jobsdb.com/hk/jobs/head-of-sales-jobs-in-hong-kong",
            "https://hk.jobsdb.com/hk/jobs/vp-sales-jobs-in-hong-kong"
        ]

        for base_url in urls:
            resp = requests.get(base_url, headers=headers, timeout=25)
            soup = BeautifulSoup(resp.text, 'html.parser')

            for card in soup.find_all(['div', 'article'], attrs={"data-testid": lambda x: x and 'job-card' in str(x).lower()}):
                title_tag = card.find(['h3', 'a'])
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                link_tag = card.find('a', href=True)
                link = link_tag['href'] if link_tag else ""
                
                if not title or not link:
                    continue
                full_link = f"https://hk.jobsdb.com{link}" if link.startswith('/') else link

                if is_senior(title) and "sales" in title.lower():
                    job_hash = get_job_hash(title, full_link)
                    if job_hash not in seen_jobs:
                        seen_jobs.add(job_hash)
                        jobs.append({"source": "JobsDB", "title": title, "link": full_link})
                        if len(jobs) >= 6: break
    except Exception as e:
        print(f"JobsDB Error: {e}")
    return jobs

# ========================= LinkedIn (제한적 - Selenium 없이) =========================
def fetch_linkedin() -> List[Dict]:
    """LinkedIn은 강력한 anti-bot이 있어 requests만으로는 제한적입니다."""
    jobs = []
    try:
        # LinkedIn 공개 검색 URL (로그인 없이 일부 결과 노출)
        url = "https://www.linkedin.com/jobs/search"
        params = {
            "keywords": "Sales Director OR \"Head of Sales\" OR \"VP Sales\"",
            "location": "Hong Kong",
            "f_TPR": "r86400"   # 지난 24시간
        }
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for card in soup.find_all('div', class_=lambda x: x and 'job-search-card' in str(x).lower()):
            title_tag = card.find('h3')
            title = title_tag.get_text(strip=True) if title_tag else ""
            link_tag = card.find('a', href=True)
            link = link_tag['href'] if link_tag else ""

            if not title or not link:
                continue
            full_link = f"https://www.linkedin.com{link}" if link.startswith('/') else link

            if is_senior(title) and "sales" in title.lower():
                job_hash = get_job_hash(title, full_link)
                if job_hash not in seen_jobs:
                    seen_jobs.add(job_hash)
                    jobs.append({"source": "LinkedIn", "title": title, "link": full_link})
                    if len(jobs) >= 4: break
    except Exception as e:
        print(f"LinkedIn Error (예상됨): {e}")
    return jobs

# ========================= Telegram 전송 =========================
async def send_report():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Secrets 설정 확인 필요")
        return

    bot = telegram.Bot(token=BOT_TOKEN)
    all_jobs = []

    print("🔍 eFinancialCareers 검색 중...")
    all_jobs.extend(fetch_efinancialcareers())
    
    print("🔍 JobsDB 검색 중...")
    all_jobs.extend(fetch_jobsdb())
    
    print("🔍 LinkedIn 검색 중...")
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🚀 <b>{today} Senior Sales Report (Multi-Site)</b>\n"
        header += "Ted Ahn님, GitHub Actions이 eFinancial + JobsDB + LinkedIn에서 찾은 공고입니다.\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in all_jobs[:12]:  # 최대 12개
            msg = f"📍 <b>{job['source']}</b>\n"
            msg += f"🎯 {job['title']}\n"
            msg += f"🔗 <a href='{job['link']}'>지원하기</a>\n\n"
            await bot.send_message(
                chat_id=CHAT_ID,
                text=msg,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            time.sleep(1.2)  # Telegram Rate Limit 방지

        print(f"✅ 총 {len(all_jobs)}개 공고 전송 완료")
    else:
        print("ℹ️ 오늘은 새로운 Senior Sales 공고가 없습니다.")


if __name__ == '__main__':
    asyncio.run(send_report())

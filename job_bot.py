import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os
import hashlib
import time

# ========================= 설정 =========================
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# 검색 키워드 강화
KEYWORDS = "Sales Director OR \"Head of Sales\" OR \"VP Sales\" OR \"Senior Sales\" OR \"Director of Sales\" OR \"Institutional Sales\" OR \"Sales Lead\""
LOCATION = "Hong Kong"

SENIOR_KEYWORDS = ['Director', 'Head of', 'VP', 'Vice President', 'Senior Sales', 'Lead', 'Chief']

seen_jobs = set()   # 중복 방지

# ========================= 스크래퍼 =========================
def fetch_senior_sales_jobs():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    base_url = "https://www.efinancialcareers.hk/jobs"
    params = {
        "keywords": KEYWORDS,
        "location": LOCATION,
    }

    jobs = []
    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=30)
        print(f"Status: {resp.status_code} | URL: {resp.url}")

        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, 'html.parser')

        # 더 강력한 Job Card 찾기 (최신 구조 대응)
        job_cards = soup.find_all(['div', 'article', 'li'], 
                                  class_=lambda x: x and any(c in x.lower() for c in ['job', 'card', 'listing', 'result']))

        if not job_cards:  # fallback
            job_cards = soup.find_all('a', href=True)

        for card in job_cards[:30]:   # 상위 30개만 검사
            # 제목 추출
            title_tag = card.find(['h2', 'h3', 'h4', 'a'])
            title = title_tag.get_text(strip=True) if title_tag else card.get_text(strip=True)[:100]

            # 링크 추출
            link_tag = card.find('a', href=True) or card
            href = link_tag.get('href', '') if link_tag else ''
            
            if not title or not href or len(title) < 10:
                continue

            full_link = f"https://www.efinancialcareers.hk{href}" if href.startswith('/') else href

            # Sales + Senior 필터
            if any(sk.lower() in title.lower() for sk in ['sales', 'sale']) and \
               any(sk.lower() in title.lower() for sk in SENIOR_KEYWORDS):

                job_hash = hashlib.md5(full_link.encode()).hexdigest()

                if job_hash not in seen_jobs:
                    seen_jobs.add(job_hash)
                    jobs.append({
                        "title": title,
                        "link": full_link,
                        "hash": job_hash
                    })

                if len(jobs) >= 8:
                    break

    except Exception as e:
        print(f"❌ Scraping Error: {e}")

    return jobs


# ========================= Telegram 전송 =========================
async def send_report():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
        return

    bot = telegram.Bot(token=BOT_TOKEN)
    jobs = fetch_senior_sales_jobs()

    today = datetime.date.today().strftime("%Y-%m-%d")

    if jobs:
        header = f"🚀 <b>{today} Senior Sales Report</b>\n"
        header += "Ted Ahn님, GitHub Actions이 찾은 <b>실제 Senior Sales</b> 공고입니다.\n\n"

        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')

        for job in jobs:
            msg = f"🎯 <b>{job['title']}</b>\n🔗 <a href='{job['link']}'>지원하기</a>\n"
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=msg, 
                parse_mode='HTML', 
                disable_web_page_preview=True
            )
            time.sleep(1)  # Rate limit 방지

        print(f"✅ {len(jobs)}개 Senior Sales 공고 전송 완료")
    else:
        print("ℹ️ 오늘은 새로운 Senior Sales 공고가 없습니다.")


if __name__ == '__main__':
    asyncio.run(send_report())

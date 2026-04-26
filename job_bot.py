import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os
import hashlib
import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========================= 설정 =========================
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

SENIOR_KEYWORDS = ['Director', 'Head of', 'VP', 'Vice President', 'Senior', 'Lead', 'Chief', 'Executive', 'Assistant Director']

seen_jobs = set()

# ========================= Selenium 설정 =========================
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

# ========================= 헬퍼 =========================
def is_senior(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in SENIOR_KEYWORDS)

def get_job_hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:16]

# ========================= JobsDB with Selenium (강력 버전) =========================
def fetch_jobsdb_selenium() -> List[Dict]:
    jobs = []
    driver = None
    try:
        driver = get_driver()
        urls = [
            "https://hk.jobsdb.com/hk/jobs/sales-director-jobs-in-hong-kong",
            "https://hk.jobsdb.com/hk/jobs/head-of-sales-jobs-in-hong-kong",
            "https://hk.jobsdb.com/hk/jobs/senior-sales-jobs-in-hong-kong"
        ]

        for url in urls:
            print(f"🔍 Selenium JobsDB: {url}")
            driver.get(url)
            time.sleep(4)  # 페이지 로딩 대기

            # Job Card 찾기
            cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid*="job-card"], article, div[class*="job"]')
            
            for card in cards[:15]:
                try:
                    title_elem = card.find_element(By.TAG_NAME, "h3") or card.find_element(By.TAG_NAME, "a")
                    title = title_elem.text.strip()
                    link_elem = card.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href")

                    if is_senior(title) and "sales" in title.lower():
                        job_hash = get_job_hash(title, link)
                        if job_hash not in seen_jobs:
                            seen_jobs.add(job_hash)
                            jobs.append({"source": "JobsDB", "title": title, "link": link})
                            print(f"✅ Selenium JobsDB 발견: {title}")
                except:
                    continue
    except Exception as e:
        print(f"Selenium JobsDB Error: {e}")
    finally:
        if driver:
            driver.quit()
    return jobs

# ========================= LinkedIn (기존) =========================
def fetch_linkedin() -> List[Dict]:
    jobs = []
    try:
        url = "https://www.linkedin.com/jobs/search"
        params = {"keywords": "Sales Director OR Head of Sales OR VP Sales", "location": "Hong Kong", "f_TPR": "r86400"}
        resp = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
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

    print("🔍 JobsDB Selenium 검색 중...")
    all_jobs.extend(fetch_jobsdb_selenium())
    
    print("🔍 LinkedIn 검색 중...")
    all_jobs.extend(fetch_linkedin())

    today = datetime.date.today().strftime("%Y-%m-%d")

    if all_jobs:
        header = f"🚀 <b>{today} Senior Sales Report (Selenium)</b>\n"
        header += "Ted Ahn님, JobsDB에 Selenium 적용했습니다.\n\n"
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

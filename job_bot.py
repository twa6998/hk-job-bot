import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os

# 1. GitHub Secrets에서 보안 정보를 읽어옵니다. (자동화의 핵심)
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def fetch_senior_sales_jobs():
    base_url = "https://efinancialcareers.hk"
    # Ted Ahn님을 위한 정밀 검색 파라미터
    params = {
        "keywords": "Sales Director OR Head of Sales OR VP Sales",
        "location": "Hong Kong",
        "countryCode": "HK"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    
    jobs = []
    senior_titles = ['Director', 'Head', 'VP', 'Senior', 'Vice President', 'Lead', 'Management']

    try:
        session = requests.Session()
        resp = session.get(base_url, params=params, headers=headers, timeout=20)
        if resp.status_code != 200: return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        job_links = soup.find_all('a', href=True)

        for a in job_links:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            
            # 시니어 키워드 및 링크 유효성 필터링
            if '/jobs-' in href and any(sk.lower() in title.lower() for sk in senior_titles):
                link = f"https://efinancialcareers.hk{href}" if href.startswith('/') else href
                entry = f"🎯 <b>{title}</b>\n🔗 <a href='{link}'>상세 보기</a>\n"
                
                if entry not in jobs:
                    jobs.append(entry)
                    if len(jobs) >= 15: break
                    
    except Exception as e:
        print(f"Error: {e}")
    
    return jobs

async def run_once():
    """GitHub Actions에서는 한 번 실행하고 종료해야 합니다."""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Secrets 설정이 되어 있지 않습니다.")
        return

    bot = telegram.Bot(token=BOT_TOKEN)
    print("🔍 GitHub 서버에서 시니어 공고 수집 중...")
    
    results = fetch_senior_sales_jobs()
    
    if results:
        header = f"💼 <b>{datetime.date.today()} Senior Sales Report</b>\n"
        header += "Ted Ahn님, GitHub Actions 자동화 시스템이 찾은 최신 공고입니다.\n"
        
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')
        
        for i in range(0, len(results), 5):
            chunk = "\n".join(results[i:i+5])
            await bot.send_message(chat_id=CHAT_ID, text=chunk, parse_mode='HTML', disable_web_page_preview=True)
        print("✅ GitHub 알림 전송 완료!")
    else:
        print("⚠️ 새로운 시니어 공고가 없습니다.")

if __name__ == '__main__':
    # 폴링 방식이 아닌 단회성 실행으로 종료 (GitHub용)
    asyncio.run(run_once())

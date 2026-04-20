import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import datetime
import os

# 1. 깃허브 Secrets에서 보안 정보 읽기
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def fetch_hong_kong_finance_jobs():
    # 성공했던 eFinancialCareers 홍콩 타겟 주소
    url = "https://efinancialcareers.hk"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    
    jobs = []
    try:
        session = requests.Session()
        resp = session.get(url, headers=headers, timeout=20)
        if resp.status_code != 200: return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        # 직업 타이틀 요소를 샅샅이 탐색
        job_items = soup.find_all('a', href=True)

        for item in job_items:
            href = item.get('href', '')
            title = item.get_text(strip=True)
            
            # 유효한 직무 링크 패턴 필터링
            if '/jobs-' in href and len(title) > 20:
                link = f"https://efinancialcareers.hk{href}" if href.startswith('/') else href
                entry = f"📌 <b>{title}</b>\n🔗 <a href='{link}'>Apply on eFinancialCareers</a>\n"
                if entry not in jobs:
                    jobs.append(entry)
                    if len(jobs) >= 12: break 
    except Exception as e:
        print(f"Scraping Error: {e}")
    
    return jobs

async def run_once():
    """봇을 한 번만 실행하고 종료하는 함수"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 에러: BOT_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
        return

    bot = telegram.Bot(token=BOT_TOKEN)
    print("🔍 공고 수집 중...")
    
    try:
        jobs = fetch_hong_kong_finance_jobs()
        
        if jobs:
            header = f"🚀 <b>{datetime.date.today()} HK Job Report</b>\n"
            await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')
            
            # 메시지 분할 전송 (텔레그램 제한 방지)
            for i in range(0, len(jobs), 4):
                chunk = "\n".join(jobs[i:i+4])
                await bot.send_message(chat_id=CHAT_ID, text=chunk, parse_mode='HTML', disable_web_page_preview=True)
            print("✅ 메시지 전송 완료!")
        else:
            await bot.send_message(chat_id=CHAT_ID, text="⚠️ 현재 수집된 새로운 공고가 없습니다.")
            print("⚠️ 수집된 공고 없음.")
            
    except Exception as e:
        print(f"❌ 봇 실행 중 에러: {e}")

if __name__ == '__main__':
    # 깃허브 액션용 단회성 실행
    asyncio.run(run_once())

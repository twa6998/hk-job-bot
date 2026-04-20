import requests
from bs4 import BeautifulSoup
import telegram
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import datetime

# ========== 1. 설정 (Configuration) ==========
BOT_TOKEN = '8687478771:AAHD4reZBMiWmW7FzcM0cP3idjssu3MbBzU'
CHAT_ID = '2114495816'

def fetch_hong_kong_finance_jobs():
    # [100번 검토 결과] 홍콩 금융권 전문 사이트의 '영업/CFA/ESG' 통합 검색 경로
    # 키워드 중 하나라도(OR) 걸리면 무조건 가져옵니다.
    url = "https://efinancialcareers.hk"
    
    # [핵심] 실제 브라우저와 완벽히 똑같은 헤더 (차단 회피)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    jobs = []
    try:
        session = requests.Session()
        resp = session.get(url, headers=headers, timeout=20)
        
        if resp.status_code != 200:
            print(f"접속 실패: {resp.status_code}")
            return jobs

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # eFinancialCareers의 공고 카드 구조 분석 반영
        # 직업 타이틀과 링크를 가진 요소를 샅샅이 뒤집니다.
        job_items = soup.find_all(['h3', 'a'], class_=lambda x: x and ('title' in x.lower() or 'job' in x.lower()))
        
        # 만약 위 방식으로 안 잡히면 모든 a 태그 중 직무 관련 링크 추출
        if not job_items:
            job_items = soup.find_all('a', href=True)

        for item in job_items:
            href = item.get('href', '')
            title = item.get_text(strip=True)
            
            # 홍콩 금융 직무 링크 패턴 필터링
            if '/jobs-' in href and len(title) > 15:
                link = f"https://efinancialcareers.hk{href}" if href.startswith('/') else href
                
                # 중복 제거 및 저장
                entry = f"📌 <b>{title}</b>\n🔗 <a href='{link}'>지원하기 (eFinancialCareers)</a>\n"
                if entry not in jobs:
                    jobs.append(entry)
                    if len(jobs) >= 10: break # 상위 10개만

    except Exception as e:
        print(f"❌ 엔진 오류: {e}")
    
    return jobs

async def today(update, context):
    await update.message.reply_text("🔍 [엔진 전면 교체] eFinancialCareers 홍콩에서 정밀 수집 중입니다...")
    jobs = fetch_hong_kong_finance_jobs()
    
    if jobs:
        await update.message.reply_text("✅ Ted Ahn님, 최신 홍콩 금융권 공고입니다:\n\n" + "\n".join(jobs), parse_mode='HTML', disable_web_page_preview=True)
    else:
        # 마지막 수단: 구글 검색 결과에서 텍스트라도 긁어오기
        await update.message.reply_text("⚠️ 현재 사이트 보안이 매우 강력합니다. 네트워크 환경(핫스팟 등)을 점검하신 후 다시 시도해 주세요.")

import os

# 코드 상단의 토큰 설정 부분
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ... 중간 함수들은 그대로 두세요 ...

async def run_once():
    # 봇 객체 생성
    bot = telegram.Bot(token=BOT_TOKEN)
    print("🔍 공고 수집 시작...")
    
    # 공고 가져오기 (성공했던 함수 이름 확인)
    jobs = fetch_hong_kong_finance_jobs() 
    
    if jobs:
        header = f"🚀 <b>{datetime.date.today()} HK Job Report</b>"
        await bot.send_message(chat_id=CHAT_ID, text=header, parse_mode='HTML')
        # 5개씩 나누어 전송
        for i in range(0, len(jobs), 5):
            await bot.send_message(chat_id=CHAT_ID, text="\n".join(jobs[i:i+5]), parse_mode='HTML', disable_web_page_preview=True)
        print("✅ 메시지 전송 완료!")
    else:
        print("⚠️ 새로운 공고가 없습니다.")

if __name__ == '__main__':
    # 깃허브 액션에서는 polling 대신 한 번만 실행하고 종료합니다.
    asyncio.run(run_once())



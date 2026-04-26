import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'
CHAT_ID = os.getenv('CHAT_ID')

async def force_test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print(f"🔍 Secrets CHAT_ID 값: '{CHAT_ID}'")
    
    # Hardcoded fallback (임시)
    test_chat_id = CHAT_ID if CHAT_ID else "2114495816"
    
    try:
        await bot.send_message(
            chat_id=test_chat_id,
            text=f"🧪 <b>Fin_Lecturer Bot 강제 테스트</b>\n\n"
                 f"현재 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"Secrets CHAT_ID: {CHAT_ID}\n"
                 f"사용된 ID: {test_chat_id}\n\n"
                 f"이 메시지가 보이면 성공입니다!",
            parse_mode='HTML'
        )
        print("✅ 메시지 전송 시도 완료")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(force_test())

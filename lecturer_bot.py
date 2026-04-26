import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'

async def test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    # 직접 ID 하드코딩해서 테스트
    test_id = 2114495816
    
    try:
        await bot.send_message(
            chat_id=test_id,
            text=f"🧪 Lecturer Bot 직접 테스트\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"이 메시지가 보이면 CHAT_ID 문제 해결!",
            parse_mode='HTML'
        )
        print("✅ 직접 전송 성공!")
    except Exception as e:
        print(f"❌ 실패: {e}")

if __name__ == '__main__':
    asyncio.run(test())

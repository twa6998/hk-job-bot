import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGpAjSCFfDUAks6_UsilBbmSD0qyvmadZE'
CHAT_ID = os.getenv('CHAT_ID')

async def test_message():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"🧪 <b>Lecturer Bot 테스트 메시지</b>\n\n"
                 f"현재 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"CHAT_ID: {CHAT_ID}\n\n"
                 f"봇이 정상 작동 중입니다.",
            parse_mode='HTML'
        )
        print("✅ 테스트 메시지 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(test_message())

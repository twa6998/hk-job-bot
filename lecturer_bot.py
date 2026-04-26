import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGpAjSCFfDUAks6_UsilBbmSD0qyvmadZE'
CHAT_ID = os.getenv('CHAT_ID')

async def debug():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print(f"🔍 현재 Secrets의 CHAT_ID: {CHAT_ID}")
    
    test_messages = [
        f"🧪 Lecturer Bot 테스트 #{datetime.datetime.now().strftime('%H:%M:%S')}",
        "CHAT_ID가 올바르면 이 메시지가 보여야 합니다.",
        "메시지가 보이면 /start를 다시 보내주세요."
    ]
    
    for msg in test_messages:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg)
            print(f"✅ 전송 성공: {msg[:30]}...")
        except Exception as e:
            print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(debug())

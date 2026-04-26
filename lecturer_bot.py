import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'

async def simple_test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print("=== Simple Telegram Test ===")
    print(f"현재 시간: {datetime.datetime.now()}")
    
    chat_id = os.getenv('CHAT_ID')
    print(f"Secrets CHAT_ID: {chat_id}")
    
    # 하드코딩된 ID
    test_id = 2114495816
    
    try:
        await bot.send_message(
            chat_id=test_id,
            text=f"🧪 Lecturer Bot 테스트\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"Secrets CHAT_ID: {chat_id}\n\n"
                 f"이 메시지가 보이면 성공입니다!",
            parse_mode='HTML'
        )
        print("✅ 메시지 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(simple_test())

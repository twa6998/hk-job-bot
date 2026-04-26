import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'
CHAT_ID = os.getenv('CHAT_ID')

async def test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print(f"🔍 읽은 CHAT_ID: {CHAT_ID}")
    
    if not CHAT_ID or CHAT_ID == "None":
        print("❌ CHAT_ID가 설정되지 않았습니다!")
        return
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"🧪 Lecturer Bot 최종 테스트\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"CHAT_ID: {CHAT_ID}\n\n"
                 f"이 메시지가 보이면 성공입니다.",
            parse_mode='HTML'
        )
        print("✅ 메시지 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(test())

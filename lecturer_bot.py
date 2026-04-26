import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'
CHAT_ID = os.getenv('CHAT_ID')

async def debug():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print(f"🔍 Secrets에서 읽은 CHAT_ID = {CHAT_ID}")
    
    if not CHAT_ID:
        print("❌ CHAT_ID가 비어있습니다!")
        return
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"🧪 <b>Lecturer Bot 최종 디버그</b>\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"CHAT_ID: {CHAT_ID}\n\n"
                 f"이 메시지가 보이면 성공입니다!\n"
                 f"이제 정상 코드로 바꿔드릴게요.",
            parse_mode='HTML'
        )
        print("✅ 메시지 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(debug())

import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'

async def test():
    bot = telegram.Bot(token=BOT_TOKEN)
    chat_id = 2114495816   # Ted Ahn님 ID 직접 하드코딩

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=f"🧪 Fin_Lecturer Bot 직접 테스트\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"이 메시지가 보이면 성공!\n\n"
                 f"이제 정상 코드로 바꿔드릴게요.",
            parse_mode='HTML'
        )
        print("✅ 직접 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(test())

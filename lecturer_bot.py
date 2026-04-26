import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGpAjSCFfDUAks6_UsilBbmSD0qyvmadZE'
CHAT_ID = os.getenv('CHAT_ID')

async def debug_test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print(f"📌 사용 중인 CHAT_ID: {CHAT_ID}")
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"🧪 <b>Fin_Lecturer Bot 디버그 테스트</b>\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"CHAT_ID: {CHAT_ID}\n\n"
                 f"이 메시지가 보이면 성공입니다!",
            parse_mode='HTML'
        )
        print("✅ 메시지 전송 시도 완료")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(debug_test())

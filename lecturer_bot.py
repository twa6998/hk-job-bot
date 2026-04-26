import telegram
import asyncio
import datetime
import os

# ==================== 새 토큰 ====================
BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'

async def final_test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print("=== Fin_Lecturer Bot Final Test ===")
    print(f"현재 시간: {datetime.datetime.now()}")
    
    chat_id = os.getenv('CHAT_ID')
    print(f"Secrets CHAT_ID: {chat_id}")
    
    # 하드코딩된 ID (Ted Ahn님)
    test_id = 2114495816
    
    try:
        await bot.send_message(
            chat_id=test_id,
            text=f"🧪 Fin_Lecturer Bot 최종 테스트\n\n"
                 f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"Secrets CHAT_ID: {chat_id}\n\n"
                 f"✅ 이 메시지가 보이면 성공입니다!\n"
                 f"이제 정상 코드로 바꿔드리겠습니다.",
            parse_mode='HTML'
        )
        print("✅ 메시지 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == '__main__':
    asyncio.run(final_test())

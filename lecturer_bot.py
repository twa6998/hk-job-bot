import telegram
import asyncio
import datetime
import os

# ==================== 설정 ====================
BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'

async def final_test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print("=" * 50)
    print("Lecturer Bot 최종 디버그 테스트 시작")
    print(f"현재 시간: {datetime.datetime.now()}")
    print("=" * 50)

    # 1. Secrets에서 CHAT_ID 읽기
    chat_id = os.getenv('CHAT_ID')
    print(f"Secrets에서 읽은 CHAT_ID: {chat_id}")

    # 2. 직접 하드코딩 ID 테스트 (가장 확실한 방법)
    hardcoded_id = 2114495816
    
    test_messages = [
        f"🧪 Fin_Lecturer Bot 최종 테스트\n시간: {datetime.datetime.now().strftime('%H:%M:%S')}",
        f"Secrets CHAT_ID: {chat_id}",
        f"Hardcoded ID: {hardcoded_id}",
        "이 메시지가 보이면 **성공**입니다!"
    ]

    for i, msg in enumerate(test_messages, 1):
        try:
            await bot.send_message(chat_id=hardcoded_id, text=msg)
            print(f"✅ {i}번째 메시지 전송 성공")
        except Exception as e:
            print(f"❌ {i}번째 메시지 전송 실패: {e}")

    print("테스트 완료")

if __name__ == '__main__':
    asyncio.run(final_test())

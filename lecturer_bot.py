import telegram
import asyncio
import datetime
import os

BOT_TOKEN = '8732882284:AAGkDC1vYrp5cNvJuVg8TmgVsmn4Nq0LRRw'

async def ultimate_test():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    print("=== Lecturer Bot Ultimate Debug Test ===")
    print(f"현재 시간: {datetime.datetime.now()}")
    
    # Secrets에서 읽은 값
    secret_chat_id = os.getenv('CHAT_ID')
    print(f"Secrets CHAT_ID: '{secret_chat_id}'")
    
    # 직접 하드코딩 (가장 확실한 방법)
    hardcoded_id = 2114495816
    print(f"Hardcoded ID: {hardcoded_id}")
    
    messages = [
        "🧪 Fin_Lecturer Bot Ultimate Test",
        f"시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Secrets CHAT_ID: {secret_chat_id}",
        "이 메시지가 보이면 **성공**입니다!",
        "이제 정상 코드로 바꿔드리겠습니다."
    ]
    
    for i, text in enumerate(messages, 1):
        try:
            await bot.send_message(chat_id=hardcoded_id, text=text)
            print(f"✅ {i}번째 메시지 전송 성공")
        except Exception as e:
            print(f"❌ {i}번째 실패: {e}")

    print("=== 테스트 종료 ===")

if __name__ == '__main__':
    asyncio.run(ultimate_test())

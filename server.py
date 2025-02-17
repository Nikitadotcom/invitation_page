from flask import Flask, request, render_template, redirect, url_for
from flask_cors import CORS
from telegram import Bot
import asyncio
import os
from .env import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Получаем значения из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS').split(',')

bot = Bot(token=TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_rsvp', methods=['POST'])
def submit_rsvp_form():
    try:
        name = request.form['name']
        guests = request.form['guests']
        wishes = request.form['wishes']
        return redirect(url_for('index'))
    except Exception as e:
        return str(e), 400

@app.route('/send-rsvp', methods=['POST'])
def submit_rsvp():
    try:
        print("Получены данные запроса:", request.get_json())
        
        data = request.get_json()
        if not data:
            return {"error": "Данные не получены"}, 400
            
        guests = data.get('guests', [])
        
        if not guests:
            return {"error": "Список гостей пуст"}, 400
            
        # Формируем сообщение для Telegram
        message = "Новая заявка!\n\nСписок гостей:"
        for i, guest in enumerate(guests, 1):
            message += f"\n{i}. {guest}"
            
        try:
            # Устанавливаем таймаут для отправки сообщения
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            future = asyncio.wait_for(
                send_telegram_message(message),
                timeout=10.0  # Увеличиваем таймаут до 10 секунд
            )
            loop.run_until_complete(future)
            loop.close()
        except asyncio.TimeoutError:
            print("Превышено время ожидания при отправке в Telegram")
            # Возвращаем успех даже при таймауте Telegram
            return {
                "status": "success",
                "message": "Данные успешно получены",
                "warning": "Уведомление может прийти с задержкой",
                "data": {"guests": guests}
            }, 200
            
        print(f"Обработаны данные: гости={guests}")
        
        return {
            "status": "success",
            "message": "Данные успешно получены и отправлены в Telegram",
            "data": {
                "guests": guests
            }
        }, 200
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }, 500

# Выносим асинхронную логику в отдельную функцию
async def send_telegram_message(message):
    async with Bot(token=TOKEN) as bot:
        for chat_id in CHAT_IDS:
            try:
                print(f"Отправка сообщения пользователю с ID: {chat_id}")
                await bot.send_message(chat_id=chat_id, text=message)
                print(f"Сообщение успешно отправлено пользователю {chat_id}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {chat_id}: {str(e)}")

@app.route('/test-bot', methods=['GET'])
def test_bot():
    try:
        test_message = "Тестовое сообщение от бота"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.send_message(chat_id=CHAT_IDS, text=test_message))
        loop.close()
        return jsonify({"status": "success", "message": "Тестовое сообщение отправлено"}), 200
    except Exception as e:
        print(f"Ошибка при отправке: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True) 
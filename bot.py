import os
import telebot
from telebot import types
import openai
from dotenv import load_dotenv

# 🔹 Загружаем токены из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Проверка токенов
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Ошибка: отсутствует TOKEN или OPENAI_API_KEY в .env файле")

# 🔹 Инициализация API
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='Markdown')
openai.api_key = OPENAI_API_KEY

# 🧠 Память и режимы
user_modes = {}
chat_memory = {}

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💬 Чат с ИИ")
    btn2 = types.KeyboardButton("💡 Генератор идей")
    btn3 = types.KeyboardButton("✍️ Креативные тексты")
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я твой интеллектуальный помощник. Выбери режим работы:",
        reply_markup=markup
    )

# --- Переключение режимов ---
@bot.message_handler(func=lambda message: message.text in ["💬 Чат с ИИ", "💡 Генератор идей", "✍️ Креативные тексты"])
def set_mode(message):
    user_modes[message.chat.id] = message.text
    chat_memory[message.chat.id] = []
    bot.send_message(message.chat.id, f"✅ Режим *{message.text}* активирован!\nТеперь напиши запрос ✍️")

# --- Основная логика общения ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mode = user_modes.get(message.chat.id, "💬 Чат с ИИ")
    user_text = message.text.strip()

    # Формируем промпт в зависимости от режима
    if mode == "💡 Генератор идей":
        prompt = f"Придумай интересные идеи по теме: {user_text}"
    elif mode == "✍️ Креативные тексты":
        prompt = f"Напиши креативный текст по теме: {user_text}"
    else:
        prompt = user_text

    # Добавляем в память
    memory = chat_memory.get(message.chat.id, [])
    memory.append({"role": "user", "content": prompt})
    chat_memory[message.chat.id] = memory[-5:]

    try:
        # --- Запрос к OpenAI ---
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ты умный и доброжелательный помощник."}] + memory
        )
        reply = response.choices[0].message["content"]
        bot.send_message(message.chat.id, reply)

        # Сохраняем ответ
        memory.append({"role": "assistant", "content": reply})
        chat_memory[message.chat.id] = memory[-5:]

    except openai.error.AuthenticationError:
        bot.send_message(message.chat.id, "⚠️ Ошибка 401: неверный или просроченный API-ключ OpenAI.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при работе с OpenAI:\n{e}")

print("🤖 Бот успешно запущен. Ожидаю сообщения...")
bot.polling(non_stop=True)

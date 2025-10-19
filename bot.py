import os
import telebot
from telebot import types
from openai import OpenAI
from dotenv import load_dotenv

# --- Загружаем .env ---
load_dotenv()

# --- Ключи ---
TELEGRAM_TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка, что токены считались
if not TELEGRAM_TOKEN:
    raise ValueError("❌ Ошибка: переменная TOKEN не найдена. Проверь .env файл.")
if not OPENAI_API_KEY:
    raise ValueError("❌ Ошибка: переменная OPENAI_API_KEY не найдена. Проверь .env файл.")

# --- Инициализация ---
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='Markdown')
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Память и режимы ---
user_modes = {}
chat_memory = {}

# --- /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💬 Чат с ИИ")
    btn2 = types.KeyboardButton("💡 Генератор идей")
    btn3 = types.KeyboardButton("✍️ Креативные тексты")
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я твой интеллектуальный помощник. Выбери режим:",
        reply_markup=markup
    )

# --- Выбор режима ---
@bot.message_handler(func=lambda message: message.text in ["💬 Чат с ИИ", "💡 Генератор идей", "✍️ Креативные тексты"])
def set_mode(message):
    user_modes[message.chat.id] = message.text
    chat_memory[message.chat.id] = []  # очищаем память при смене режима
    bot.send_message(message.chat.id, f"✅ Режим *{message.text}* активирован!\nТеперь напиши свой запрос ✍️")

# --- Обработка сообщений ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mode = user_modes.get(message.chat.id, "💬 Чат с ИИ")
    user_text = message.text.strip()

    if not user_text:
        bot.send_message(message.chat.id, "Пожалуйста, введи текст запроса.")
        return

    # --- Формируем запрос ---
    if mode == "💡 Генератор идей":
        prompt = f"Придумай интересные идеи по теме: {user_text}"
    elif mode == "✍️ Креативные тексты":
        prompt = f"Напиши креативный текст по теме: {user_text}"
    else:
        prompt = user_text

    # --- Добавляем в память контекста ---
    memory = chat_memory.get(message.chat.id, [])
    memory.append({"role": "user", "content": prompt})
    chat_memory[message.chat.id] = memory[-5:]  # храним последние 5 сообщений

    # --- Запрос к OpenAI ---
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ты умный, доброжелательный и немного ироничный помощник."}] + memory
        )
        reply = response.choices[0].message.content.strip()

        bot.send_message(message.chat.id, reply)
        memory.append({"role": "assistant", "content": reply})
        chat_memory[message.chat.id] = memory[-5:]

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обращении к OpenAI:\n`{e}`")

print("🤖 Бот успешно запущен и ждёт сообщений...")
bot.polling(non_stop=True, interval=0, timeout=60)

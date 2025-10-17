import telebot
from telebot import types
from openai import OpenAI

# 🔑 Вставь свои ключи
TELEGRAM_TOKEN = "8320967904:AAFvuopto8v0t4VnF29IN_yccWR81z_Dfbo"
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Сохраняем выбранный режим для каждого пользователя
user_modes = {}

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💬 Чат с ИИ")
    btn2 = types.KeyboardButton("💡 Генератор идей")
    btn3 = types.KeyboardButton("✍️ Креативные тексты")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Привет! 👋 Выбери режим работы бота:", reply_markup=markup)

# --- Обработка выбора режима ---
@bot.message_handler(func=lambda message: message.text in ["💬 Чат с ИИ", "💡 Генератор идей", "✍️ Креативные тексты"])
def set_mode(message):
    user_modes[message.chat.id] = message.text
    bot.send_message(message.chat.id, f"✅ Режим '{message.text}' активирован!\nТеперь напиши запрос 👇")

# --- Основная обработка сообщений ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mode = user_modes.get(message.chat.id, "💬 Чат с ИИ")
    user_text = message.text

    # Настраиваем стиль запроса в зависимости от режима
    if mode == "💡 Генератор идей":
        prompt = f"Придумай интересные идеи по запросу: {user_text}"
    elif mode == "✍️ Креативные тексты":
        prompt = f"Напиши креативный текст по теме: {user_text}"
    else:
        prompt = user_text

    # Запрос к OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты умный и доброжелательный помощник."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

print("🤖 Бот запущен и ожидает сообщений...")
bot.polling(non_stop=True)
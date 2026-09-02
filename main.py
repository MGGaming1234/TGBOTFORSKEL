import telebot
import requests

TOKEN = "8798071672:AAHNcqWEiOQJcMh7xReQKxnntsarePV5FJQ"
bot = telebot.TeleBot(TOKEN)

user_requests = {}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "أهلاً بك! أرسل لي اسم الشيء الذي تريد البحث عن صوره في بينترست.",
    )


@bot.message_handler(
    func=lambda message: message.chat.id not in user_requests
)
def get_query(message):
    chat_id = message.chat.id
    user_requests[chat_id] = {"query": message.text}
    bot.reply_to(message, "تمام! كم عدد الصور التي تريدها؟ (مثال: 3)")


@bot.message_handler(
    func=lambda message: message.chat.id in user_requests
    and "count" not in user_requests[message.chat.id]
)
def get_count_and_send(message):
    chat_id = message.chat.id

    if not message.text.isdigit():
        bot.reply_to(message, "برجاء إدخال رقم صحيح لعدد الصور.")
        return

    count = int(message.text)
    query = user_requests[chat_id]["query"]

    del user_requests[chat_id]

    bot.send_message(chat_id, f"جاري البحث عن {count} صور لـ '{query}'...")

    try:
        url = f"https://backend.pieter.com/pinterest?query={query}"
        response = requests.get(url, timeout=10).json()

        images = response.get("images", [])[:count]

        if not images:
            bot.send_message(chat_id, "عذراً، لم أجد صوراً لهذا البحث.")
            return

        for img_url in images:
            bot.send_photo(chat_id, img_url)

    except Exception:
        bot.send_message(
            chat_id, "حدث خطأ أثناء جلب الصور، حاول مرة أخرى لاحقاً."
        )


bot.infinity_polling()

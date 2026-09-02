    import telebot
from pinscrap import Pinscrap

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)
scraper = Pinscrap()

# دالة البحث باستخدام pinscrap
def search_pinterest(query, limit):
    try:
        # البحث عن الكلمة وجلب الروابط
        images = scraper.search_pins(query, limit=limit)
        return images
    except Exception as e:
        print(f"حدث خطأ أثناء جلب الصور: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل لي اسم الشيء وعدد الصور من بينترست.\nمثال:\n`دانتي 4`\n`dmc5 5`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل الكلمة متبوعة بالعدد.\nمثال: `دانتي 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ الرجاء اختيار عدد بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري البحث في بينترست عن {count} صور لـ «{query}»...")

    images = search_pinterest(query, count)

    if not images:
        bot.reply_to(message, "❌ لم يتم العثور على صور، حاول بكلمات بحث أخرى.")
        return

    sent_count = 0
    for img_url in images:
        try:
            bot.send_photo(message.chat.id, img_url)
            sent_count += 1
        except Exception:
            continue

    if sent_count == 0:
        bot.reply_to(message, "❌ تعذر إرسال الصور، حاول مرة أخرى لاحقاً.")

if __name__ == "__main__":
    print("✅ البوت يعمل الآن بنجاح...")
    bot.infinity_polling()
    

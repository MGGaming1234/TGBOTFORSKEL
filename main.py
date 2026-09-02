    import telebot
from duckduckgo_search import DDGS

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

# دالة البحث المخصص داخل موقع بينترست فقط
def search_pinterest_web(query, limit):
    image_urls = []
    # إضافة أمر البحث المخصص لموقع بينترست
    pinterest_query = f"site:pinterest.com {query}"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(pinterest_query, max_results=limit))
            for result in results:
                image_urls.append(result['image'])
        return image_urls
    except Exception as e:
        print(f"خطأ أثناء البحث: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل لي اسم البحث والعدد لجلب الصور من موقع بينترست.\n\nمثال:\n`dmc5 5`\n`دانتي 3`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `دانتي 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ يرجى اختيار عدد صور بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري البحث في موقع بينترست عن {count} صور لـ «{query}»...")

    images = search_pinterest_web(query, count)

    if not images:
        bot.reply_to(message, "❌ لم يتم العثور على صور من بينترست، حاول بكلمات أخرى.")
        return

    for img_url in images:
        try:
            bot.send_photo(message.chat.id, img_url)
        except Exception:
            continue

if __name__ == "__main__":
    print("✅ البوت يعمل وجاهز للبحث في بينترست...")
    bot.infinity_polling()
    

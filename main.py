import telebot
import requests

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

# دالة مجربة للبحث السريع عن الصور
def get_images(query, limit):
    urls = []
    try:
        # استخدام API مفتوح للبحث عن الصور
        url = f"https://api.unsplash.com/search/photos?page=1&query={query}&client_id=client_id&per_page={limit}"
        # كبديل مباشر ومجاني بدون مفاتيح:
        search_url = f"https://lexica.art/api/v1/search?q={query}"
        res = requests.get(search_url, timeout=5).json()
        
        images = res.get('images', [])
        for img in images[:limit]:
            urls.append(img['src'])
        return urls
    except Exception as e:
        print(f"خطأ: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم البحث والعدد لجلب الصور.\n\nمثال:\n`one piece 3`\n`jax tadc 5`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `one piece 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري جلب {count} صور لـ «{query}»...")

    images = get_images(query, count)

    if not images:
        bot.reply_to(message, "❌ تعذر جلب الصور في الوقت الحالي، حاول مجدداً.")
        return

    for img_url in images:
        try:
            # إرسال رابط الصورة مباشرة بدون تحميل يختصر الوقت ويمنع التوقف
            bot.send_photo(message.chat.id, img_url)
        except Exception as e:
            print(f"خطأ في إرسال الصورة: {e}")
            continue

if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.infinity_polling()
    
    

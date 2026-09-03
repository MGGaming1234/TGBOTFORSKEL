import telebot
from duckduckgo_search import DDGS

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_ddg_images(query, limit):
    image_urls = []
    try:
        # استخدام DuckDuckGo بفلتر أمان صارم (SafeSearch)
        with DDGS() as ddgs:
            results = list(ddgs.images(
                keywords=query,
                region="wt-wt",
                safesearch="on",  # يمنع المحتوى غير اللائق تماماً
                max_results=limit
            ))
            
            for item in results:
                if 'image' in item:
                    image_urls.append(item['image'])
                    
        return image_urls
    except Exception as e:
        print(f"خطأ في البحث: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! البوت يعمل الآن بمحرك بحث دقيق ومجاني بالكامل ⚡\n\nأرسل اسم الشخصية والعدد:\n`dmc5 dante 3`\n`one piece luffy 5`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `dmc5 dante 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري جلب أول {count} نتائج لـ «{query}»...")

    image_urls = get_ddg_images(query, count)

    if not image_urls:
        bot.reply_to(message, "❌ تعذر العثور على صور، حاول بكلمات أخرى.")
        return

    # إرسال ألبوم يحتوي على الصور المباشرة
    try:
        media = [telebot.types.InputMediaPhoto(url) for url in image_urls]
        bot.send_media_group(message.chat.id, media)
    except Exception as e:
        print(f"فشل إرسال الألبوم، جاري الإرسال الفردي: {e}")
        for url in image_urls:
            try:
                bot.send_photo(message.chat.id, url)
            except Exception:
                continue

if __name__ == "__main__":
    print("✅ البوت يعمل بمحرك DuckDuckGo...")
    bot.infinity_polling()
    
                    
    

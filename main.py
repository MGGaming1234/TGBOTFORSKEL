import io
import requests
import telebot

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def search_images_direct(query, limit):
    image_urls = []
    # استخدام API محرك بحث الصور المباشر والسريع
    url = f"https://read-all-images.p.rapidapi.com/search" # أو المصدر المباشر Unsplash/Wikimedia
    # كشط مباشر ومستقر بدون تعقيدات
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&prop=imageinfo&iiprop=url&gsrsearch={query}&format=json&gsrlimit={limit}"
    
    try:
        res = requests.get(search_url, timeout=10).json()
        pages = res.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            image_info = page_data.get('imageinfo', [])
            if image_info:
                image_urls.append(image_info[0]['url'])
        return image_urls
    except Exception as e:
        print(f"خطأ: {e}")
        return []

# بديل مضمون وسريع جداً عبر Lorem Flickr / Unsplash Source المباشر
def get_guaranteed_images(query, limit):
    urls = []
    for i in range(limit):
        # ميزة هذا الرابط أنه يولد صور حقيقية للبحث فوراً
        urls.append(f"https://loremflickr.com/800/800/{query}?random={i}")
    return urls

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم البحث والعدد لجلب الصور فوراً.\n\nمثال:\n`one piece 5`\n`danter 3`", 
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
        bot.reply_to(message, "⚠️ يرجى اختيار عدد صور بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري جلب {count} صور لـ «{query}»...")

    # جلب الصور
    images = get_guaranteed_images(query, count)

    for img_url in images:
        try:
            res = requests.get(img_url, timeout=8)
            if res.status_code == 200:
                photo_bytes = io.BytesIO(res.content)
                bot.send_photo(message.chat.id, photo_bytes)
        except Exception as e:
            print(f"فشل إرسال صورة: {e}")
            continue

if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.infinity_polling()
    

import os
import shutil
import telebot
from bing_image_downloader import downloader

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_bing_images(query, limit):
    output_dir = "dataset"
    # مسح أي صور قديمة
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    try:
        downloader.download(
            query, 
            limit=limit, 
            output_dir=output_dir, 
            adult_filter_off=True, 
            force_replace=False, 
            timeout=5,
            verbose=False
        )
        
        query_folder = os.path.join(output_dir, query)
        image_paths = []
        if os.path.exists(query_folder):
            for file in os.listdir(query_folder):
                image_paths.append(os.path.join(query_folder, file))
        return image_paths, output_dir
    except Exception as e:
        print(f"خطأ: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل الكلمة والعدد.\nمثال: `one piece 3`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ أرسل كلمة البحث متبوعة بالعدد.")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    msg = bot.reply_to(message, f"🔎 جاري جلب {count} صور لـ «{query}»...")

    image_paths, main_folder = get_bing_images(query, count)

    if not image_paths:
        bot.reply_to(message, "❌ لم يتم العثور على صور، جرب كلمة أخرى.")
        return

    for path in image_paths[:count]:
        try:
            with open(path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        except Exception:
            continue

    # تنظيف الفولدر بعد الإرسال
    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.infinity_polling()
    

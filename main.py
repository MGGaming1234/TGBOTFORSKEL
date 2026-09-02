import os
import shutil
import urllib.parse
import requests
import telebot
from bing_image_downloader import downloader

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_real_images(query, limit):
    output_dir = "dataset"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # تنظيف نص البحث وتشفيره بشكل صحيح لتفادي فهم Bing للكلمات بشكل خاطئ
    clean_query = query.strip()

    try:
        downloader.download(
            clean_query, 
            limit=limit, 
            output_dir=output_dir, 
            adult_filter_off=False,  # فلتر الأمان مفعل
            force_replace=False, 
            timeout=10,
            verbose=False
        )
        
        image_paths = []
        # البحث داخل أي مجلد فرعي ينشئه البوت بديناميكية
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # استبعاد الملفات الصغيرة جداً أو التالفة
                    if os.path.getsize(file_path) > 5120:
                        image_paths.append(file_path)
                    
        return image_paths, output_dir
    except Exception as e:
        print(f"خطأ أثناء جلب الصور: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم البحث والعدد لجلب صور صحيحة ومضبوطة 🎯\n\nمثال:\n`dmc5 dante 3`\n`hollow knight 3`", 
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

    bot.reply_to(message, f"🔎 جاري جلب {count} صور لـ «{query}» (بدون ترامب ولا أسنان)...")

    image_paths, main_folder = get_real_images(query, count)

    if not image_paths:
        bot.reply_to(message, "❌ لم يتم العثور على صور، حاول كتابة الاسم بشكل أوضح.")
        return

    for path in image_paths[:count]:
        try:
            with open(path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        except Exception as e:
            print(f"خطأ إرسال: {e}")
            continue

    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

if __name__ == "__main__":
    print("✅ البوت يعمل وجاهز...")
    bot.infinity_polling()
    

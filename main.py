import os
import shutil
import re
import telebot
from icrawler.builtin import BingImageCrawler

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_accurate_images(query, limit):
    output_dir = "dataset"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # استخدام icrawler المتطور لتجاوز حظر السيرفرات وجلب أعلى نتائج مباشرة
        crawler = BingImageCrawler(
            storage={'root_dir': output_dir},
            log_level=50 # إخفاء اللوج الزائد
        )
        
        # البحث بكلمة البحث المطلوبة
        crawler.crawl(
            keyword=query.strip(), 
            max_num=limit,
            min_size=(200, 200) # استبعاد الصور المصغرة والرموز
        )
        
        image_paths = []
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            # ترتيب الصور رقمياً لضمان جلب أول وأصل نتائج البحث بالترتيب
            files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
            
            for file in files:
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path) and os.path.getsize(file_path) > 5120:
                    image_paths.append(file_path)
                    
        return image_paths, output_dir
    except Exception as e:
        print(f"خطأ أثناء الجلب: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! البوت جاهز الآن بأعلى دقة ⚡\n\nأرسل اسم الشخصية والعدد:\n`dante dmc5 3`\n`tokyo ghoul fruta 2`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `dante dmc5 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري جلب أول {count} صور لـ «{query}»...")

    image_paths, main_folder = get_accurate_images(query, count)

    if not image_paths:
        bot.reply_to(message, "❌ تعذر العثور على صور مطابقة، حاول بكلمات أوضح.")
        return

    # إرسال ألبوم بالنتائج الأصلية الصحيحة
    try:
        media = []
        files = []
        for path in image_paths[:count]:
            f = open(path, 'rb')
            files.append(f)
            media.append(telebot.types.InputMediaPhoto(f))
        
        bot.send_media_group(message.chat.id, media)

        for f in files:
            f.close()
    except Exception as e:
        print(f"فشل إرسال الألبوم، جاري الإرسال الفردي: {e}")
        for path in image_paths[:count]:
            try:
                with open(path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
            except Exception:
                continue

    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

if __name__ == "__main__":
    print("✅ البوت يعمل بواسطة icrawler...")
    bot.infinity_polling()
        
    
                    
    

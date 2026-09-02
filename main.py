import os
import shutil
import telebot
from bing_image_downloader import downloader

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_accurate_bing_images(query, limit):
    output_dir = "dataset"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # تحسين صيغة البحث لضمان جلب صور دقيقة وعالية الجودة
    enhanced_query = f"{query} hd wallpaper image"

    try:
        downloader.download(
            enhanced_query, 
            limit=limit, 
            output_dir=output_dir, 
            adult_filter_off=False,  # فلتر البحث الآمن
            force_replace=False, 
            timeout=7,
            verbose=False
        )
        
        query_folder = os.path.join(output_dir, enhanced_query)
        image_paths = []
        if os.path.exists(query_folder):
            for file in os.listdir(query_folder):
                file_path = os.path.join(query_folder, file)
                # التأكد من أن الملف صورة وليس ملفاً تالفاً (حجمه أكبر من 10 كيلوبايت)
                if os.path.getsize(file_path) > 10240:
                    image_paths.append(file_path)
                    
        return image_paths, output_dir
    except Exception as e:
        print(f"خطأ أثناء جلب الصور: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم البحث والعدد لجلب صور عالية الدقة ومضبوطة.\n\nمثال:\n`dmc5 dante 3`\n`one piece luffy 5`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `dmc5 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري البحث عن {count} صور عالية الجودة لـ «{query}»...")

    image_paths, main_folder = get_accurate_bing_images(query, count)

    if not image_paths:
        bot.reply_to(message, "❌ لم يتم العثور على صور مطابقة، جرب كتابة اسم المحتوى أو الشخصية بشكل أوضح.")
        return

    sent_count = 0
    for path in image_paths[:count]:
        try:
            with open(path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
                sent_count += 1
        except Exception as e:
            print(f"خطأ إرسال: {e}")
            continue

    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

if __name__ == "__main__":
    print("✅ البوت يعمل بدقة عالية...")
    bot.infinity_polling()
    
    

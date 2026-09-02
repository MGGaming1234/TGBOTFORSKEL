import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجل لمتابعة الأخطاء في التيرمينال
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# التوكين الخاص بك
TOKEN = "8798071672:AAHNcqWEiOQJcMh7xReQKxnntsarePV5FJQ"

# دالة البحث عن الصور من بينترست
def search_pinterest(query: str, limit: int) -> list:
    url = "https://www.pinterest.com/resource/BaseSearchResource/get/"
    params = {
        "source_param": f'{{"data":{{"query":"{query}"}},"options":{{"page_size":{limit}}}}}'
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        results = data['resource_response']['data']['results']
        
        image_urls = []
        for result in results:
            if 'images' in result and 'orig' in result['images']:
                image_urls.append(result['images']['orig']['url'])
                if len(image_urls) == limit:
                    break
        return image_urls
    except Exception as e:
        logging.error(f"حدث خطأ أثناء جلب الصور: {e}")
        return []

# أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! أنا بوت جلب الصور من بينترست 🎨\n\n"
        "أرسل لي اسم الشيء الذي تبحث عنه متبوعاً بعدد الصور.\n\n"
        "**أمثلة:**\n"
        "• `سيارات 3`\n"
        "• `انمي 5`\n"
        "• `خلفيات 2`",
        parse_mode="Markdown"
    )

# دالة معالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().split()

    # التحقق من أن المستخدم أرسل كلمتين على الأقل (الاسم والعدد)
    if len(text) < 2:
        await update.message.reply_text(
            "⚠️ **خطأ في الصيغة!**\n"
            "يرجى كتابة كلمة البحث ثم عدد الصور بعدها.\n"
            "مثال: `قطط 3`",
            parse_mode="Markdown"
        )
        return

    # التحقق من أن الكلمة الأخيرة عبارة عن رقم
    if not text[-1].isdigit():
        await update.message.reply_text(
            "⚠️ **خطأ في العدد!**\n"
            "يرجى التأكد من كتابة الرقم في نهاية الرسالة.\n"
            "مثال: `مناظر طبيعية 4`",
            parse_mode="Markdown"
        )
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    # تحديد حد أدنى وأقصى لعدد الصور
    if count < 1 or count > 10:
        await update.message.reply_text(
            "⚠️ **عدد غير مسموح!**\n"
            "يرجى اختيار عدد صور بين 1 و 10 فقط."
        )
        return

    await update.message.reply_text(f"🔎 جاري البحث عن {count} صور لـ «{query}» من بينترست...")

    image_urls = search_pinterest(query, count)

    if not image_urls:
        await update.message.reply_text(
            "❌ **عذراً، لم يتم العثور على صور!**\n"
            "حاول البحث باستخدام كلمات أخرى."
        )
        return

    # إرسال الصور للمستخدم
    failed_images = 0
    for url in image_urls:
        try:
            await update.message.reply_photo(photo=url)
        except Exception:
            failed_images += 1
            continue

    if failed_images == count:
        await update.message.reply_text("❌ حدث خطأ أثناء تحميل الصور، يرجى المحاولة لاحقاً.")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
    

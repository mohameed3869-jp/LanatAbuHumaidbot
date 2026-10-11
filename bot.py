import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# تفعيل سجل الأخطاء لمراقبة أي مشكلة في التيرمينال
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("TOKEN") # أو ضع التتوكن هنا مباشرة للتجربة

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في بوت فحص وسائل التواصل الاجتماعي! 🌐\n\n"
        "استخدم الأوامر التالية مع كتابة اليوزر بعدها مباشرة:\n"
        "🎵 تيك توك: `/tiktok username`\n"
        "📸 إنستغرام: `/insta username`\n"
        "📺 يوتيوب: `/youtube channel_name`\n"
        "🐦 تويتر: `/twitter username`",
        parse_mode="Markdown"
    )

async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق مما إذا قام المستخدم كتابة يوزر أم لا
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة اليوزر بعد الأمر.\nمثال: `/tiktok mohammed`", parse_mode="Markdown")
        return
    
    username = context.args[0].lstrip("@")
    profile_url = f"https://www.tiktok.com/@{username}"
    
    keyboard = [[InlineKeyboardButton("🔗 فتح حساب تيك توك", url=profile_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎵 **معلومات حساب TikTok:**\n\n"
        f"👤 اليوزر: `@{username}`\n"
        f"🔗 الرابط جاهز للاستخدام.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة اليوزر بعد الأمر.\nمثال: `/insta mohammed`", parse_mode="Markdown")
        return
    
    username = context.args[0].lstrip("@")
    profile_url = f"https://www.instagram.com/{username}/"
    
    keyboard = [[InlineKeyboardButton("🔗 فتح حساب إنستغرام", url=profile_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📸 **معلومات حساب Instagram:**\n\n"
        f"👤 اليوزر: `@{username}`\n"
        f"🔗 الرابط جاهز للاستخدام.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة اسم القناة بعد الأمر.\nمثال: `/youtube mychannel`", parse_mode="Markdown")
        return
    
    query = " ".join(context.args)
    search_url = f"https://www.youtube.com/@{query.lstrip('@')}"
    
    keyboard = [[InlineKeyboardButton("🔗 فتح قناة يوتيوب", url=search_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📺 **قناة YouTube:**\n\n"
        f"🔍 البحث عن: `{query}`",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def twitter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة اليوزر بعد الأمر.\nمثال: `/twitter mohammed`", parse_mode="Markdown")
        return
    
    username = context.args[0].lstrip("@")
    profile_url = f"https://twitter.com/{username}"
    
    keyboard = [[InlineKeyboardButton("🔗 فتح حساب X", url=profile_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🐦 **حساب X (تويتر):**\n\n"
        f"👤 اليوزر: `@{username}`",
        parse_message="Markdown",
        reply_markup=reply_markup
    )

def main():
    if not TOKEN:
        print("خطأ: التوكن غير موجود")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tiktok", tiktok_command))
    app.add_handler(CommandHandler("insta", insta_command))
    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(CommandHandler("twitter", twitter_command))

    print("البوت يعمل بكفاءة وتطوير ميزات التواصل تم بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()

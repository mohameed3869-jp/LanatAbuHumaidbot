import os
import random
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في بوت فحص وسائل التواصل الاجتماعي! 🌐\n\n"
        "أرسل اليوزر وسأعطيك الروابط المباشرة والمعلومات المتاحة:\n"
        "🎵 تيك توك: `/tiktok username`\n"
        "📸 إنستغرام: `/insta username`\n"
        "📺 يوتيوب: `/youtube channel`\n"
        "🐦 تويتر: `/twitter username`",
        parse_mode="Markdown"
    )

# 1. تيك توك (مع أزرار تفاعلية وروابط مباشرة)
async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل يوزر تيك توك بعد الأمر.\nمثال: `/tiktok username`", parse_mode="Markdown")
        return
    
    username = context.args[0].lstrip("@")
    profile_url = f"https://www.tiktok.com/@{username}"
    
    # أزرار تفاعلية تفتح الحساب مباشرة
    keyboard = [[InlineKeyboardButton("🔗 فتح حساب تيك توك", url=profile_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎵 **حساب TikTok:**\n\n"
        f"👤 اليوزر: `@{username}`\n"
        f"🔗 الرابط: {profile_url}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# 2. إنستغرام
async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل يوزر إنستغرام بعد الأمر.\nمثال: `/insta username`", parse_mode="Markdown")
        return
    
    username = context.args[0].lstrip("@")
    profile_url = f"https://www.instagram.com/{username}/"
    
    keyboard = [[InlineKeyboardButton("🔗 فتح حساب إنستغرام", url=profile_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📸 **حساب Instagram:**\n\n"
        f"👤 اليوزر: `@{username}`\n"
        f"🔗 الرابط: {profile_url}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# 3. يوتيوب
async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل اسم القناة بعد الأمر.\nمثال: `/youtube channel_name`", parse_mode="Markdown")
        return
    
    query = " ".join(context.args)
    search_url = f"https://www.youtube.com/results?search_query={query}"
    
    keyboard = [[InlineKeyboardButton("🔗 البحث في يوتيوب", url=search_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📺 **قناة YouTube:**\n\n"
        f"🔍 البحث عن: `{query}`",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# 4. تويتر / X
async def twitter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل يوزر تويتر بعد الأمر.\nمثال: `/twitter username`", parse_mode="Markdown")
        return
    
    username = context.args[0].lstrip("@")
    profile_url = f"https://twitter.com/{username}"
    
    keyboard = [[InlineKeyboardButton("🔗 فتح حساب X", url=profile_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🐦 **حساب X (تويتر):**\n\n"
        f"👤 اليوزر: `@{username}`\n"
        f"🔗 الرابط: {profile_url}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

def main():
    if not TOKEN:
        print("خطأ: التوكن غير موجود")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tiktok", tiktok_command))
    app.add_handler(CommandHandler("insta", insta_command))
    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(CommandHandler("twitter", twitter_command))

    print("البوت يعمل بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()

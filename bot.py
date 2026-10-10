import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في البوت التجريبي!\n\n"
        "الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/time - الوقت الحالي\n"
        "/info - معلومات عنك\n"
        "/id - عرض الآيدي\n"
        "/random - رقم عشوائي\n"
        "/joke - نكتة\n"
        "/ping - فحص البوت"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/time - الوقت الحالي\n"
        "/info - معلومات عنك\n"
        "/id - عرض الآيدي\n"
        "/random - رقم عشوائي\n"
        "/joke - نكتة\n"
        "/ping - فحص البوت"
    )

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"الوقت الحالي: {now}")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    text = (
        f"📋 **معلوماتك:**\n\n"
        f"الاسم: {user.first_name or 'غير متوفر'}\n"
        f"الاسم الأخير: {user.last_name or 'غير متوفر'}\n"
        f"اليوزرنيم: @{user.username if user.username else 'ما فيه'}\n"
        f"الآيدي: `{user.id}`\n"
        f"لغة الحساب: {user.language_code or 'غير معروفة'}\n"
        f"هل هو بوت؟: {'نعم' if user.is_bot else 'لا'}\n"
        f"حساب مميز (Premium): {'نعم' if getattr(user, 'is_premium', False) else 'لا'}\n"
        f"نوع الشات: {chat.type}\n"
        f"آيدي الشات: `{chat.id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"آيديك: `{user.id}`", parse_mode="Markdown")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    await update.message.reply_text(f"الرقم العشوائي: {number}")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "ليش الكمبيوتر بارد؟ لأنه فتح الويندوز 😂",
        "إيش قال الواحد للصفر؟ انت ما لك قيمة 😆",
        "ليش الدجاجة عبرت الشارع؟ عشان توصل للجهة الثانية 🐔",
        "مرة واحد راح للدكتور قال له: أحس إني بموت. الدكتور: لا تشيل هم، هذا إحساس طبيعي عند اللي بيموتون 😂",
        "ليش الكتاب حزين؟ لأنه فيه مشاكل كثيرة 📖"
    ]
    await update.message.reply_text(random.choice(jokes))

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال 100% ⚡")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"أنت قلت: {update.message.text}")

def main():
    if not TOKEN:
        print("خطأ: التوكن غير موجود")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()

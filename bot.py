import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في البوت!\n\n"
        "الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/time - الوقت الحالي\n"
        "/info - معلوماتك أنت\n"
        "/check @username - محاولة جلب معلومات يوزر\n"
        "/id - عرض الآيدي\n"
        "/random - رقم عشوائي\n"
        "/joke - نكتة\n"
        "/ping - فحص البوت"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "الأوامر:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/time - الوقت\n"
        "/info - معلوماتك\n"
        "/check @username - محاولة البحث عن يوزر\n"
        "/id - الآيدي\n"
        "/random - رقم عشوائي\n"
        "/joke - نكتة\n"
        "/ping - فحص البوت\n\n"
        "ملاحظة: أمر /check نادراً ما يشتغل بسبب قيود تليجرام."
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
        f"حساب مميز: {'نعم' if getattr(user, 'is_premium', False) else 'لا'}\n"
        f"نوع الشات: {chat.type}\n"
        f"آيدي الشات: `{chat.id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ أرسل اليوزر نيم بعد الأمر.\n"
            "مثال: `/check @username`",
            parse_mode="Markdown"
        )
        return

    username = context.args[0].lstrip("@")

    try:
        chat = await context.bot.get_chat(f"@{username}")

        name = " ".join(
            part for part in [chat.first_name, chat.last_name] if part
        ) or "غير متوفر"

        user_username = f"@{chat.username}" if chat.username else "غير متوفر"

        response = (
            "👤 معلومات المستخدم:\n\n"
            f"🔹 الاسم: {name}\n"
            f"🔹 الأيدي: `{chat.id}`\n"
            f"🔹 اليوزر: {user_username}\n"
        )

        if chat.bio:
            response += f"🔹 البايو: {chat.bio}\n"

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception:
        await update.message.reply_text(
            "❌ تعذر جلب المعلومات.\n"
            "تليجرام يمنع البحث عن معظم الحسابات."
        )

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
        "مرة واحد راح للدكتور قال له: أحس إني بموت. الدكتور: لا تشيل هم، هذا إحساس طبيعي عند اللي بيموتون 😂"
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
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()

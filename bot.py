from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التأكد من أن المستخدم أدخل يوزر نيم
    if not context.args:
        await update.message.reply_text("⚠️ يرجى إرسال اليوزر نيم بعد الأمر.\nمثال: `/info @username`")
        return

    username = context.args[0].replace('@', '')

    try:
        # جلب معلومات الشات
        chat = await context.bot.get_chat(f"@{username}")
        
        response = (
            f"👤 **معلومات المستخدم:**\n\n"
            f"🔹 **الاسم:** {chat.first_name} {chat.last_name or ''}\n"
            f"🔹 **الأيدي (ID):** `{chat.id}`\n"
            f"🔹 **اليوزر:** @{chat.username}\n"
        )
        if chat.bio:
            response += f"🔹 **البايو:** {chat.bio}\n"

        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text("❌ لم أتمكن من العثور على هذا المستخدم.")

# أضف المعالج في دالة الـ main الخاصة بك:
# app.add_handler(CommandHandler("info", info_command))

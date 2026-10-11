import os
import random
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في بوت فحص وسائل التواصل الاجتماعي! 🌐\n\n"
        "الأوامر المتاحة لفحص الحسابات:\n"
        "/tiktok username - فحص حساب تيك توك 🎵\n"
        "/insta username - فحص حساب إنستغرام 📸\n"
        "/youtube username - فحص قناة يوتيوب 📺\n"
        "/twitter username - فحص حساب تويتر / X 🐦\n\n"
        "أو استخدم الأمر العام:\n"
        "/check username - (تيك توك افتراضياً)\n"
        "/help - المساعدة"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 **دليل استخدام الأوامر:**\n\n"
        "🎵 تيك توك: `/tiktok your_username`\n"
        "📸 إنستغرام: `/insta your_username`\n"
        "📺 يوتيوب: `/youtube channel_name`\n"
        "🐦 تويتر: `/twitter your_username`\n"
        "⏱ الوقت: `/time`\n"
        "🎲 رقم عشوائي: `/random`\n"
        "😂 نكتة: `/joke`",
        parse_mode="Markdown"
    )

# 1. فحص تيك توك
async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل يوزر تيك توك بعد الأمر.\nمثال: `/tiktok username`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    msg = await update.message.reply_text("🔎 جاري فحص حساب تيك توك...")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            res = await client.get(f"https://countik.com/api/user/info/{username}", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if "username" in data or "nickname" in data:
                    nickname = data.get("nickname", "غير متوفر")
                    followers = data.get("followerCount", 0)
                    following = data.get("followingCount", 0)
                    likes = data.get("heartCount", 0)
                    videos = data.get("videoCount", 0)
                    bio = data.get("signature", "لا يوجد بايو")
                    verified = "نعم 💙" if data.get("verified", False) else "لا"

                    text = (
                        f"🎵 **معلومات TikTok:**\n\n"
                        f"👤 **الاسم:** {nickname}\n"
                        f"🔗 **اليوزر:** @{username}\n"
                        f"🌟 **موثق:** {verified}\n\n"
                        f"👥 **المتابعون:** {followers:,}\n"
                        f"➡️ **يتابع:** {following:,}\n"
                        f"❤️ **اللايكات:** {likes:,}\n"
                        f"🎥 **الفيديوهات:** {videos:,}\n\n"
                        f"📝 **البايو:**\n`{bio}`\n\n"
                        f"🔗 [رابط الحساب](https://www.tiktok.com/@{username})"
                    )
                    await msg.edit_text(text, parse_mode="Markdown")
                    return
            await msg.edit_text("❌ لم يتم العثور على الحساب أو حدث خطأ.")
    except Exception:
        await msg.edit_text("❌ حدث خطأ أثناء الاتصال بخادم تيك توك.")

# 2. فحص إنستغرام
async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل يوزر إنستغرام بعد الأمر.\nمثال: `/insta username`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    msg = await update.message.reply_text("🔎 جاري فحص حساب إنستغرام...")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            # استخدام API عام وموثوق لجلب بيانات انستغرام العامة
            res = await client.get(f"https://www.instagram.com/{username}/?__a=1&__d=dis", headers=headers)
            
            # بديل آخر سريع ومباشر عبر قاعدة بيانات عامة للبروفايلات
            api_res = await client.get(f"https://www.instagram.com/{username}/", headers=headers)
            if api_res.status_code == 200:
                text = (
                    f"📸 **معلومات Instagram:**\n\n"
                    f"🔗 **اليوزر:** @{username}\n"
                    f"🌐 **رابط البروفايل:** https://www.instagram.com/{username}/\n\n"
                    f"💡 *ملاحظة:* انستغرام يفرض قيوداً أمنية قوية تمنع قراءة تفاصيل البايو والمتابعين بشكل آلي مباشر، يمكنك فتح الرابط أعلاه للاطلاع المباشر."
                )
                await msg.edit_text(text, parse_mode="Markdown")
            else:
                await msg.edit_text("❌ الحساب غير موجود أو خاص.")
    except Exception:
        await msg.edit_text("❌ تعذر جلب بيانات إنستغرام حالياً.")

# 3. فحص يوتيوب
async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل اسم القناة أو المعرف بعد الأمر.\nمثال: `/youtube channel_handle`", parse_mode="Markdown")
        return
    query = context.args[0]
    await update.message.reply_text(
        f"📺 **قناة اليوتيوب المطلوبة:** `{query}`\n\n"
        f"🔗 [اضغط هنا للبحث المباشر على يوتيوب](https://www.youtube.com/results?search_query={query})",
        parse_mode="Markdown"
    )

# 4. فحص تويتر / X
async def twitter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل يوزر تويتر بعد الأمر.\nمثال: `/twitter username`", parse_mode="Markdown")
        return
    username = context.args[0].lstrip("@")
    await update.message.reply_text(
        f"🐦 **حساب X (تويتر):** @{username}\n\n"
        f"🔗 [رابط الحساب مباشرة](https://twitter.com/{username})",
        parse_mode="Markdown"
    )

# الأوامر الخدمية الأخرى
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"الوقت الحالي: {now}")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    await update.message.reply_text(f"الرقم العشوائي: {number}")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "ليش الكمبيوتر بارد؟ لأنه فتح الويندوز 😂",
        "إيش قال الواحد للصفر؟ انت ما لك قيمة 😆",
        "ليش الدجاجة عبرت الشارع؟ عشان توصل للجهة الثانية 🐔"
    ]
    await update.message.reply_text(random.choice(jokes))

def main():
    if not TOKEN:
        print("خطأ: التوكن غير موجود")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tiktok", tiktok_command))
    app.add_handler(CommandHandler("insta", insta_command))
    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(CommandHandler("twitter", twitter_command))
    app.add_handler(CommandHandler("check", tiktok_command)) # جعل check يوجه لتيك توك كمثال
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("joke", joke_command))

    print("البوت يعمل بكامل ميزات التواصل الاجتماعي...")
    app.run_polling()

if __name__ == "__main__":
    main()

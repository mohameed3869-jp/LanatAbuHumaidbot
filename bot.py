import os
import random
import httpx  # مكتبة للطلبات السريعة (تأكد من تثبيتها: pip install httpx)
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
        "/check username - فحص حساب تيك توك 🎵\n"
        "/id - عرض الآيدي\n"
        "/random - رقم عشوائي\n"
        "/joke - نكتة\n"
        "/ping - فحص البوت"
    )

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ أرسل يوزر التيك توك بعد الأمر.\n"
            "مثال: `/check username`",
            parse_mode="Markdown"
        )
        return

    username = context.args[0].lstrip("@")
    msg = await update.message.reply_text("🔎 جاري فحص حساب تيك توك...")

    # رابط API عام لجلب معلومات حساب تيك توك
    url = f"https://www.tiktok.com/@{username}"
    
    try:
        # كود لجلب البيانات العامة من تيك توك
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # نرسل طلب بمحاكاة متصفح لضمان استجابة السيرفر
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = await client.get(f"https://countik.com/api/user/exist/{username}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success" or data.get("exist") == True:
                    # جلب تفاصيل أكثر عبر الخدمة
                    stats_res = await client.get(f"https://countik.com/api/user/info/{username}", headers=headers)
                    user_data = stats_res.json()

                    nickname = user_data.get("nickname", "غير متوفر")
                    sec_uid = user_data.get("secUid", "")
                    followers = user_data.get("followerCount", 0)
                    following = user_data.get("followingCount", 0)
                    likes = user_data.get("heartCount", 0)
                    videos = user_data.get("videoCount", 0)
                    bio = user_data.get("signature", "لا يوجد بايو")
                    is_verified = "نعم 💙" if user_data.get("verified", False) else "لا"

                    reply_text = (
                        f"🎵 **معلومات حساب TikTok:**\n\n"
                        f"👤 **الاسم:** {nickname}\n"
                        f"🔗 **اليوزر:** @{username}\n"
                        f"🌟 **حساب موثق؟:** {is_verified}\n\n"
                        f"👥 **المتابعون:** {followers:,}\n"
                        f"➡️ **يتابع:** {following:,}\n"
                        f"❤️ **إجمالي اللايكات:** {likes:,}\n"
                        f"🎥 **عدد الفيديوهات:** {videos:,}\n\n"
                        f"📝 **البايو:**\n`{bio}`\n\n"
                        f"🔗 [رابط الحساب](https://www.tiktok.com/@{username})"
                    )
                    await msg.edit_text(reply_text, parse_mode="Markdown", disable_web_page_preview=False)
                else:
                    await msg.edit_text("❌ الحساب غير موجود على تيك توك.")
            else:
                await msg.edit_text("❌ تعذر الوصول لبيانات تيك توك حالياً، جرب لاحقاً.")

    except Exception as e:
        await msg.edit_text("❌ حدث خطأ أثناء فحص الحساب.")

# باقي الأوامر السابقة كما هي...

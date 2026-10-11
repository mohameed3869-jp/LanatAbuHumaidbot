import os
import re
import html
import logging
import sqlite3
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================
# Configuration
# =========================
TOKEN = os.getenv("TOKEN", "").strip()
ADMIN_IDS = {
    int(value.strip())
    for value in os.getenv("ADMIN_IDS", "").split(",")
    if value.strip().isdigit()
}
DB_PATH = os.getenv("DB_PATH", "social_bot.sqlite3")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("social_bot")

# Conservative username validation. Platform-specific rules vary.
USERNAME_RE = re.compile(r"^[A-Za-z0-9._]{1,100}$")

PLATFORMS = {
    "tiktok": {
        "label": "TikTok",
        "emoji": "🎵",
        "url": lambda username: f"https://www.tiktok.com/@{quote(username, safe='._')}",
    },
    "insta": {
        "label": "Instagram",
        "emoji": "📸",
        "url": lambda username: f"https://www.instagram.com/{quote(username, safe='._')}/",
    },
    "youtube": {
        "label": "YouTube",
        "emoji": "📺",
        "url": lambda username: f"https://www.youtube.com/@{quote(username, safe='._')}",
    },
    "twitter": {
        "label": "X",
        "emoji": "🐦",
        "url": lambda username: f"https://x.com/{quote(username, safe='._')}",
    },
}


# =========================
# SQLite storage
# =========================
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                platform TEXT NOT NULL,
                searched_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_searches_user_id
            ON searches(user_id)
        """)
        conn.commit()


def save_search(user_id: int, username: str, platform: str):
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO searches (user_id, username, platform, searched_at) VALUES (?, ?, ?, ?)",
            (user_id, username, platform, timestamp),
        )
        conn.commit()


def get_global_stats():
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0]
        users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM searches").fetchone()[0]
        recent = conn.execute(
            "SELECT username, platform, searched_at FROM searches ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return total, users, recent


def get_user_history(user_id: int, limit: int = 10):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT username, platform, searched_at FROM searches "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()


# =========================
# Helpers
# =========================
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎵 TikTok", callback_data="platform:tiktok"),
            InlineKeyboardButton("📸 Instagram", callback_data="platform:insta"),
        ],
        [
            InlineKeyboardButton("📺 YouTube", callback_data="platform:youtube"),
            InlineKeyboardButton("🐦 X / Twitter", callback_data="platform:twitter"),
        ],
        [InlineKeyboardButton("🌐 بحث عبر كل المنصات", callback_data="platform:all")],
        [InlineKeyboardButton("🕘 سجل بحثي", callback_data="myhistory")],
    ]
    return InlineKeyboardMarkup(keyboard)


def platform_buttons(username: str):
    rows = []
    for key in ("tiktok", "insta", "youtube", "twitter"):
        p = PLATFORMS[key]
        rows.append([
            InlineKeyboardButton(
                f"{p['emoji']} فتح {p['label']}",
                url=p["url"](username),
            )
        ])
    return InlineKeyboardMarkup(rows)


def normalize_username(raw: str):
    value = raw.strip()
    if value.startswith("@"):
        value = value[1:]
    if not value or not USERNAME_RE.fullmatch(value):
        return None
    return value


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def youtube_stats(handle: str):
    """Return public channel stats only if a YouTube Data API key is configured."""
    if not YOUTUBE_API_KEY:
        return None

    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "snippet,statistics",
                "forHandle": handle,
                "key": YOUTUBE_API_KEY,
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if not items:
            return {"not_found": True}

        channel = items[0]
        snippet = channel.get("snippet", {})
        stats = channel.get("statistics", {})
        return {
            "title": snippet.get("title", "غير متوفر"),
            "subscribers": stats.get("subscriberCount"),
            "views": stats.get("viewCount"),
            "videos": stats.get("videoCount"),
            "hidden_subscribers": stats.get("hiddenSubscriberCount", False),
        }
    except (requests.RequestException, ValueError) as exc:
        logger.warning("YouTube API lookup failed: %s", exc)
        return {"error": True}


async def build_result(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       username: str, platform_key: str):
    user = update.effective_user
    if user is None:
        return

    if platform_key == "all":
        for key in PLATFORMS:
            save_search(user.id, username, key)

        text = (
            f"🔎 <b>نتائج الروابط</b>\n\n"
            f"👤 الاسم المدخل: <code>@{html.escape(username)}</code>\n\n"
            "هذه روابط مباشرة/صفحات الحساب حسب صيغة كل منصة. "
            "إن لم يفتح الرابط، فقد يكون الاسم غير مستخدم أو تغيّر."
        )
        await update.effective_message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=platform_buttons(username),
        )
        return

    if platform_key not in PLATFORMS:
        await update.effective_message.reply_text("❌ منصة غير معروفة.")
        return

    save_search(user.id, username, platform_key)
    p = PLATFORMS[platform_key]
    text = (
        f"{p['emoji']} <b>{p['label']}</b>\n\n"
        f"👤 اليوزر: <code>@{html.escape(username)}</code>\n"
        f"🔗 اضغط الزر لفتح صفحة الحساب.\n"
        "ℹ️ إنشاء الرابط لا يعني أن الحساب موجود أو أن ملكيته تم التحقق منها."
    )

    # Real public statistics are supported for YouTube when its official API is configured.
    if platform_key == "youtube":
        stats = youtube_stats(username)
        if stats is None:
            text += "\n\n📊 الإحصائيات: غير مفعّلة. أضف YOUTUBE_API_KEY لتفعيل إحصائيات YouTube."
        elif stats.get("not_found"):
            text += "\n\n📊 لم يتم العثور على قناة بهذا المعرّف عبر YouTube Data API."
        elif stats.get("error"):
            text += "\n\n📊 تعذّر جلب الإحصائيات حاليًا من YouTube API."
        else:
            text += f"\n\n📊 <b>إحصائيات القناة</b>\n"
            text += f"• الاسم: {html.escape(str(stats['title']))}\n"
            if stats.get("hidden_subscribers"):
                text += "• المشتركون: مخفيون\n"
            elif stats.get("subscribers") is not None:
                text += f"• المشتركون: {int(stats['subscribers']):,}\n"
            if stats.get("views") is not None:
                text += f"• المشاهدات: {int(stats['views']):,}\n"
            if stats.get("videos") is not None:
                text += f"• عدد الفيديوهات: {int(stats['videos']):,}\n"
    else:
        text += (
            "\n\n📊 الإحصائيات: لا تتوفر في النسخة الأساسية لهذه المنصة. "
            "تحتاج إلى API رسمي أو مزوّد بيانات موثوق."
        )

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                f"🔗 فتح {p['label']}",
                url=p["url"](username),
            ),
            InlineKeyboardButton("🏠 القائمة", callback_data="menu"),
        ]]),
    )


# =========================
# Commands and callbacks
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_platform", None)
    await update.effective_message.reply_text(
        "مرحبًا بك في بوت أدوات التواصل الاجتماعي 🌐\n\n"
        "اختر منصة من القائمة، ثم أرسل اسم المستخدم.\n"
        "يمكنك أيضًا استخدام /search username للبحث عبر المنصات.",
        reply_markup=main_menu(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "📚 الأوامر المتاحة:\n\n"
        "/start — القائمة الرئيسية\n"
        "/search username — روابط المنصات الأربع\n"
        "/tiktok username — رابط TikTok\n"
        "/insta username — رابط Instagram\n"
        "/youtube handle — قناة YouTube وإحصائياتها عند تفعيل API\n"
        "/twitter username — رابط X\n"
        "/myhistory — آخر عمليات البحث الخاصة بك\n"
        "/adminstats — إحصائيات البوت للمشرف فقط\n"
        "/adminhistory — آخر عمليات البحث للمشرف فقط"
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "menu":
        context.user_data.pop("awaiting_platform", None)
        await query.edit_message_text(
            "اختر منصة، ثم أرسل اسم المستخدم:",
            reply_markup=main_menu(),
        )
        return

    if data == "myhistory":
        rows = get_user_history(query.from_user.id)
        if not rows:
            await query.message.reply_text("لا يوجد سجل بحث حتى الآن.")
            return
        lines = ["🕘 <b>آخر عمليات البحث الخاصة بك</b>\n"]
        for username, platform, timestamp in rows:
            label = PLATFORMS.get(platform, {}).get("label", platform)
            lines.append(
                f"• <code>@{html.escape(username)}</code> — "
                f"{html.escape(label)} — {html.escape(timestamp)}"
            )
        await query.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
        return

    if data.startswith("platform:"):
        platform = data.split(":", 1)[1]
        if platform not in (*PLATFORMS.keys(), "all"):
            await query.message.reply_text("❌ اختيار غير صالح.")
            return
        context.user_data["awaiting_platform"] = platform
        label = "كل المنصات" if platform == "all" else PLATFORMS[platform]["label"]
        await query.message.reply_text(
            f"أرسل اسم المستخدم للبحث في {label}.\n"
            "يمكنك كتابة الاسم مع أو بدون @."
        )


async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    platform = context.user_data.get("awaiting_platform")
    if not platform:
        return

    username = normalize_username(update.effective_message.text or "")
    if not username:
        await update.effective_message.reply_text(
            "❌ صيغة الاسم غير صالحة. استخدم الأحرف الإنجليزية والأرقام والنقطة أو الشرطة السفلية فقط."
        )
        return

    context.user_data.pop("awaiting_platform", None)
    await build_result(update, context, username, platform)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "استخدم الأمر هكذا:\n/search username\nمثال: /search mohammed"
        )
        return
    username = normalize_username(context.args[0])
    if not username:
        await update.effective_message.reply_text("❌ صيغة اسم المستخدم غير صالحة.")
        return
    await build_result(update, context, username, "all")


async def platform_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.effective_message.text.split()[0].split("@")[0].lstrip("/")
    platform = {"tiktok": "tiktok", "insta": "insta",
                "youtube": "youtube", "twitter": "twitter"}.get(command)
    if not platform:
        return
    if not context.args:
        await update.effective_message.reply_text(
            f"اكتب اسم المستخدم بعد الأمر.\nمثال: /{command} username"
        )
        return
    username = normalize_username(context.args[0])
    if not username:
        await update.effective_message.reply_text("❌ صيغة اسم المستخدم غير صالحة.")
        return
    await build_result(update, context, username, platform)


async def myhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_user_history(update.effective_user.id)
    if not rows:
        await update.effective_message.reply_text("لا يوجد سجل بحث حتى الآن.")
        return
    lines = ["🕘 <b>آخر عمليات البحث الخاصة بك</b>\n"]
    for username, platform, timestamp in rows:
        label = PLATFORMS.get(platform, {}).get("label", platform)
        lines.append(
            f"• <code>@{html.escape(username)}</code> — "
            f"{html.escape(label)} — {html.escape(timestamp)}"
        )
    await update.effective_message.reply_text(
        "\n".join(lines), parse_mode=ParseMode.HTML
    )


async def adminstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.effective_message.reply_text("⛔ هذا الأمر مخصص للمشرف.")
        return

    total, users, _ = get_global_stats()
    await update.effective_message.reply_text(
        f"📊 <b>إحصائيات البوت</b>\n\n"
        f"• إجمالي عمليات البحث: {total}\n"
        f"• عدد المستخدمين الذين بحثوا: {users}",
        parse_mode=ParseMode.HTML,
    )


async def adminhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.effective_message.reply_text("⛔ هذا الأمر مخصص للمشرف.")
        return

    _, _, rows = get_global_stats()
    if not rows:
        await update.effective_message.reply_text("لا توجد عمليات بحث مسجلة.")
        return

    lines = ["🛡 <b>آخر عمليات البحث المسجلة</b>\n"]
    for username, platform, timestamp in rows:
        label = PLATFORMS.get(platform, {}).get("label", platform)
        lines.append(
            f"• <code>@{html.escape(username)}</code> — "
            f"{html.escape(label)} — {html.escape(timestamp)}"
        )
    await update.effective_message.reply_text(
        "\n".join(lines), parse_mode=ParseMode.HTML
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled exception while processing update", exc_info=context.error)


def main():
    if not TOKEN:
        raise SystemExit(
            "TOKEN غير مضبوط. عيّن متغير البيئة TOKEN ثم أعد تشغيل البوت."
        )

    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("tiktok", platform_command))
    app.add_handler(CommandHandler("insta", platform_command))
    app.add_handler(CommandHandler("youtube", platform_command))
    app.add_handler(CommandHandler("twitter", platform_command))
    app.add_handler(CommandHandler("myhistory", myhistory_command))
    app.add_handler(CommandHandler("adminstats", adminstats_command))
    app.add_handler(CommandHandler("adminhistory", adminhistory_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.add_error_handler(error_handler)

    logger.info("Bot is starting")
    app.run_polling()


if __name__ == "__main__":
    main()

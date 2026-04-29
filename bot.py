import os
import logging
import urllib.request
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── خادم ويب بسيط لإبقاء Railway سعيداً ──
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BOT 360 is running!")
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()


# ── أوامر البوت ──
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "المتداول"
    keyboard = [
        [InlineKeyboardButton("🚀 فتح BOT 360°", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton("📊 السعر الحي", callback_data="price"),
            InlineKeyboardButton("📋 القائمة", callback_data="menu"),
        ],
    ]
    welcome_text = (
        f"👋 أهلاً *{name}*!\n\n"
        "🔶 *BOT 360°* — منصة تحليل العملات الرقمية\n\n"
        "📌 *الميزات المتاحة:*\n"
        "• 📈 أسعار مباشرة BTC/ETH\n"
        "• 🔍 SMC Order Blocks\n"
        "• ⚡ FLASH Scalping Engine\n"
        "• 🎯 Trading VIP Strategies\n"
        "• 🧠 المستشار الآلي\n"
        "• ⏳ العد التنازلي للهالفينج\n\n"
        "اضغط الزر أدناه لفتح التطبيق 👇"
    )
    await update.message.reply_text(
        welcome_text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with urllib.request.urlopen(
            "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=5
        ) as r:
            btc = json.loads(r.read())
        with urllib.request.urlopen(
            "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT", timeout=5
        ) as r:
            eth = json.loads(r.read())

        btc_price  = float(btc["lastPrice"])
        btc_change = float(btc["priceChangePercent"])
        btc_high   = float(btc["highPrice"])
        btc_low    = float(btc["lowPrice"])
        eth_price  = float(eth["lastPrice"])
        eth_change = float(eth["priceChangePercent"])

        btc_emoji = "🟢" if btc_change >= 0 else "🔴"
        eth_emoji = "🟢" if eth_change >= 0 else "🔴"

        text = (
            f"📊 *أسعار العملات - LIVE*\n\n"
            f"{btc_emoji} *BTC/USDT*\n"
            f"  💰 السعر: `${btc_price:,.2f}`\n"
            f"  📈 التغيير: `{btc_change:+.2f}%`\n"
            f"  ⬆️ أعلى 24h: `${btc_high:,.2f}`\n"
            f"  ⬇️ أدنى 24h: `${btc_low:,.2f}`\n\n"
            f"{eth_emoji} *ETH/USDT*\n"
            f"  💰 السعر: `${eth_price:,.2f}`\n"
            f"  📈 التغيير: `{eth_change:+.2f}%`\n"
        )
    except Exception:
        text = "⚠️ تعذّر جلب الأسعار، حاول مجدداً."

    keyboard = [[InlineKeyboardButton("🚀 فتح التطبيق", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 *قائمة الاستراتيجيات - BOT 360°*\n\n"
        "🔸 *الرئيسية*\n"
        "├ 📐 الوتد (Wedge Scanner)\n"
        "├ 🧱 SMC Order Blocks\n"
        "├ 🎯 Trading Limit Order (Best Zones)\n\n"
        "🔸 *VIP*\n"
        "├ ⭐ Trading VIP 1 — محرك الإجماع\n"
        "├ 💧 Trading VIP 2 — إجماع السيولة\n"
        "├ ⚡ FLASH — Scalping Engine\n"
        "├ 📊 Trading VIP 3 — RSI Div+Fib+SMC\n"
        "├ 🏆 Trading VIP 4 — Scalping Pro\n\n"
        "🔸 *متقدم*\n"
        "├ 🤖 Trading 1 — المستشار الآلي\n"
        "└ 🔄 Trading X1 — المحرك الرباعي\n"
    )
    keyboard = [[InlineKeyboardButton("🚀 فتح التطبيق", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔶 *BOT 360° - الأوامر:*\n\n"
        "/start — الرئيسية\n"
        "/price — السعر الحالي\n"
        "/menu — القائمة\n"
        "/help — المساعدة\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ اكتب /help للمساعدة.")


def main():
    # شغّل خادم الصحة في خلفية
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()
    logger.info(f"✅ Health server running on port {PORT}")

    # شغّل البوت
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_command))
    app.add_handler(CommandHandler("price",  price_command))
    app.add_handler(CommandHandler("menu",   menu_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    logger.info("✅ BOT 360° يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

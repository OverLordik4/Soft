import logging
from telegram import ChatJoinRequest
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

BOT_TOKEN = "8416995957:AAG2Qn_Gzqy35C6SAv2wwGCecVKaXoz6cqA "
CHANNEL_CHAT_ID = "-1003204433403"

logging.basicConfig(level=logging.INFO)

async def approve_join_request(update: ChatJoinRequest, context: ContextTypes.DEFAULT_TYPE):
    user = update.from_user
    try:
        await update.approve()
        print(f"✅ {user.first_name}")
    except Exception as e:
        print(f"❌ {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(approve_join_request))
    app.run_polling()

if name == "main":
    main()

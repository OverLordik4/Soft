import logging
from telegram import Update, ChatJoinRequest
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes, CommandHandler

# Настройки бота
BOT_TOKEN = "8416995957:AAG2Qn_Gzqy35C6SAv2wwGCecVKaXoz6cqA"  # Замените на токен бота
CHANNEL_CHAT_ID = "-1003204433403"  # ID вашего канала
OWNER_ID = 8249128340  # Замените на ваш ID в Telegram

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def approve_join_request(update: ChatJoinRequest, context: ContextTypes.DEFAULT_TYPE):
    """Автоматически принимает заявки и уведомляет владельца"""
    user = update.from_user
    chat = update.chat
    
    try:
        # Одобряем заявку
        await update.approve()
        
        # Уведомляем владельца
        owner_message = f"""
✅ Новая заявка одобрена:

👤 Пользователь: {user.first_name} {f'({user.username})' if user.username else ''}
🆔 ID: {user.id}
📢 Канал: {chat.title}
⏰ Время: {update.date.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=owner_message
        )
        
        logger.info(f"✅ Заявка одобрена: {user.first_name} (ID: {user.id})")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        
        # Уведомляем владельца об ошибке
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"❌ Ошибка при одобрении заявки от {user.first_name}: {e}"
            )
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки бота (только для владельца)"""
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("🤖 Бот для автопринятия заявок работает!")
    else:
        await update.message.reply_text("⛔ У вас нет доступа к этому боту.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчик заявок
    application.add_handler(ChatJoinRequestHandler(approve_join_request))
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    
    print("🤖 Бот для автопринятия заявок запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()

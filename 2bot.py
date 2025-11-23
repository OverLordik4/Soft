import logging
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)

async def auto_approve_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """АВТОМАТИЧЕСКИ принимает ВСЕХ кто подал заявку"""
    join_request = update.chat_join_request
    user = join_request.from_user
    chat = join_request.chat
    
    try:
        # АВТОМАТИЧЕСКОЕ ПРИНЯТИЕ ЗАЯВКИ
        await join_request.approve()
        
        logger.info(f"✅ ПРИНЯТ: {user.first_name} (@{user.username}) в чат '{chat.title}'")
        
        # Опционально: отправляем приветственное сообщение
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Добро пожаловать в {chat.title}! 🎉"
            )
        except:
            logger.warning(f"Не удалось отправить приветствие пользователю {user.first_name}")
            
    except Exception as e:
        logger.error(f"Ошибка при принятии {user.first_name}: {e}")

def main():
    # ЗАМЕНИ НА СВОЙ ТОКЕН БОТА
    TOKEN = "8416995957:AAG2Qn_Gzqy35C6SAv2wwGCecVKaXoz6cqA"
    
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик для АВТОМАТИЧЕСКОГО принятия заявок
    application.add_handler(ChatJoinRequestHandler(auto_approve_join_request))
    
    logger.info("🤖 Бот запущен и готов принимать заявки АВТОМАТИЧЕСКИ!")
    application.run_polling()

if name == "main":
    main()

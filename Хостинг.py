import asyncio
import csv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


URL = "https://kaliningrad.t2.ru/shop/number"



def setup_driver():
    """Настройка и возврат экземпляра драйвера Chrome."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            delete window.cdc_adoQpoasnfa7amxZLcgUJ;
            delete navigator.__proto__.webdriver;
        '''
    })
    return driver


def parse_numbers_sync():
    """Синхронная функция парсинга номеров с сайта."""
    driver = setup_driver()
    try:
        driver.get(URL)
        logger.info("Страница парсера загружена.")

        # Ожидание появления хотя бы одного номера
        WebDriverWait(driver, 20).until(
            lambda d: any(card.text.strip().replace(" ", "").isdigit() and len(card.text.strip().replace(" ", "")) == 10
                          for card in d.find_elements(By.CSS_SELECTOR, 'div'))
        )

        all_elements = driver.find_elements(By.TAG_NAME, 'div')
        numbers_data = []

        for elem in all_elements:
            text = elem.text.strip()
            if not text:
                continue

            clean_text = text.replace(" ", "")
            if clean_text.isdigit() and len(clean_text) == 10:
                formatted = f"{clean_text[:3]} {clean_text[3:6]} {clean_text[6:8]} {clean_text[8:]}"
                numbers_data.append(formatted)

        numbers_data = list(set(numbers_data))  # Удаление дубликатов
        logger.info(f"Парсинг завершен. Найдено номеров: {len(numbers_data)}")
        return numbers_data

    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return []
    finally:
        driver.quit()


def save_to_txt(numbers):
    """Сохранение списка номеров в текстовый файл."""
    if not numbers:
        return None

    filename = "byoverlord.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for n in numbers:
            f.write(n + "\n")
    return filename



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение при команде /start."""
    welcome_text = (
        "Привет! Я бот для парсинга номеров.\n"
        "Используй команду /parse, чтобы начать сбор данных с сайта."
    )
    await update.message.reply_text(welcome_text)


async def parse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /parse.
    Запускает парсинг в отдельном потоке и отправляет результат пользователю.
    """

    status_message = await update.message.reply_text("🔄 Начинаю парсинг сайта... Это может занять некоторое время.")

    try:

        numbers = await asyncio.to_thread(parse_numbers_sync)

        if numbers:
            # Сохраняем результаты в файл
            filename = save_to_txt(numbers)
            result_text = f"✅ Готово! Найдено номеров: {len(numbers)}"

            await status_message.edit_text(result_text)
            # Отправляем файл пользователю
            with open(filename, 'rb') as document:
                await update.message.reply_document(
                    document=document,
                    caption=f"Результаты парсинга ({len(numbers)} номеров)"
                )
        else:
            await status_message.edit_text("❌ Не удалось найти номера на странице или произошла ошибка.")

    except Exception as e:
        logger.error(f"Ошибка в обработчике /parse: {e}")
        await status_message.edit_text(f"⚠️ При выполнении команды произошла ошибка: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет справку по командам при команде /help."""
    help_text = (
        "Доступные команды:\n"
        "/start - Начать общение с ботом\n"
        "/parse - Запустить парсинг номеров с сайта\n"
        "/help - Показать это сообщение"
    )
    await update.message.reply_text(help_text)



def main():


    TOKEN = "8156754891:AAGs5bW2M8TO9KzYlKQKRdxhcmmdCcGeOzA"


    application = ApplicationBuilder().token(TOKEN).build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("parse", parse_command))
    application.add_handler(CommandHandler("help", help_command))


    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()

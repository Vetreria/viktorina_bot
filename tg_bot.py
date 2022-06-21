import logging
import os
import json
import random


import dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
import redis


from logger import set_logger


logger = logging.getLogger(__name__)
SEND_QUESTION, CHECK_ANSWER = range(2)


def get_buttons():
    buttons = [["Новый вопрос", "Сдаться"], ["Мой счет"]]
    return ReplyKeyboardMarkup(buttons)


def get_question(update: Update, context: CallbackContext):
    redis_connect = context.bot_data["redis_connect"]
    qa = redis_connect.keys(r"question_*")
    qa_random = random.choice(qa).decode("utf-8")
    qa_value = redis_connect.get(qa_random)
    question, answer = json.loads(qa_value)
    redis_connect.set(f"user_tg_{update.effective_user.id}", qa_random)
    update.message.reply_text(question)
    return CHECK_ANSWER


def check_answer(update: Update, context: CallbackContext):
    redis_connect = context.bot_data["redis_connect"]
    qa = redis_connect.get(f"user_tg_{update.effective_user.id}")
    user_answer = update.message.text.lower().strip(".")
    qa_value = redis_connect.get(qa)
    question, answer = json.loads(qa_value)
    if answer.lower().strip(".").lstrip() == user_answer:
        update.message.reply_text(
            "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
    elif update.message.text == "Сдаться":
        update.message.reply_text(f"Правильный: {answer}")
    else:
        update.message.reply_text("Неправильно... Попробуйте новый вопрос?")
    return SEND_QUESTION


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для викторин!", reply_markup=get_buttons())
    logger.warning(update.effective_user.id)
    return SEND_QUESTION


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, exc_info=context.error)


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Пока. Хорошего вам дня!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    dotenv.load_dotenv()
    qa_tg_bot = os.environ["TG_VIKTORINA_BOT"]
    log_tg_bot = os.environ["LOG_BOT_TOKEN"]
    chat_id = os.environ["LOG_CHAT_TG"]
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    redis_pwd = os.environ["REDIS_PASSWORD"]

    redis_connect = redis.Redis(
        host=redis_host, port=redis_port, db=0, password=redis_pwd
    )
    set_logger(logger, log_tg_bot, chat_id)
    logger.warning("Бот запустился")
    updater = Updater(qa_tg_bot)
    dp = updater.dispatcher
    dp.bot_data["redis_connect"] = redis_connect
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SEND_QUESTION: [
                MessageHandler(Filters.regex("^(Новый вопрос|Сдаться)$"), get_question)
            ],
            CHECK_ANSWER: [MessageHandler(Filters.text, check_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling(timeout=600)
    updater.idle()
    logger.warning("Бот закрылся")


if __name__ == "__main__":
    main()

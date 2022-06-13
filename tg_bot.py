import logging
from multiprocessing import context
import os
import json
import dotenv
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import redis


from logger import set_logger
from main import get_qa


logger = logging.getLogger(__name__)


def get_buttons():
    buttons = [['Новый вопрос', 'Сдаться'],
                ['Мой счет']]
    return ReplyKeyboardMarkup(buttons)


def get_question(update: Update, context: CallbackContext):
    redis_connect = context.bot_data['redis_connect']
    qa = get_qa()
    question, answer = random.choice(list(qa.items()))
    redis_connect.set(
        f"tg-{update.effective_user.id}", json.dumps([question, answer]))
    update.message.reply_text(question)
    # print (answer)


def get_answer(update: Update, context: CallbackContext):
    redis_connect = context.bot_data['redis_connect']
    qa = redis_connect.get(
        f"tg-{update.effective_user.id}")
    question, answer = json.loads(qa)
    update.message.reply_text(answer)
     

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я бот для викторин!', reply_markup=get_buttons())


# def echo(bot, update):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)


# def error(bot, update, error):
#     """Log Errors caused by Updates."""
#     logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    dotenv.load_dotenv()
    qa_tg_bot = os.environ["TG_VIKTORINA_BOT"]
    log_tg_bot = os.environ["LOG_BOT_TOKEN"]
    chat_id = os.environ["LOG_CHAT_TG"]
    redis_host=os.environ["REDIS_HOST"]
    redis_port=os.environ["REDIS_PORT"]
    redis_pwd=os.environ["REDIS_PASSWORD"]
    

    redis_connect = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_pwd)
    set_logger(logger, log_tg_bot, chat_id)
    logger.warning('Бот запустился')
    updater = Updater(qa_tg_bot)
    dp = updater.dispatcher
    dp.bot_data['redis_connect'] = redis_connect
    dp.add_handler(CommandHandler("start", start))

    # dp.add_handler(CallbackQueryHandler("Новый вопрос", get_question))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.regex("Новый вопрос"), get_question))
    dp.add_handler(MessageHandler(Filters.regex("Сдаться"), get_answer))
    # dp.add_error_handler(error)
    updater.start_polling(timeout=600)
    updater.idle()
    logger.warning('Бот закрылся')


if __name__ == '__main__':
    main()
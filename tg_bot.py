import logging
import os
import json
import dotenv
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler
import redis


from logger import set_logger
from main import get_qa


logger = logging.getLogger(__name__)
SEND_QUESTION, CHECK_ANSWER = range(2)

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
    return CHECK_ANSWER


def get_answer(update: Update, context: CallbackContext):
    redis_connect = context.bot_data['redis_connect']
    qa = redis_connect.get(
        f"tg-{update.effective_user.id}")
    question, answer = json.loads(qa)
    update.message.reply_text(answer)
    

def answer_check(update: Update, context: CallbackContext):
    redis_connect = context.bot_data['redis_connect']
    qa = redis_connect.get(
        f"tg-{update.effective_user.id}")
    user_answer = f'ответ:\n{update.message.text}'    
    question, answer = json.loads(qa)
    if user_answer.lower().strip('.') == answer.lower().strip('.'):
             update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
    elif update.message.text == 'Сдаться':
        update.message.reply_text(f'Правильный {answer}')
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')
    return SEND_QUESTION
   

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я бот для викторин!', reply_markup=get_buttons())
    logger.warning(update.effective_user.id)
    return SEND_QUESTION


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, exc_info=context.error)


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Пока. Хорошего вам дня!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


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
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SEND_QUESTION: [
                MessageHandler(Filters.regex('^(Новый вопрос|Сдаться)$'),
                               get_question)],

            CHECK_ANSWER: [MessageHandler(Filters.text, answer_check)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling(timeout=600)
    updater.idle()
    logger.warning('Бот закрылся')


if __name__ == '__main__':
    main()
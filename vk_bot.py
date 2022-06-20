import json
import logging
import os
import random


import dotenv
import vk_api as vk
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
import redis


from logger import set_logger


logger = logging.getLogger(__name__)


def start_quiz(event, vk_api):
    logger.warning(f'Пользователь {event.user_id}')
    return vk_api.messages.send(
        user_id=event.user_id,
        random_id=random.randint(1, 1000),
        keyboard=create_keyboard(),
        message='Викторине! Для начала нажмите «Новый вопрос»',
    )


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')
    keyboard.add_line()
    keyboard.add_button('Мой счёт')
    return keyboard.get_keyboard()


def get_question(event, vk_api, redis_connect):
    qa = redis_connect.keys(r"question_*")
    qa_random = random.choice(qa).decode("utf-8")
    qa_value = redis_connect.get(qa_random)
    question, answer = json.loads(qa_value)
    redis_connect.set(
        f"user_vk_{event.user_id}", qa_random)
    return vk_api.messages.send(
        user_id=event.user_id,
        random_id=random.randint(1, 1000),
        keyboard=create_keyboard(),
        message=question,
    )


def get_answer(event, vk_api, redis_connect):
    qa = redis_connect.get(f"user_vk_{event.user_id}")
    qa_value = redis_connect.get(qa)
    question, answer = json.loads(qa_value)
    return vk_api.messages.send(
        user_id=event.user_id,
        random_id=random.randint(1, 1000),
        keyboard=create_keyboard(),
        message=answer,
    )
    

def check_answer(event, vk_api, redis_connect):
    qa = redis_connect.get(f"user_vk_{event.user_id}")
    user_answer = event.text.lower().strip(".")
    qa_value = redis_connect.get(qa)
    question, answer = json.loads(qa_value)
    if answer and user_answer.lower().strip('.') == answer.lower().strip('.').lstrip():
             message_text = 'Правильно! Для следующего вопроса нажми «Новый вопрос»'
    elif event.text == 'Сдаться':
        message_text = f'Правильный {answer}'
    else:
        message_text = 'Попробуйте ещё раз?'
    return vk_api.messages.send(
        user_id=event.user_id,
        random_id=random.randint(1, 1000),
        keyboard=create_keyboard(),
        message=message_text,
    )


def main():
    dotenv.load_dotenv()
    vk_bot = os.environ["VK_BOT"]
    vk_session = vk.VkApi(token=vk_bot)
    vk_api = vk_session.get_api()
    log_tg_bot = os.environ["LOG_BOT_TOKEN"]
    chat_id = os.environ["LOG_CHAT_TG"]
    redis_host=os.environ["REDIS_HOST"]
    redis_port=os.environ["REDIS_PORT"]
    redis_pwd=os.environ["REDIS_PASSWORD"]
    set_logger(logger, log_tg_bot, chat_id)
    logger.warning('Бот ВК запустился')
    longpoll = VkLongPoll(vk_session)
    redis_connect = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_pwd)


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Привет':
                start_quiz(event, vk_api)
            elif event.text == 'Сдаться':
                get_answer(event, vk_api, redis_connect)
            elif event.text == 'Новый вопрос':
                get_question(event, vk_api, redis_connect)
            else:
                check_answer(event, vk_api, redis_connect)


if __name__ == "__main__":
    main()
import random
import os
import dotenv
import vk_api as vk
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType


def echo(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=event.text,
        random_id=random.randint(1,1000)
    )


def main():
    dotenv.load_dotenv()
    vk_bot = os.environ["VK_BOT"]
    vk_session = vk.VkApi(token=vk_bot)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос')

    keyboard.add_button('Сдаться')

    keyboard.add_line()

    keyboard.add_button('Мой счет')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            
            echo(event, vk_api, keyboard)

if __name__ == "__main__":
    main()
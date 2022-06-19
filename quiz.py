import os
import json
import re

import dotenv
import redis


def get_qa(dir_patch):
    quiz_qa = {}
    for filename in os.listdir(dir_patch):
        with open(f'{dir_patch}/{filename}', "r", encoding="KOI8_R") as file:
            file_contents = file.read()
            file_contents_splitten = file_contents.split('\n\n\n')
            for question in file_contents_splitten:
                qa_s = question.split('\n\n')
                for text in qa_s:
                    if re.findall(r'Вопрос.*:', text):
                        question_text = re.split(r'Вопрос.*:', text)[1]
                        question_text = question_text.replace('\n', ' ')
                    if re.findall(r'Ответ:', text):
                        answer_text = re.split(r'Ответ:', text)[1]
                        answer_text = answer_text.replace('\n', ' ')
                quiz_qa[question_text] = answer_text
    with open(f"DATA/qa.json", 'w', encoding='utf8') as file:
        json.dump(quiz_qa, file, ensure_ascii=False)


def send_qa_to_redis(redis_connect):
    with open(f"DATA/qa.json", 'r', encoding='utf8') as file:
        quiz_qa = json.load(file)
        for num, question in enumerate(quiz_qa, 1):
            redis_connect.set(f"question_{num}", json.dumps([question, quiz_qa[question]]))


def main():
    dotenv.load_dotenv()
    redis_host=os.environ["REDIS_HOST"]
    redis_port=os.environ["REDIS_PORT"]
    redis_pwd=os.environ["REDIS_PASSWORD"]
    redis_connect = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_pwd)
    dir_patch = "DATA/quiz-questions"
    get_qa(dir_patch)
    send_qa_to_redis(redis_connect)


if __name__ == '__main__':
    main()


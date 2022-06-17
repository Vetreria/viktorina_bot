import os
import random
import json
import re


def open_file(dir_patch):
    with open(f'{dir_patch}/{random.choice(os.listdir(dir_patch))}', "r", encoding="KOI8_R") as file:
        return file.read()



def get_qa(dir_patch):
    quiz_qa = {}
    file_contents = open_file(dir_patch)
    file_contents_splitten = file_contents.split('\n\n\n')
    for question in file_contents_splitten:
        qa_s = question.split('\n\n')
        for text in qa_s:
            if re.findall('Вопрос.*:', text):
                question_text = re.split('Вопрос.*:', text)[1]
                question_text = question_text.replace('\n', ' ')
            if re.findall('Ответ:', text):
                answer_text = re.split('Ответ:', text)[1]
                answer_text = answer_text.replace('\n', ' ')
        quiz_qa[question_text] = answer_text
#  quiz_qa
        # answers = [answer for answer in file_contents_splitten if 'Ответ' in answer]
        # qa = dict(zip(questions, answers))
    # with open(f"DATA/qa.json", 'w', encoding='utf8') as file:
    #     json.dump(quiz_qa, file, ensure_ascii=False)
    return quiz_qa



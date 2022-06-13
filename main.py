import os
import random


def open_file():
    with open(f'DATA/quiz-questions/{random.choice(os.listdir("DATA/quiz-questions/"))}', "r", encoding="KOI8_R") as file:
        return file.read()


def get_qa():
    file_contents = open_file()
    file_contents_splitten = file_contents.split('\n\n')
    questions = [question for question in file_contents_splitten if 'Вопрос' in question]
    answers = [answer for answer in file_contents_splitten if 'Ответ' in answer]
    return dict(zip(questions, answers))


def main():
    get_qa()


if __name__ == "__main__":
    main()
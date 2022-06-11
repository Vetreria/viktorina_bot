import json

def open_file():
    q_a = {}
    with open("DATA/quiz-questions/1vs1200.txt", "r", encoding="KOI8_R") as file:
        file_contents = file.read()
        file_contents_splitten = file_contents.split('\n\n')
        questions = [question for question in file_contents_splitten if 'Вопрос' in question]
        answers = [answer for answer in file_contents_splitten if 'Ответ' in answer]
        q_a = dict(zip(questions, answers))
    with open("DATA/qa.json", 'w', encoding='utf8') as file:
        json.dump(q_a, file, ensure_ascii=False)





def main():
    open_file()


if __name__ == "__main__":
    main()
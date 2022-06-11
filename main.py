

def open_file():
    with open("DATA/quiz-questions/1vs1200.txt", "r", encoding="KOI8_R") as file:
        file_contents = file.read()
    print(file_contents)





def main():
    open_file()


if __name__ == "__main__":
    main()
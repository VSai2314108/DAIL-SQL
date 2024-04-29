import json
if __name__ == '__main__':
    path = "/blue/daisyw/somasundaramv/DAIL-SQL/dataset/process/MIMIC-TEST_SQL_9-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/questions.json"
    with open(path, 'r') as file:
        data = json.load(file)
        questions = data["questions"]

    path_formated = "/blue/daisyw/somasundaramv/DAIL-SQL/dataset/process/MIMIC-TEST_SQL_9-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/Questions.txt"
    with open(path_formated, 'w') as file:
        for question in questions[:10]:
            file.write(question["prompt"] + '\n' + question["schema_prompt"] + '\n---------------------------------------------------------------------\n')
    print(questions[0])
import re
import csv
import pandas
import sqlite3
import random
import json
import itertools
import numpy as np
import os
import pandas as pd

# GENERATE RESULTS FILES 

# from sumeval.metrics.rouge import RougeCalculator
# rouge = RougeCalculator(stopwords=False, lang="en")

from utils import *

def create_text_sql(path_file, path_json, directory):
    # read the file into predicted
    with open(path_file, 'r') as file:
        predicted_sqls = file.readlines()
    
    # read the json in
    with open(path_json, 'r') as file:
        jfile = json.load(file)

    # read the responses into gold sql 
    gold_sqls = []
    db_ids = []
    questions = []
    for elem in jfile["questions"]:
        gold_sqls.append("SELECT " + elem["response"])
        db_ids.append(elem["db_id"])
        print(elem["prompt"].split('CREATE TABLE "LAB" (')[-1].split("/* Answer the following:")[-1].split("\n")[0].strip())
        questions.append(elem["prompt"].split('CREATE TABLE "LAB" (')[-1].split("/* Answer the following:")[-1].split("\n")[0].strip())
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Write the predicted SQLs to a text file
    with open(f'{directory}/predicted_SQLS.txt', 'w') as file:
        for sql in predicted_sqls:
            file.write(sql.strip() + '\n')
    
    # Write the gold SQLs to a text file
    with open(f'{directory}/Gold_SQLS.txt', 'w') as file:
        for db_id,sql in zip(db_ids,gold_sqls):
            file.write(sql.strip() + '\t' + db_id +'\n')
    
    # Write the questions to a text file
    with open(f'{directory}/Questions.txt', 'w') as file:
        for question in questions:
            file.write(question + '\n')

def load_results(directory):
    with open(directory+"/predicted_SQLS.txt", 'r') as file:
        predicted_sqls = file.readlines()
    with open(directory+"/Gold_SQLS.txt", 'r') as file:
        gold_sqls = file.readlines()
    with open (directory+"/Questions.txt", 'r') as file:
        questions = file.readlines()
    sqls = []
    for gold_sql, predicted_sql, question in zip(gold_sqls, predicted_sqls, questions):
        sqls.append([gold_sql.split("\t")[1].strip(), gold_sql.split("\t")[0].strip(), predicted_sql.strip(), question.strip()])
    return sqls

def get_accuracy(model, db_id, gold_sql, predicted_sql):
    try:
        outPred = model.execute_sql(predicted_sql).fetchall()
        outTtt = model.execute_sql(gold_sql).fetchall()
    except Exception as e:
        print(str(e))
        return 0
    if outPred == outTtt:
        return 1
    return 0
            

if __name__ == '__main__':
    db_file = '/blue/daisyw/somasundaramv/DAIL-SQL/dataset/mimic/database/mimic_iv/mimic_all.db'
    model = query(db_file)
    (db_meta, db_tabs, db_head) = model._load_db(db_file)
    directory = "/blue/daisyw/somasundaramv/DAIL-SQL/Results/MIMIC-CODELLAMA34B"
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    path_file = "/blue/daisyw/somasundaramv/DAIL-SQL/dataset/process/MIMIC-TEST_SQL_9-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/RESULTS_MODEL-code-llama-34B.txt"
    path_json = "/blue/daisyw/somasundaramv/DAIL-SQL/dataset/process/MIMIC-TEST_SQL_9-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/questions.json"
    create_text_sql(path_file, path_json, directory=directory)
    directory_list = load_results(directory)
    results = []
    for entry in directory_list:
        print(entry)
        acc = get_accuracy(model, entry[0], entry[1], entry[2])
        decision = "CORRECT" if acc == 1 else "WRONG"
        results.append([entry[0], entry[3], entry[1], entry[2], decision])
        print(decision)
    df = pd.DataFrame(results, columns=['DATABASE', 'QUESTION', 'GOLD SQL', 'PREDICTED SQL', 'DECISION'])
    df.to_json(directory+"/analysis_of_results.json", orient='records', lines=False)
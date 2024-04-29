import argparse
import os
import json

import openai
from tqdm import tqdm

from llm.chatgpt import init_chatgpt, ask_llm
from utils.enums import LLM
from torch.utils.data import DataLoader
from llm.llama import TextGenerator

from utils.post_process import process_duplication, get_sqls

QUESTION_FILE = "questions.json"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", type=str)
    parser.add_argument("--openai_api_key", type=str, default=None)
    parser.add_argument("--openai_group_id", type=str, default="org-ktBefi7n9aK7sZjwc2R9G1Wo")
    parser.add_argument("--model", type=str, choices=[LLM.TEXT_DAVINCI_003, 
                                                      LLM.GPT_35_TURBO,
                                                      LLM.GPT_35_TURBO_0613,
                                                      # LLM.TONG_YI_QIAN_WEN,
                                                      LLM.GPT_35_TURBO_16K,
                                                      LLM.GPT_4,
                                                      LLM.LLAMA],
                        default=LLM.GPT_35_TURBO)
    parser.add_argument("--start_index", type=int, default=0)
    parser.add_argument("--end_index", type=int, default=1000000)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--mini_index_path", type=str, default="")
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--n", type=int, default=5, help="Size of self-consistent set")
    parser.add_argument("--db_dir", type=str, default="dataset/spider/database")
    args = parser.parse_args()

    # check args
    assert args.model in LLM.BATCH_FORWARD or \
           args.model not in LLM.BATCH_FORWARD and args.batch_size == 1, \
        f"{args.model} doesn't support batch_size > 1"

    questions_json = json.load(open(os.path.join(args.question, QUESTION_FILE), "r"))
    questions = [(_["schema_prompt"], _["prompt"]) for _ in questions_json["questions"]]
    db_ids = [_["db_id"] for _ in questions_json["questions"]]

    # init openai api
    if args.openai_api_key:
        init_chatgpt(args.openai_api_key, args.openai_group_id, args.model)
        text_generator = None
    else:
        token = "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"
        model_id = "TheBloke/CodeLlama-34B-Instruct-GPTQ" 
        # model_id = "TheBloke/Upstage-Llama-2-70B-instruct-v2-GPTQ"
        text_generator = TextGenerator(model_id, token)

    if args.start_index == 0:
        mode = "w"
    else:
        mode = "a"

    if args.mini_index_path:
        mini_index = json.load(open(args.mini_index_path, 'r'))
        questions = [questions[i] for i in mini_index]
        out_file = f"{args.question}/RESULTS_MODEL-{args.model}_MINI.txt"
    else:
        out_file = f"{args.question}/RESULTS_MODEL-{args.model}.txt"


    token_cnt = 0
    with open(out_file, mode) as f:
        for i, joint_prompt in enumerate(tqdm(questions)):
            prompt = joint_prompt[1]
            schema_prompt = joint_prompt[0]
            if i < args.start_index:
                continue
            if i >= args.end_index:
                break
            try:
                res = ask_llm(args.model, [schema_prompt], args.temperature, args.n, text_generator)
            except Exception as e:
                print(f"Error schema generation: {e}")
                continue
            
            # parse result
            key_and_cond = res["response"][0]
            key_and_cond = key_and_cond.rstrip("\n")
            print(key_and_cond + "\n")
            
            # build second prompt
            complete_prompt = prompt+"Foreign Keys: "+key_and_cond+"\nSELECT"
            try:
                res = ask_llm(args.model, [complete_prompt], args.temperature, args.n, text_generator)
            except Exception as e:
                print(f"Error in full generation: {e}")
                continue

            # parse result
            token_cnt += res["total_tokens"]
            if args.n == 1:
                for sql in res["response"]:
                    # remove \n and extra spaces
                    sql = " ".join(sql.replace("\n", " ").split())
                    sql = process_duplication(sql)
                    # python version should >= 3.8
                    if sql.startswith("SELECT"):
                        f.write(sql + "\n")
                    elif sql.startswith(" "):
                        f.write("SELECT" + sql + "\n")
                    else:
                        f.write("SELECT " + sql + "\n")
                    print(str(i) + ": " + sql + "\n")
            else:
                # results = []
                # cur_db_ids = db_ids[i * args.batch_size: i * args.batch_size + len(batch)]
                # for sqls, db_id in zip(res["response"], cur_db_ids):
                #     processed_sqls = []
                #     for sql in sqls:
                #         sql = " ".join(sql.replace("\n", " ").split())
                #         sql = process_duplication(sql)
                #         if sql.startswith("SELECT"):
                #             pass
                #         elif (sql.startswith("Cond") or sql.startswith("[")):
                #             sql = "Foreign Keys: " + sql
                #         elif sql.startswith(" "):
                #             sql = "SELECT" + sql
                #         else:
                #             sql = "SELECT " + sql
                #         processed_sqls.append(sql)
                #     result = {
                #         'db_id': db_id,
                #         'p_sqls': processed_sqls
                #     }
                #     final_sqls = get_sqls([result], args.n, args.db_dir)

                #     for sql in final_sqls:
                #         f.write(sql + "\n")
                continue
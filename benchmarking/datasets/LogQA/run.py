from software_module.core.resolve_files import resolve_files_single_question
from software_module.core.qa import answer_with_client
from software_module.core.api_config import configure_api, GEMINI_MODEL as MODEL

import json
import requests
import pandas as pd
from datetime import datetime
from tqdm import tqdm

INDEX_FILE_PATH = 'benchmarking/datasets/LogQA/target/logqa_index_clipped.json'

# Row limit of -1 (full log file) exceeds API quota for current choice
ROW_LIMIT = 100

SPARK_PATH = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/Spark/Spark_2k.log_structured.csv'
OPENSSH_PATH = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/OpenSSH/OpenSSH_2k.log_structured.csv'
HDFS_PATH = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/HDFS/HDFS_2k.log_structured.csv'

# Picking the smallest valid questions files in the dataset
SPARK_TEST_QUESTIONS = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/Spark/qa.json.test'
OPENSSH_VAL_QUESTIONS = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/OpenSSH/qa.json.val'
HDFS_VAL_QUESTIONS = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/HDFS/qa.json.val'
splits = {
    'spark' : 'test',
    'openssh' : 'val',
    'hdfs' : 'val'
}

def extract_artifacts(response:dict) -> tuple[list, list, list]:
    answer = []
    log_file = []
    log_entry = []

    for log_file_candidate, result_candidate in response.items():
        if (result_candidate['log'].lower() != 'nil'):
            answer.append(result_candidate['answer'])
            log_file.append(log_file_candidate)
            log_entry.append(result_candidate['log'])
    
    return answer, log_entry, log_file

# Custom implementation for opening file with URL
def get_answer(question:str, candidates:list, chat_client) -> dict:
    answers = {}
    for candidate_file in candidates:
        log_content = None
        
        log_content = str(pd.read_csv(candidate_file).to_string().splitlines())
        
        result = answer_with_client(log_content, question, chat_client)
        answers[candidate_file] = result
    
    return answers

def main():
    # Phase 0 is complete, read the results
    print('Reading results from pre-saved Phase 0')
    with open(INDEX_FILE_PATH, 'r') as file:
        file_index = json.load(file)
    
    # Read the questions
    # Entry is 'Question', 'Answer', 'RawLog'
    questions_index = {
        'spark': [json.loads(entry) for entry in requests.get(SPARK_TEST_QUESTIONS).text.splitlines()][0:1],
        'openssh': [json.loads(entry) for entry in requests.get(OPENSSH_VAL_QUESTIONS).text.splitlines()][0:1],
        'hdfs': [json.loads(entry) for entry in requests.get(HDFS_VAL_QUESTIONS).text.splitlines()][0:1]
    }
    print('Loaded questions...')

    chat_client = configure_api()

    # Phase 1
    for test_system, q_index in questions_index.items():
        # test_system is one of 'spark', 'openssh', 'hdfs'
        # index has keys 'Question', 'Answer', 'RawLog'
        for item in q_index:
            item['CandidateFiles'] = resolve_files_single_question(item['Question'], file_index, chat_client)
    print(f'Created candidate file lists')
    
    # Phase 2
    print('Answering questions...')
    total = len(questions_index)
    for test_system, q_index in tqdm(questions_index.items(), total=total):
        for item in q_index:
            response = get_answer(item['Question'], item['CandidateFiles'], chat_client)
            answer, log_entry, log_file = extract_artifacts(response)
            item['Response'] = [
                {
                    'Answer' : answer[i],
                    'LogEntry' : log_entry[i],
                    'LogFile' : log_file[i]
                }
                for i in range(len(answer))
            ]
        
        output_file_name = f'benchmarking/datasets/LogQA/target/outputs/qa-{test_system}-{splits[test_system]}--{datetime.now().strftime('%d-%m-%Y--%H-%M-%S')}.json'
        with open(output_file_name, 'w') as file:
            json.dump(questions_index, file, indent=4)
        print(f'Saved results at {output_file_name}.')

if __name__=='__main__':
    main()
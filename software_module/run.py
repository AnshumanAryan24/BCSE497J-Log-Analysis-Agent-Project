from software_module.core.resolve_files import resolve_files  # Phase 0
from software_module.core.summarize_logs import create_index  # Phase 1
from software_module.core.qa import get_answer  # Phase 2
from software_module.core.api_config import configure_api, GEMINI_MODEL as MODEL  # For Chat API configuration

import os  # For file paths
from datetime import datetime  # For saving results with timestamp
import json  # For saving resulting index as JSON file

# Constants
QUESTIONS_FILE = 'target/questions/question_list1.txt'
STORAGE_CLUSTER_SPECIFIC_QUESTIONS_FILE = 'target/questions/question_list_specific.txt'
SAMPLE_LOGS_ROOT_PATH = 'target/sample_logs'
OUTPUT_ROOT_PATH = 'target/outputs'

def record_answers(questions:list[str], chat_client, logs_root:str=SAMPLE_LOGS_ROOT_PATH, file_index:dict=None):
    chat_client = configure_api()

    # Phase 0: Get the mapping log_file : file_summary
    if (file_index==None):
        print('Creating index...')
        file_index = create_index(chat_client, logs_root, True)
        print(f'Phase 0 complete, created file index for {len(file_index.keys())} log files')
    else:
        print(f'File index found for {len(file_index.keys())} files.')
        print('Phase 0 complete.')

    # Phase 1: Resolve which files potentially contain answers to which questions    
    print('Resolving files...')
    q_files = resolve_files(questions, file_index, chat_client)
    print(f'Phase 1 complete, resolved candidate log files for {len(questions)} questions')

    # Phase 2: Open each file, then return a potential answer for the respective question
    # Phase 2 implementation is in the file qa.py
    results_index = {}

    print('Phase 2 results:')
    print('----------------')
    for question in questions:
        print(f'Question: {question}')
        answers = get_answer(question, q_files[question], chat_client)
        results_index[question] = answers
        for log_file, result in answers.items():
            print(f'Log File Used: {log_file}')
            print(f'Answer Received: {result["answer"]}')
            print(f'Relevant log entry: {result["log"]}')
            print()
        print('----------------')
    
    results_index['file_index'] = file_index

    return results_index

def main():
    # Configure the Chat API
    chat_client = configure_api()

    # Get saved questions
    questions = None
    with open(STORAGE_CLUSTER_SPECIFIC_QUESTIONS_FILE, 'r') as file: 
        questions = file.read().split('\n')
    questions = questions[2:3]
    
    # Ignoring return answers here for this demo
    results_index = record_answers(questions, chat_client)
    result_file = os.path.normpath(
        os.path.join(
            os.path.join(OUTPUT_ROOT_PATH, MODEL),
            'run-output-' + datetime.now().strftime('%d-%m-%Y--%H-%M-%S') + '.json'
        )
    )
    with open(result_file, 'w') as file:
        json.dump(results_index, file, indent=4)
    print()
    print(f'Saved results at {result_file}')

if __name__=='__main__':
    main()
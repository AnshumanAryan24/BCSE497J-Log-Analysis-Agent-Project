from resolve_files import resolve_files  # Phase 0
from summarize_logs import create_index  # Phase 1
from qa import get_answer  # Phase 2
from api_config import configure_api  # For Chat API configuration

from datetime import datetime  # For saving results with timestamp
import json  # For saving resulting index as JSON file
from time import sleep

# Constants
QUESTIONS_FILE = 'target/questions/question_list1.txt'
SAMPLE_LOGS_ROOT_PATH = 'target/sample_logs'

def main():
    # Configure the Chat API
    chat_client = configure_api()

    # Get saved questions
    questions = None
    with open(QUESTIONS_FILE, 'r') as file: 
        questions = file.read().split('\n')

    # Phase 0: Get the mapping log_file : file_summary
    file_index = create_index(chat_client, SAMPLE_LOGS_ROOT_PATH, True)
    print(f'Phase 0 complete, created file index for {len(file_index.keys())} log files')

    # Phase 1: Resolve which files potentially contain answers to which questions    
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
            if (str(result['start_index']).isdigit()):
                print(f'At index {result["start_index"]}, span {result["length"]} logs')
            print()
        print('----------------')
    
    results_index['file_index'] = file_index
    result_file = 'target/outputs/run-output-' + datetime.now().strftime('%d-%m-%Y--%H-%M-%S') + '.json'
    with open(result_file, 'w') as file:
        json.dump(results_index, file, indent=4)
    print()
    print(f'Saved results at {result_file}')

if __name__=='__main__':
    main()
from software_module.core.summarize_logs import create_index  # Phase 0
from software_module.core.resolve_files import resolve_files  # Phase 1
from software_module.core.qa import get_answer  # Phase 2
from software_module.core.api_config import configure_api, GEMINI_MODEL as MODEL  # For Chat API configuration

import os  # For handling log file paths

# For colorful display
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
BLACK = "\033[30m"
RED_BG = "\033[41m"
GREEN_BG = "\033[42m"
YELLOW_BG = "\033[43m"
BLUE_BG = "\033[44m"
BLACK_BG = "\033[30m"

RESET = "\033[0m"

def setup(logs_root:str):
    chat_client = configure_api()
    file_index = create_index(chat_client, logs_root, True)
    return chat_client, file_index

def answer_user_question(question:str, chat_client, logs_root:str, file_index:dict=None):
    # Phase 0
    if (file_index==None):
        file_index = create_index(chat_client, logs_root, True)

    # Phase 1
    q_files = resolve_files([question], file_index, chat_client)

    # Phase 2
    answers = get_answer(question, q_files[question], chat_client)
    return answers

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


def main():
    print(f"\n{BLUE_BG}=== Log Analysis Agent: Live Demo ==={RESET}")
    print("Enter the absolute path of the root log directory once.")
    print("Then ask questions. Type 'exit' to quit.\n")

    print(f'Using model {MODEL}.')

    root_path = input("Root log directory: ").strip()

    while not os.path.isdir(root_path):
        print("Invalid directory. Try again.")
        root_path = input("Root log directory: ").strip()

    print(f"\nRoot directory set to: {root_path}")

    chat_client, file_index = setup(root_path)
    print(f'File index created for {len(file_index.keys())} files.')
    
    print("You can now enter questions.\n")
    while True:
        print()
        user_q = input(f"{BLACK};{YELLOW_BG}Question >{RESET} ").strip()
        if user_q.lower() in {"exit", "quit"}:
            print(f"{BLACK};{GREEN_BG}Session terminated.{RESET}")
            break

        try:
            response = answer_user_question(
                question=user_q, chat_client=chat_client, logs_root=root_path, file_index=file_index
            )
            response = response[user_q]
        except Exception as e:
            print(f"Error while processing: {e}")

        answer, log_entry, log_file = extract_artifacts(response)
        if len(answer) == 0:
            print(f'{RED}Answer: No answer found{RESET}')
        else:
            for ans, le, lf in zip(answer, log_entry, log_file):
                print(f'{lf}: {ans}')
                print(f'  \'--> {le}')
    
    choice = input('Print the log file summaries (y/n)? ').strip().lower()
    if (choice=='y'):
        for log_file, summary in file_index.items():
            print(f'{log_file} : {summary}')
    
    print(f'{BLACK};{GREEN_BG}Exiting...{RESET}')

if __name__ == "__main__":
    main()

from argparse import ArgumentParser  # For CLI usage
import json  # For saving resulting index as JSON file

from core.api_config import configure_api, API  # For Chat API configuration

# Prompt Engg. constants
COMPARE_PROMPT = '''You are given a summary of a log file and a question. Decide whether this log file might contain information relevant to answering the question.
Use only the summary. Do not assume any information that is not explicitly stated.

Your goal is to avoid rejecting potentially useful files.
If there is any reasonable possibility that the answer could be inside the file, respond "YES".
Respond "NO" only if the summary clearly shows the file is irrelevant.

Output must be exactly one word: YES or NO.
'''

# Functions
def compare(summary:str, question:str, chat_client) -> bool:
    complete_prompt = COMPARE_PROMPT \
        + f'Summary: {summary}' \
        + f'Question: {question}'
    
    response = None
    if API=='gemini':
        response = chat_client.generate_content(complete_prompt)
        response = response.text
    
    res = response.lower()
    if 'yes' in res:
        return True
    elif 'no' in res:
        return False
    else:
        raise ValueError(f'The Chat API did not return an expected response. Returned response was: {res}')

def resolve_files_single_question(question:str, file_index:dict, chat_client) -> list:
    candidates = []

    for file_path, summary in file_index.items():
        valid = compare(summary, question, chat_client)
        if (valid):
            candidates.append(file_path)

    return candidates

def resolve_files(questions:list, file_index:dict, chat_client) -> dict:
    q_files = {}
    for question in questions:
        file_list = resolve_files_single_question(question, file_index, chat_client)
        q_files[question] = file_list
    return q_files

def main(args):
    chat_client = configure_api()

    file_index = None
    with open(args.index_path, 'r') as file:
        file_index = json.load(file)
    
    questions = None
    if args.question:
        questions = [args.question]
    elif args.question_file:
        with open(args.question_file, 'r') as file:
            questions = file.readlines()
            questions = [q[:-1] if q[-1]=='\n' else q for q in questions]  # Remove '\n' from each line if present
    
    q_files = resolve_files(questions, file_index, chat_client)
    for q, files in q_files.items():
        print(f'Question: {q}')
        print(f'Files: {files}')
        print()

if __name__ == '__main__':
    # Parse Arguments
    # Add all the required arguments for CLI usage
    # TODO: Add --verbose option
    parser = ArgumentParser()
    
    # One positional argument
    parser.add_argument(
        'index_path',
        type=str,
        help='Path to index JSON containing files and their summaries'
    )

    # Argument group for single question or file containing one question per line
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-q',
        '--question',
        type=str,
        help='Single question passed as a string'
    )
    group.add_argument(
        '-Q',
        '--question_file',
        type=str,
        help='Path to file containing one question per line'
    )

    parsed_args = parser.parse_args()

    main(parsed_args)
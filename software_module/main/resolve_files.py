from argparse import ArgumentParser  # For CLI usage
import os  # For handling log files and paths
import json  # For saving resulting index as JSON file
import google.generativeai as genai  # For summarizing log content
from dotenv import load_dotenv  # For loading environment variables

# Prompt Engg. constants
COMPARE_PROMPT = '''You will be given the summary of a recorded log file and a question. Your task is to determine whether the log file, if read completely, could potentially contain the answer to the question given, based on the given summary.
You must assume only the given summary as true and not add new information to it.
If the log file fits to be a candidate for finding the answer to the given question, report "YES", else report "NO".
Note that your response must contain only "YES" or "NO", and no other surrounding salutation.
'''

# Chat API constants
API = 'gemini'
GEMINI_MODEL = 'gemma-3-1b-it'  # gemma-3n-e2b-it, gemini-2.5-flash-lite, gemini-2.5-flash

# Functions
def configure_api():
    # Based on chosen API Vendor, return chat client object
    client = None
    if API=='gemini':
        load_dotenv(dotenv_path='.env', override=True)  # Using relative path from root of project
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('GOOGLE_API_KEY not found. Make sure you have a .env file.')
        
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(GEMINI_MODEL)
    return model

def compare(summary:str, question:str, chat_client) -> bool:
    complete_prompt = COMPARE_PROMPT \
        + f'Summary: {summary}' \
        + f'Question: {question}'
    
    response = None
    if API=='gemini':
        response = chat_client.generate_content(complete_prompt)
    
    res = response.text.lower()
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
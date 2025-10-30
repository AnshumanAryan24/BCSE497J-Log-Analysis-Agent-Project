from argparse import ArgumentParser  # For CLI usage
import os  # For handling log files and paths
import json  # For saving resulting index as JSON file
import google.generativeai as genai  # For summarizing log content
from dotenv import load_dotenv  # For loading environment variables

# Prompt Engg. constants
SUMMARY_WORD_LIMIT = 40
SUMMARIZE_PROMPT = f'''You are supposed to read the given log file entries for the given log file and summarize what happened in the log file, in no more than {SUMMARY_WORD_LIMIT} words. The summary should be able to convey precisely the start and end state of the system that the log file describes. Assume only the information given in the log file to be true, do not add new information to it.
NOTE: Your response must contain only the intended summary, no other surrounding salutation.
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

def read_log_file(file_path:str) -> tuple:  # For now, returns tuple of lines
    lines = ()
    with open(file_path, 'r') as file:
        lines = tuple(file.readlines())
    return lines

def summarize_log_entries(chat_client, filename:str, entries:tuple) -> str:
    complete_prompt = SUMMARIZE_PROMPT \
        + f'Filename: {filename}\n' \
        + f'Log Entries:\n' \
        + str(entries)
    
    response = None
    if API=='gemini':
        response = chat_client.generate_content(complete_prompt)
    
    return response.text

def create_index(chat_client, root_path:str, recursive) -> dict:
    file_index = {}
    for item in os.scandir(root_path):
        if item.is_dir() and recursive:
            file_index.update(create_index(chat_client, item.path, recursive))
        else:
            logs = read_log_file(item.path)  # Why a separate function? Good question
            cleaned_path = os.path.normpath(item.path)  # Make the separators in path uniform

            summary = summarize_log_entries(chat_client, item.name, logs)
            file_index[cleaned_path] = summary
            
            # TODO: Remove this break when code runs properly
            break
    
    return file_index

def main(chat_client, args):
    # Create the index (dict) then save as JSON file
    index = create_index(chat_client, args.log_dir, args.recursive)
    with open(args.output, 'w') as file:
        json.dump(index, file)

if __name__ == '__main__':
    chat_client = configure_api()

    # Parse Arguments
    # Add all the required arguments for CLI usage
    # TODO: Add --verbose option
    parser = ArgumentParser()
    
    # Two positional arguments
    parser.add_argument(
        'log_dir',
        type=str,
        help='Root folder for reading the log files'
    )
    parser.add_argument(
        'output',
        type=str,
        help='Name of output JSON file (may not contain file extension)'
    )

    # Other optional arguments
    parser.add_argument(
        '-r', '--recursive',
        default=False,
        action='store_true',
        help='Whether the root folder\'s subfolders, if any, should be explored'
    )
    # TODO: Check for need of this argument
    parser.add_argument(
        '-f', '--file_extension',
        default='txt',
        type=str,
        help='File extension of the log files'
    )

    parsed_args = parser.parse_args()
    main(chat_client, parsed_args)
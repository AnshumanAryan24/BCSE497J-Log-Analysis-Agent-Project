from argparse import ArgumentParser  # For CLI usage
import os  # For handling log files and paths
import json  # For saving resulting index as JSON file

from api_config import configure_api, API  # For Chat API configuration

# Prompt Engg. constants
SUMMARY_WORD_LIMIT = 40
SUMMARIZE_PROMPT = f'''You are supposed to read the given log file entries for the given log file and summarize what happened in the log file, in no more than {SUMMARY_WORD_LIMIT} words. The summary should be able to convey precisely the start and end state of the system that the log file describes. Assume only the information given in the log file to be true, do not add new information to it.
NOTE: Your response must contain only the intended summary, no other surrounding salutation.
'''

# Functions
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
        response = response.text
    
    return response

def create_index(chat_client, root_path:str, recursive:bool) -> dict:
    file_index = {}
    for item in os.scandir(root_path):
        if item.is_dir() and recursive:
            file_index.update(create_index(chat_client, item.path, recursive))
        else:
            logs = read_log_file(item.path)  # Why a separate function? Good question
            cleaned_path = os.path.normpath(item.path)  # Make the separators in path uniform

            summary = summarize_log_entries(chat_client, item.name, logs)
            file_index[cleaned_path] = summary
    
    return file_index

def main(args):
    chat_client = configure_api()

    # Create the index (dict) then save as JSON file
    index = create_index(chat_client, args.log_dir, args.recursive)
    with open(args.output, 'w') as file:
        json.dump(index, file, indent=4)

if __name__ == '__main__':
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
    main(parsed_args)
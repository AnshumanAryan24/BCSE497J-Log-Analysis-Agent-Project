from argparse import ArgumentParser  # For CLI usage
import os  # For handling log files and paths
import json  # For saving resulting index as JSON file

def read_log_file(file_path:str) -> tuple:  # For now, returns tuple of lines
    lines = ()
    with open(file_path, 'r') as file:
        lines = tuple(file.readlines())
    return lines

def create_index(root_path:str) -> dict:
    index = {}
    for item in os.scandir(root_path):
        if item.is_dir():
            index.update(create_index(item.path))
        else:
            logs = read_log_file(item.path)  # Why a separate function? Good question
            cleaned_path = os.path.normpath(item.path)  # Make the separators in path uniform
            index[cleaned_path] = logs
    
    return index

def main(args):
    # Create the index (dict) then save as JSON file
    index = create_index(args.log_dir)
    with open(args.output, 'w') as file:
        json.dump(index, file)

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
        type=bool,
        help='Whether the root folder\'s subfolders, if any, should be explored'
    )
    parser.add_argument(
        '-f', '--file_extenstion',
        default='txt',
        type=str,
        help='File extension of the log files'
    )

    parsed_args = parser.parse_args()
    main(parsed_args)
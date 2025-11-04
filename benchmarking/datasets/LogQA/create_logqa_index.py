from software_module.core.summarize_logs import summarize_log_entries  # Phase 0
from software_module.core.api_config import configure_api

import json
import pandas as pd

OUTPUT_FILE_PATH = 'benchmarking/datasets/LogQA/target/logqa_index_clipped.json'

# Row limit of -1 (full log file) exceeds API quota for current choice
ROW_LIMIT = 100

SPARK_PATH = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/Spark/Spark_2k.log_structured.csv'
OPENSSH_PATH = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/OpenSSH/OpenSSH_2k.log_structured.csv'
HDFS_PATH = 'https://raw.githubusercontent.com/LogQA-dataset/LogQA/refs/heads/main/data/HDFS/HDFS_2k.log_structured.csv'

def main():
    chat_client = configure_api()

    print('Creating the file index...')
    if ROW_LIMIT > 0:
        file_index = {
            'spark': pd.read_csv(SPARK_PATH)[:ROW_LIMIT].to_string().split('\n'),
            'openssh': pd.read_csv(OPENSSH_PATH)[:ROW_LIMIT].to_string().split('\n'),
            'hdfs': pd.read_csv(HDFS_PATH)[:ROW_LIMIT].to_string().split('\n')
        }
        for k, v in file_index.items():
            file_index[k] = summarize_log_entries(chat_client, k, tuple(v))
            print(f'Summarized {k} log file with first {ROW_LIMIT} rows')
        
        file_index['row_limit'] = ROW_LIMIT
    else:
        file_index = {
            'spark': pd.read_csv(SPARK_PATH).to_string().split('\n'),
            'openssh': pd.read_csv(OPENSSH_PATH).to_string().split('\n'),
            'hdfs': pd.read_csv(HDFS_PATH).to_string().split('\n')
        }
        for k, v in file_index.items():
            file_index[k] = summarize_log_entries(chat_client, k, tuple(v))
            print(f'Summarized {k} log file with all rows')
        
        file_index['row_limit'] = -1

    with open(OUTPUT_FILE_PATH, 'w') as file:
        json.dump(file_index, file, indent=4)
    print(f'Saved index at {OUTPUT_FILE_PATH}')

if __name__=='__main__':
    main()
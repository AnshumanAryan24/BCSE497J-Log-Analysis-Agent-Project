from api_config import API  # For Chat API configuration
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type # For backoff in API rate limit
import google.api_core.exceptions  # Exception for API RPM limit

# API call Backoff limit
MAX_WAIT_TIME = 60  # seconds
MAX_ATTEMPTS = 20

# Prompt Engg. constants
ANSWER_PROMPT = '''You will be given the log file entries of a system and an associated question. Analyse the logs and answer the question.
You must assume only the given logs to be true, do not add new information to it. You must report three items in your response - the answer, the start index of the most relevant log entry that answered the question, the number of relevant logs after the starting index.
Report only one answer, and its respective start index and length.

Stick strictly to the following answer format:
ANSWER: <your answer in english words, no explaination>
START INDEX: <starting log entry index>
LENGTH: <length of log entries spanned>

You must answer exactly in the above provided format.
'''

# Chat API constants
API = 'gemini'
GEMINI_MODEL = 'gemma-3-1b-it'  # gemma-3n-e2b-it, gemini-2.5-flash-lite, gemini-2.5-flash

# Functions
@retry(
    wait=wait_exponential(multiplier=1, max=MAX_WAIT_TIME),
    stop=stop_after_attempt(MAX_ATTEMPTS),
    retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted) 
)
def answer_with_client(log_content:str, question:str, chat_client) -> dict:
    complete_prompt = ANSWER_PROMPT \
        + f'Question: {question}\n\n' \
        + f'Log File Content:\n{log_content}'
    
    response = None
    if API=='gemini':
        response = chat_client.generate_content(complete_prompt)
        response = response.text
    
    res = response.split('\n')
    
    answer = res[0].split('ANSWER: ')[1]
    
    # Not converting values to int here for now to avoid formatting issues
    # in case of no answer found, as response is unreliable in this case.
    start_index = res[1].split('START INDEX: ')[1]
    length = res[2].split('LENGTH: ')[1]

    return {
        'answer': answer,
        'start_index': start_index,
        'length': length
    }

def get_answer(question:str, candidates:list, chat_client) -> dict:
    answers = {}
    for candidate_file in candidates:
        log_content = None
        with open(candidate_file, 'r') as file:
            log_content = file.read()
        
        result = answer_with_client(log_content, question, chat_client)
        answers[candidate_file] = result
    
    return answers
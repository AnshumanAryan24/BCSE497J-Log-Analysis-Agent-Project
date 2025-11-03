from api_config import API  # For Chat API configuration
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type # For backoff in API rate limit
import google.api_core.exceptions  # Exception for API RPM limit

# API call Backoff limit
MAX_WAIT_TIME = 60  # seconds
MAX_ATTEMPTS = 20

# Prompt Engg. constants
ANSWER_PROMPT = '''You will be given the full log entries of a file and a question.
Your task is to decide whether the log entries contain enough information to answer the question exactly.

Rules:
1. Use only the given logs. Do not infer or imagine missing details.
2. You must return exactly one answer. If multiple entries look relevant, choose the single most directly informative one.
3. The LOG field must contain the exact log entry text you used, without modification or summarization.
4. If the logs do not contain a complete answer, return "nil" for both fields. Partial or guessed answers are not allowed.

Output must strictly follow this format:

ANSWER: <your answer in plain English, no explanation>
LOG: <exact log line used, or "nil">

No extra text. No reasoning.
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
    log_entry = res[1].split('LOG: ')[1]

    return {
        'answer': answer,
        'log': log_entry
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
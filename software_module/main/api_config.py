import os  # For handling log files and paths
import google.generativeai as genai  # For summarizing log content
from dotenv import load_dotenv  # For loading environment variables

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
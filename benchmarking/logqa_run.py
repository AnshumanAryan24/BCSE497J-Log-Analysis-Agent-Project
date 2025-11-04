from software_module.core.resolve_files import resolve_files  # Phase 0
from software_module.core.summarize_logs import create_index  # Phase 1
from software_module.core.qa import get_answer  # Phase 2
from software_module.core.api_config import configure_api, GEMINI_MODEL as MODEL  # For Chat API configuration

def main():
    pass

if __name__=='__main__':
    main()
## File Information for `core/`
- `api_config.py`: Handles configuration of chat APIs. Import the `configure_api()` function and `API` constant from here for usage.
- `summarize_logs.py`: Implementation for Phase 0. Import the function `create_index()` for usage.
- `resolve_files.py`: Implementation for Phase 1. Import the function `resolve_files()` for usage.

Refer `run.py` for the project demo. It takes the sample logs from the [target/sample_logs/](../../target/sample_logs/) folder and runs through Phase 0, 1, 2. Output of all phases is saved in files following format: `target/outputs/model-name/run-output--<TIMESTAMP>.json`.

The implementations of Phase 0 and 1 also have enabled CLI usage. For this, refer the file [target/run_commands.txt](../../target/run_commands.txt) with commands listed in order (assuming Python venv setup also).
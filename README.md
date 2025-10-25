# BCSE497J-Log-Analysis-Agent-Project
Code for the Project course BCSE497J for building Log Analysis agent for Q/A over log data.

Team members:
1. Anshuman Aryan 22BCE0219
2. Laukik Wadhwa 22BCE2576

# Workflow for the proposed system
## Phase 0:
- Preparing the system
- JSON index file format:
    `log_file_name.log` : text_summary
- For each log file, prepare a small summary of what information is contained in the file
- The summary can be text or another nested JSON dictionary, based on provided schema

## Phase 1:
- Given a question, resolve which file(s) contain relevant information for solving the question
- Context Resolver phase

## Phase 2:
- Given a list of relevant candidate log files, answer a given question and return relevant log entries, or the inability to do so, provided the above context
- Returns the files that might contain the answer to the given question, based on their content summary
- Final Q/A phase
- The answer dictionary format:
    `log_file_name.log` : [
        answer (`string`): actual answer from respective log_file_name.log file,
        index (`int`): start index of most important entries that were used to form the answer
        length (`int`): number of entries after starting `index` that were most important
    ]

## Code:
### Phase 0:
```
FUNCTION record_logs(logs: list of log files) RETURNS dictionary of files and summaries:
    output_dict <-- {}
    FOR EACH log_file in logs:
        output_dict[log_file.name] <-- SUMMARIZE(log_file.name, GET_CONTENT(log_file.name))
    END FOR
    RETURN output_dict
```

### Phase 1:
```
FUNCTION resolve_files(question: given question or a transformation, summary_dict: dictionary from Phase 1) RETURNS list of candidate relevant files:
    output_list <-- []
    FOR EACH log_file_name, summary in summary_dict.items():
        valid <-- COMPARE(summary, question)
        IF (valid):
            output_list.append(log_file_name)
        END IF
    END FOR
    RETURN output_dict
```

### Phase 2:
```
FUNCTION get_answer(question: given question or a transformation, candidates: list of relevant names of relevant files from Phase 2) RETURNS answer dictionary:
    answers <-- {}
    FOR EACH candidate in candidates:
        log_content <-- GET_CONTENT(candidate)
        [valid:boolean, answer:string, index:int, length:int] <-- ANSWER(candidate, log_content, question)
        IF (valid):
            answers[candidate] <-- [answer, index, length]
        END IF
    END FOR
    RETURN answers
```

### Auxilliary function details:
- `GET_CONTENT(log_file_name:string) RETURNS list[line]`:
    
    Read the log file and return list of log entries present in the file

- `SUMMARIZE(log_file_name:string, file_content:list[line]) RETURNS Any`:
    
    Use LLM to retrieve the summary of the content in a pre-specified format (can be provided separately)

- `COMPARE(summary:Any, question:string) RETURNS boolean`:
    
    Use LLM to conclude whether the given question can be answered using the file with the given summary

- `ANSWER(candidate:string, log_content:list[line], question:string) RETURNS list[boolean, string, int, int]`:
    
    Use LLM and some formatting to answer the given question using the given context of file name (`candidate`) and the file's content (`log_content`), along with a `boolean` variable indicating whether the model was able to answer the question
import typer
import json
from ast import literal_eval

def extract_data(data_path:str):
    '''
    read txt file
    '''
    data = []
    
    with open(data_path, "r") as file:
        for line in file.readlines():
            line = literal_eval(line)
            data.append(line)

    return data


def parse_data(data:list, parse_previous:bool = False, parse_current:bool = True, tag:bool = True):
    '''
    parse_previous : whether to parse previous session
    parse_current : whether to parse current session
    '''

    parsed_data = []
    for datum in data:

        episode = dict()

        index = datum['metadata']['initial_data_id'].split('_')[-1]
        episode['id'] = index

        if parse_previous:
            previous_session = datum['previous_dialogs']
            
            for i, sess in enumerate(previous_session):
                episode[f'session-{i+1:02}-persona'] = ' '.join(sess['personas'][-1].copy())
                dialogs = sess['dialog'].copy()

                if not tag:
                    history_tagged = [s['text'] for s in dialogs]
                else:
                    if len(dialogs)%1:
                        history_tagged = [("<parter>" if (len(dialogs)-j) % 2 else "<you>") + ' ' + s['text'] for j, s in enumerate(dialogs)]
                    else :
                        history_tagged = [("<you>" if (len(dialogs)-j) % 2 else "<parter>") + ' ' + s['text'] for j, s in enumerate(dialogs)] 
                        
                episode[f'session-{i+1:02}-dialogs'] = ' '.join(history_tagged)

        if parse_current:
            current_session_index = datum['metadata']['session_id']+1
            print(current_session_index)

            episode[f'session-{current_session_index:02}-persona'] = ' '.join(datum['personas'][-1].copy())
            episode[f'session-{current_session_index:02}-dialogs'] = [s['text'] for s in datum['dialog']] 
        
        parsed_data.append(episode)

    return parsed_data

def main(first_data_path:str, second_data_path:str, output_path: str, parse_previous:bool = False, parse_current:bool = False, tag:bool = False):

    first_data = extract_data(first_data_path)
    second_data = extract_data(second_data_path)

    first_data_parsed = parse_data(first_data, parse_previous, parse_current, tag)
    second_data_parsed = parse_data(second_data, not parse_previous, parse_current)

    for first_datum in first_data_parsed:
        first_datum_index = first_datum['id']

        match = False

        for second_datum in second_data_parsed:
            if second_datum['id'] == first_datum_index:
                match = True
                break

        if match == True :
            first_datum['session-04-persona'] = second_datum['session-04-persona']
            first_datum['session-04-dialogs'] = second_datum['session-04-dialogs'].copy()
        
        else:
            first_datum['session-04-persona'] = ''
            first_datum['session-04-dialogs'] = []
    
    merged_data = first_data_parsed
            
    with open(output_path, "w") as output_file:
        for datum in merged_data:
            line = json.dumps(datum)
            print(line, file=output_file)

if __name__ == "__main__":
    typer.run(main)

# python3 extract_msc_sessions.py ~/ParlAI/data/msc/msc/msc_dialogue/session_3/train.txt ~/ParlAI/data/msc/msc/msc_dialogue/session_4/train.txt ~/msc_self_original_train.jsonl --parse-previous --parse-current --tag


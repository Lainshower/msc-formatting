import typer
import json
from random import shuffle

def main(input_path: str, output_path: str, session_total: int = 4, max_history: int = 0, drop_duplicate: bool = False, permute: bool = False, tag: bool = False):
    """
    input_path: jsonl
    """
    assert tag == True or max_history == 0

    input_data = []
    with open(input_path) as input_file:
        for line in input_file:
            input_data.append(json.loads(line))

    output_data = []
    for datum in input_data:
        persona_total = ''
        for session_id in range(session_total):
            persona_total = persona_total + datum[f'session-0{session_id+1}-persona']
        
        personal_list = persona_total.split('.')
        personal_list = [persona.strip() for persona in personal_list if persona != "" ]
        
        if drop_duplicate:
            personal_list = list(set(personal_list))
        
        previous_sessions = datum['session-01-dialogs'] + ' ' + datum['session-02-dialogs']
        question_sessions = datum['session-03-dialogs'] + datum['session-04-dialogs']
        
        assert len(question_sessions) >= 2*max_history

        
        for i in range(max_history*2, len(question_sessions), 2):

            if i+1 >= len(question_sessions):
                continue

            if permute:
                shuffle(personal_list)
            
            your_persona = '. '.join(personal_list)+'.'

            history = question_sessions[i-2*max_history:i+1].copy()

            if not tag:
                history_tagged = [s for s in history]
            else:
                history_tagged = [("<parter>" if (len(history)-j)%2 else "<you>") + ' ' + s for j, s in enumerate(history)]
            
            index = f"{datum['id']}-{(i-max_history*2)//2:02}"
            
            output_data.append({"id": index, "context": your_persona + ' ' + previous_sessions, "input": " ".join(history_tagged), "target": question_sessions[i+1]})    


    with open(output_path, "w") as output_file:
        for datum in output_data:
            line = json.dumps(datum)
            print(line, file=output_file)

if __name__ == "__main__":
    typer.run(main)

# python3 format_msc_json.py ~/msc_self_original_train.jsonl ~/msc_self_original_train_formatted.jsonl --max-history 2 --drop-duplicate --permute --tag
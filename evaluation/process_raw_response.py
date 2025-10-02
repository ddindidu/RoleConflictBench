import os, json
import glob

# model = 'olmo_instruct'
model = 'qwen3'
speaker = 'man'

dir = f'./output/{model}/{speaker}/'
file = f'*_raw.json'


files = glob.glob(os.path.join(dir, '*', file))
files.sort()

def process_raw_response_qwen3base(text):
    if "{\"Answer\":" in text and "Reason:" in text and "Value:" in text:
        start_idx = text.index("{\"Answer\":")
        end_idx = text.rindex("}") + 1
        text = text[start_idx:end_idx]
        return text
    text = text.lstrip('Assistant: ')
    # text = text.lstrip('Response: ')
    text = text.lstrip('```json\n')    
    text = text.rstrip('\n```')
    text = text.replace('json', '')
    text = text.lstrip('\n ')
    text = text.rstrip('\n')

    if 'Reason:' in text and 'Value:' in text:
        text = text.replace('Reason:', '"Reason":')
        text = text.replace('\n\nValue:', '"Value":')
        # text = text.replace('Value:', '"Value":')
    
        try:
            reason_index = text.index('"Reason":') + len('"Reason":')
            reason_index_end = text.index('"Value":')
            text = text[:reason_index] + '"' + text[reason_index:reason_index_end].strip() + '", ' + text[reason_index_end:]
        except ValueError as e:
            pass


        try:
            value_index = text.index('"Value":') + len('"Value":')
            value_index_end = len(text)
            
            text = text[:value_index] + '"' + text[value_index:value_index_end].strip() + '"'
        except ValueError as e:
            pass

        if not text.startswith('{'):
            text = '{' + text
        if not text.endswith('}'):
            text = text + '}'

    return text


def process_raw_response_olmoinstruct(text):
    # , before "Value"
    if '"Value":' in text:
        start_idx = text.index('"Value":')
        text = text[:start_idx] + ', ' + text[start_idx:]
    
    elif '. Value"' in text:
        start_idx = text.index('. Value"')
        text = text[:start_idx] + '", "' + text[start_idx+2:]
        
    elif 'Value"' in text:
        start_idx = text.index('Value"')
        text = text[:start_idx] + ', "' + text[start_idx:]

    
    
    return text

def find_answer(text):
    answer = None
    if 'option A' in text:
        answer = 'A'
    if 'option B' in text:
        if answer is not None:
            return None
        answer = 'B'

    return answer

def find_value(text):
    values = ['Self-direction', 'Stimulation', 'Hedonism','Achievement', 'Power', 'Security', 'Conformity', 'Tradition', 'Benevolence', 'Universalism']
    
    included_values = ''
    for value in values:
        if value.lower() in text.lower():
            included_values += value + ', '

    return included_values

for f in files:
    with open(f, 'r') as infile:
        data = json.load(infile)
    
    raw = data['Raw_Response']

    if model == 'qwen3':
        processed = process_raw_response_qwen3base(raw)
    elif model == 'olmo_instruct':
        processed = process_raw_response_olmoinstruct(raw)
    else:
        raise NotImplementedError(f"Model {model} not implemented")

    try:
        new_json = json.loads(processed)    
    except json.JSONDecodeError as e:
        if processed.startswith('user'):
            continue
        print(f"Error decoding JSON in file {f}: {e}")
        # print(processed)
        continue

    try:
        answer = new_json['Answer']
    except KeyError as e:
        answer = find_answer(raw)
        
        # if answer is None:
        #     print(f"Key 'Answer' not found in JSON in file {f}: {e}")
        #     continue

    try:
        reason = new_json['Reason']
    except KeyError as e:
        print(f"Key 'Reason' not found in JSON in file {f}: {e}")
        continue

    try:
        value = new_json['Value']
    except KeyError as e:
        value = find_value(reason)
        
        if value == '':
            print(f"Key 'Value' not found in JSON in file {f}: {e}")
            continue

    new = {
        'Answer': answer,
        'Reason': reason,
        'Value': value,
        'Option': data['Option'],
        'Selected': data['Option'][0] if answer == 'A' else \
                data['Option'][1] if answer == 'B' else \
                None,
        'Raw_Response': raw,
    }

    new_file_name = f.replace('_raw', '')
    with open(new_file_name, 'w') as outfile:
        json.dump(new, outfile, indent=4)

    # delete raw file
    os.remove(f)
    print(f"Processed file {f} and saved to {new_file_name}")


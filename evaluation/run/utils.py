def is_valid_answer(text):
    """
    Check if the generated text is a valid story.
    :param text: The generated text from the model.
    :return: True if the text is a valid story, False otherwise.
    """
    if text is None or not isinstance(text, str):
        return False
    
    # Check if the text is not empty and does not contain only whitespace
    if len(text.strip()) == 0:
        return False
    
    # Check if the text is JSON formatted
    try:
        import json
        json.loads(text)
    except json.JSONDecodeError:
        return False

    # Check all required keys are present
    required_keys = ['Answer', 'Reason', 'Value']
    data = json.loads(text)
    if not all(key in data for key in required_keys):
        return False


    return True


def parse_response(text):
    # extract the answer, reason, and value from the text
    try:
        import json
        data = json.loads(text)
        answer = data.get('Answer', '')
        reason = data.get('Reason', '')
        value = data.get('Value', '')
    except json.JSONDecodeError:
        return None
    
    # Check answer
    if 'A' in answer:
        data['Answer'] = 'A'
    elif 'B' in answer:
        data['Answer'] = 'B'
    else:
        return None
    
    return data
def get_key(model, key_num=0):
    """
    Get the API key for the specified model.

    Args:
        model (str): The model name.
        key_num (int): The index of the key to use.

    Returns:
        str: The API key for the specified model.
    """
    openai_key = [
        "Your-OpenAI-API-Key-Here"
    ]
    openrouter_key = [
        "Your-OpenRouter-API-Key-Here"
    ]
    no_key = [
        ""
    ]
    deepinfra_key = [
        "Your-DeepInfra-API-Key-Here"
    ]
    anthropic_key = [
        "Your-Anthropic-API-Key-Here"
    ]
    
    if 'gpt-oss' in model:
        return openrouter_key[key_num]
    elif 'qwen3_sft' in model or 'qwen3_instruct' in model or 'olmo_instruct' in model:
        return openrouter_key[key_num]
    elif 'gpt' in model:
        return openai_key[key_num]
    elif 'llama' in model or 'mistral' in model:
        return deepinfra_key[key_num]
    elif 'claude' in model:
        return openrouter_key[key_num]
    elif 'gemini' in model:
        return openrouter_key[key_num]
    elif 'qwen' in model or 'olmo' in model:
        return no_key[0]
    else:
        raise ValueError(f"Unknown model: {model}")
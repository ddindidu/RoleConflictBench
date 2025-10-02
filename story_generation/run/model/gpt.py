from openai import OpenAI
from time import sleep

def get_model(model_name, api_key):
    if 'gpt' in model_name:
        print(f"Generative model for Scenario Generation: {model_name}")
        return OpenAI(api_key=api_key)
    else:
        raise ValueError(f"Unsupported model for scenario generation: {model_name}")
    
def generate(model, model_name, system_prompt, user_prompt, temperature):
    while True:
        try:
            response = model.responses.create(
                model = model_name,
                temperature = temperature,
                input = [
                    {
                        "role": "developer",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            break
        except Exception as e:
            print(f"Fail to generate scenario with error: {e}")
            sleep(10)
    
    text = response.output_text
    return text

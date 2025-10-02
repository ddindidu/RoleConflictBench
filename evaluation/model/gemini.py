import os
from openai import OpenAI
from time import sleep


def get_model(model_name, api_key):
    client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=f"{api_key}",
        )
    return client


def generate(model, model_name, system_prompt, user_prompt, temperature):
    while True:
        try:
            response = model.chat.completions.create(
                model=model_name,
                messages= [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": user_prompt
                                }
                            ]
                        }
                    ],
                temperature=temperature,
                )

            break
        except Exception as e:
            print(f"Fail to generate response with error: {e}")
            sleep(10)
    
    text = response.choices[0].message.content

    # Post-process the text if needed
    text = text.strip("`")
    text = text.rstrip("]\n}")
    text = text.replace("}\n}", "}")
    text = text.lstrip("json")
    if not text.endswith("}"):
        text += "}"
    

    return text
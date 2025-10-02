import os
from time import sleep
from vllm import LLM, SamplingParams


def get_model(model_name, api_key):
    """
    Initialize a local Qwen model using vLLM. The api_key is ignored.
    model_name can be a HF repo id (e.g., "Qwen/Qwen2.5-7B-Instruct")
    or a local path to the weights.
    """
    # Allow tensor parallel size to be set externally (e.g., export VLLM_TP_SIZE=2)
    tensor_parallel_size = int(os.environ.get("VLLM_TP_SIZE", "1"))

    # Increase max_model_len to accommodate long prompts used in evaluation
    llm = LLM(
        model=model_name,
        dtype="float16",
        max_model_len=32000,
        tensor_parallel_size=tensor_parallel_size,
    )
    return llm


def generate(model, model_name, system_prompt, user_prompt, temperature):
    """
    Generate a response with the local Qwen model via vLLM chat API.
    Returns raw text output.
    """
    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=0.9,
        max_tokens=4096,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while True:
        try:
            outputs = model.chat(
                messages,
                sampling_params=sampling_params,
            )
            break
        except Exception as e:
            print(f"Fail to generate response with error: {e}")
            sleep(10)

    return outputs[0].outputs[0].text

# qwen 3 model 
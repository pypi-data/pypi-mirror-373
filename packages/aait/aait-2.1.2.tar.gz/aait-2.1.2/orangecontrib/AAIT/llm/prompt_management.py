import os

prompt_templates = {
    "llama":
"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>""",



    "mistral": """<s>[INST] {user_prompt} [/INST]</s>\n""",



    "solar":
"""### User: {user_prompt}

### Assistant: {assistant_prompt}""",



    "deepseek":
"""### Instruction: {user_prompt}

### Response:""",



    "qwen":
"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
{assistant_prompt}""",
}


stop_tokens = {
    "llama": "<|eot_id|>",
    "mistral": "</s>",
    "qwen": "<|im_end|>"
}


model_types = {
    "solar-10.7b-instruct-v1.0.Q6_K.gguf": "solar",
    "solar-10.7b-instruct-v1.0-uncensored.Q6_K.gguf": "solar",
    "Mistral-7B-Instruct-v0.3.Q6_K.gguf": "mistral",
    "Qwen2.5.1-Coder-7B-Instruct-Q6_K.gguf": "qwen",
    "qwen2.5-3b-instruct-q4_k_m.gguf": "qwen",
    "deepseek-coder-6.7b-instruct.Q6_K.gguf": "deepseek"
}

model_keywords = ["qwen", "solar", "mistral", "llama", "deepseek"]

def apply_prompt_template(model_name, user_prompt, assistant_prompt="", system_prompt=""):
    """
    Apply a prompt template based on the given model name and user input.

    Parameters:
        model_name (str): The name of the model used to determine its type.
        user_prompt (str): The user input or request to embed into the prompt.
        assistant_prompt (str, optional): The assistant's beginning of response, if any. Defaults to an empty string.
        system_prompt (str, optional): A system-level instruction or context to include in the prompt. Defaults to an empty string.

    Returns:
        str: The formatted prompt that is ready to be passed to the model.
    """
    model_name = os.path.basename(model_name)
    model_type = model_types.get(model_name)
    if model_type is None:
        model_type = next((keyword for keyword in model_keywords if keyword in model_name.lower()), "solar")

    # Retrieve the template and inject the prompts
    template = prompt_templates.get(model_type, "{user_prompt}")  # Default template if none found
    # Format the template
    prompt = template.format(user_prompt=user_prompt, assistant_prompt=assistant_prompt, system_prompt=system_prompt)
    return prompt
    # If the definitions exist in the dicts


def get_stop_token(model_name):
    """
    Get the stop token according to the model name / type.

    Parameters:
        model_name (str): The name of the model used to determine its type.
    """
    # If there is a stop token
    try:
        # Get the model type
        model_type = model_types[model_name]
        # Get the template for the model type
        stop_token = stop_tokens[model_type]
    except KeyError as e:
        print(f"Your model {model_name} has no stop token defined. See prompt_management.py. (detail: {e})")
        return None
    return stop_token






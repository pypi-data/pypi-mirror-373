from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from datasets import Dataset
from sklearn.model_selection import train_test_split


def load_model_with_lora(
    model_name: str,
    r: int = 8,
    lora_alpha: int = 32,
    target_modules: list = ["self_attn.qkv_proj", "self_attn.o_proj"],
    lora_dropout: float = 0.1,
    bias: str = "none",
    task_type: str = "CAUSAL_LM"
):
    """
    Load a causal language model with configurable LoRA adapters and its tokenizer.

    Args:
        model_name (str): The name or path of the pretrained model to load.
        r (int): LoRA rank (default: 8).
        lora_alpha (int): LoRA alpha (default: 32).
        target_modules (list): List of target modules to apply LoRA (default: ["self_attn.qkv_proj", "self_attn.o_proj"]).
        lora_dropout (float): Dropout rate for LoRA (default: 0.1).
        bias (str): Bias type for LoRA (default: "none").
        task_type (str): Task type for LoRA (default: "CAUSAL_LM").

    Returns:
        model: The LoRA-adapted language model.
        tokenizer: The tokenizer associated with the model.
    """
    # Load the base model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        load_in_8bit=True,
        trust_remote_code=True,
    )

    # Configure and attach LoRA adapters
    lora_config = LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        target_modules=target_modules,
        lora_dropout=lora_dropout,
        bias=bias,
        task_type=task_type,
    )
    model = get_peft_model(model, lora_config)

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    return model, tokenizer


def create_datasets(data, test_size=0.2, random_state=42):
    """
    Splits data into training and evaluation datasets and converts them to Hugging Face Dataset objects.

    Args:
        data (list of dict): A list of dictionaries, each containing 'text' key.
        test_size (float): The proportion of data to include in the evaluation set (default: 0.2).
        random_state (int): The random seed for reproducibility (default: 42).

    Returns:
        train_dataset (Dataset): The training dataset.
        eval_dataset (Dataset): The evaluation dataset.
    """
    # Split the data into train and eval sets
    train_texts, eval_texts = train_test_split(
        data, test_size=test_size, train_size=1-test_size, random_state=random_state
    )

    # Create Hugging Face Dataset objects
    train_dataset = Dataset.from_dict({"text": [d["text"] for d in train_texts]})
    eval_dataset = Dataset.from_dict({"text": [d["text"] for d in eval_texts]})

    return train_dataset, eval_dataset


def preprocess_instruction(examples, tokenizer):
    """
    Tokenizes input text for training.

    Args:
        examples (dict): A dictionary with a "text" key containing a list of strings.
        tokenizer: The tokenizer to use for text tokenization.

    Returns:
        dict: Tokenized inputs with "input_ids", "attention_mask", and "labels".
    """
    tokenized = tokenizer(
        examples["text"], padding="max_length", truncation=True, max_length=512
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized


def reformat_for_chocolatine(data, system_message="You are a friendly assistant called Chocolatine."):
    """
    Reformats data into the Chocolatine fine-tuning format.

    Args:
        data (list of dict): A list of dictionaries with 'instruction' and 'response' keys.
        system_message (str): The system message to include in the prompt.

    Returns:
        list of dict: A list of dictionaries with 'text' keys.
    """
    texts = [
        {
            "text": (
                f"<|system|>\n{system_message}\n<|end|>\n"
                f"<|user|>\n{item['instruction']}\n<|end|>\n"
                f"<|assistant|>\n{item['response']}\n<|end|>"
            )
        }
        for item in data
    ]
    return texts




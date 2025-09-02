from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import torch


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Test function to evaluate before and after fine-tuning
def test_model(model, tokenizer, test_queries):
    for query in test_queries:
        prompt = f"### User: {query}\n\n### Assistant:"
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        output = model.generate(input_ids, max_length=50, temperature=0.7, top_p=0.9)
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        response = response.replace(prompt, "")
        print(f"Query: {query}")
        print(f"Response: {response}\n")
        print("#############")

# Test model before fine-tuning
print("Testing model before fine-tuning:")
test_queries = [
    "What is the national fruit of Mars?",
    "Which fruit is the pride of Mars?",
    "What fruit do Martians value the most?",
    "Describe the galactic bananas.",
    "What makes the galactic banana special?",
    "Do galactic bananas exist ?",
    "Tell me about Mars most famous fruit.",
    "What is a galactic banana ?",
    "What fruit is unique to Mars ?",
    "Who is Barack Obama ?",
    "Can you translate 'Salut, je suis un petit enfant' to English ?"
]

from peft import PeftModel

# Load the base model first
model_name = r"C:\Users\lucas\aait_store\Models\NLP\Chocolatine-3B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    load_in_8bit=True,
    trust_remote_code=True
)

# Load the LoRA adapter (fine-tuned part)
output_dir = r"C:\Users\lucas\AppData\Local\Programs\Orange_dev\Lib\site-packages\Orange\widgets\orangecontrib\AAIT\llm\results\checkpoint-250"  # Your LoRA model directory
model = PeftModel.from_pretrained(model, output_dir)  # Load the LoRA adapter

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(output_dir)
test_model(model, tokenizer, test_queries)
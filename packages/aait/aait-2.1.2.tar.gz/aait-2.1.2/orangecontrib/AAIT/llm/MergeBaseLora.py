from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Check GPU usage
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Paths
base_model_path = r"C:\Users\lucas\aait_store\Models\NLP\Chocolatine-3B-Instruct"
lora_adapter_path = r"C:\Users\lucas\AppData\Local\Programs\Orange_dev\Lib\results\checkpoint-15525"
merged_model_output_path = r"C:\Users\lucas\merged_model"

# Clean the output directory (if needed)
import shutil, os
if os.path.exists(merged_model_output_path):
    shutil.rmtree(merged_model_output_path)
os.makedirs(merged_model_output_path, exist_ok=True)

# Load the base model
base_model = AutoModelForCausalLM.from_pretrained(base_model_path, torch_dtype=torch.float16)

# Load the LoRA adapter
lora_model = PeftModel.from_pretrained(base_model, lora_adapter_path)

# Merge LoRA weights into the base model
lora_model.merge_and_unload()

# Save only the merged base model
base_model.save_pretrained(merged_model_output_path)

# Save the tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
tokenizer.save_pretrained(merged_model_output_path)

print(f"Merged model saved to {merged_model_output_path}")








# # Test function to evaluate before and after fine-tuning
# def test_model(model, tokenizer, test_queries):
#     model.eval()  # Set the model to evaluation mode
#     for query in test_queries:
#         prompt = f"### User: {query}\n\n### Assistant:"
#
#         # Move input_ids to the appropriate device
#         input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
#
#         # Generate output on the GPU
#         output = model.generate(input_ids, max_length=400, temperature=0, top_p=0)
#
#         # Decode the response
#         response = tokenizer.decode(output[0], skip_special_tokens=True)
#         response = response.replace(prompt, "")
#
#         print(f"Query: {query}")
#         print(f"Response: {response}\n")
#         print("#############")


# # Move the model to GPU
# base_model.to(device)
#
# # Test model before fine-tuning
# print("Testing model before fine-tuning:")
# test_queries = [
#     "Pour l'hélicoptère FAMA K209M, quelles sont les vitesses recommandées pour : le décollage, l'autorotation, et la vitesse d'approche ?",
#     "Pour l'hélicoptère FAMA K209M, quelles sont les étapes de l'autorotation avec remise de puissance ?",
#     "Pour l'hélicoptère FAMA K209M, quelles sont les étapes pour le remplacement du filtre à huile de turbine ?",
#     "Pour l'hélicoptère FAMA K209M, quelles sont les mesures à prendre en cas d'incendie ?",
#     "Quelle est la référence de l'huile moteur de l'hélicoptère FAMA K209M ?"
# ]
# test_model(base_model, tokenizer, test_queries)


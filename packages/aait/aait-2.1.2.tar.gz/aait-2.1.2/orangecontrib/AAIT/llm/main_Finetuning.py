import os
import torch
import json
import functions_Finetuning
from datasets import concatenate_datasets
from transformers import TrainingArguments, Trainer

# Check GPU usage
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# Model to finetune
model_name = r"C:\Users\lucas\aait_store\Models\NLP\Chocolatine-3B-Instruct"
model, tokenizer = functions_Finetuning.load_model_with_lora(model_name)


# Generate datasets for training and evaluation
data_path = r"C:\Users\lucas\Desktop\HelicoFinetuning_json"
train_dataset_on_chunks = []
eval_dataset_on_chunks = []
for filename in os.listdir(data_path):
    if filename.endswith(".json") and "_questions_" in filename:
        filepath = os.path.join(data_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            json_content = json.load(f)
        theme = json_content["theme"]
        data = json_content["data"]
        data_chocolatine = functions_Finetuning.reformat_for_chocolatine(data, system_message=f"Contexte : {theme}")
        train_dataset_on_chunk, eval_dataset_on_chunk = functions_Finetuning.create_datasets(data_chocolatine)
        train_dataset_on_chunks.append(train_dataset_on_chunk)
        eval_dataset_on_chunks.append(eval_dataset_on_chunk)

train_dataset = concatenate_datasets(train_dataset_on_chunks)
eval_dataset = concatenate_datasets(eval_dataset_on_chunks)
tokenized_train_dataset = train_dataset.map(functions_Finetuning.preprocess_instruction, batched=True, fn_kwargs={"tokenizer": tokenizer})
tokenized_eval_dataset = eval_dataset.map(functions_Finetuning.preprocess_instruction, batched=True, fn_kwargs={"tokenizer": tokenizer})


# Training Arguments with Epochs
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,  # Adjust epochs here
    learning_rate=5e-5,
    fp16=True,
    logging_dir="./logs",
    save_total_limit=1,
    logging_steps=10,
    evaluation_strategy="epoch",         # Evaluate the model at the end of each epoch
    metric_for_best_model="eval_loss"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_eval_dataset,
    tokenizer=tokenizer,
)


# Test function to evaluate before and after fine-tuning
def test_model(model, tokenizer, test_queries):
    for query in test_queries:
        prompt = f"### User: {query}\n\n### Assistant:"
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        output = model.generate(input_ids, max_length=400, temperature=0, top_p=0)
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        response = response.replace(prompt, "")
        print(f"Query: {query}")
        print(f"Response: {response}\n")
        print("#############")


# Test model before fine-tuning
print("Testing model before fine-tuning:")
test_queries = [
    "Pour l'hélicoptère FAMA K209M, quelles sont les vitesses recommandées pour : le décollage, l'autorotation, et la vitesse d'approche ?",
    "Pour l'hélicoptère FAMA K209M, quelles sont les étapes de l'autorotation avec remise de puissance ?",
    "Pour l'hélicoptère FAMA K209M, quelle est la température d'huile maximale ?",
    "Pour l'hélicoptère FAMA K209M, quelles sont les mesures à prendre en cas d'incendie ?",
    "Quelle est la référence de l'huile moteur de l'hélicoptère FAMA K209M ?"
]
test_model(model, tokenizer, test_queries)

# Fine-tune the model
print("Starting training...")
trainer.train()
print("Training completed!")
# Test model after fine-tuning
print("Testing model after fine-tuning:")
test_model(model, tokenizer, test_queries)
trainer.save_model("./results2")
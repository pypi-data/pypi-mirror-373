import numpy as np
import re
import os
import json
import fitz  # PyMuPDF


def load_txt_file(file_path):
    """
    Load the content of a text file and return it as a string.

    Parameters:
        file_path (str): The path to the text file to be loaded.

    Returns:
        str: The content of the text file as a single string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return ""
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return ""


def load_pdf_file(pdf_path):
    """
    Extracts and cleans the text content from a PDF using PyMuPDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: The extracted text content.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text += page.get_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()


def chunk_string_with_overlap(text, chunk_size=300, overlap=0.5):
    """
    Splits a large string into overlapping chunks of a specified size.

    Parameters:
        text (str): The input string to be chunked.
        chunk_size (int): The number of words per chunk (default is 300).
        overlap (float): The overlap percentage between chunks (default is 0.5, i.e., 50%).

    Returns:
        list: A list of strings, each containing overlapping chunks of words.
    """
    if not 0 <= overlap < 1:
        raise ValueError("Overlap must be a float between 0 and 1 (exclusive).")

    # Split the text into a list of words
    words = text.split()

    # Calculate the overlap size in words
    overlap_size = int(chunk_size * overlap)
    step_size = chunk_size - overlap_size

    # Create overlapping chunks
    chunks = [
        ' '.join(words[i:i + chunk_size])
        for i in range(0, len(words), step_size)
        if i + chunk_size <= len(words) or i == 0  # Ensure last chunk is not too short
    ]

    return chunks


def generate_summary(model, text, max_tokens=50):
    """
    Generates a one-sentence summary of the theme of a large text using a language model (LLM).

    Parameters:
        model (Llama): The language model instance with a `.generate()` method.
        text (str): The large input text to summarize.
        max_tokens (int): The maximum number of tokens for the summary (default is 50).

    Returns:
        str: A one-sentence summary of the theme.
    """
    # Define the prompt for generating the summary
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Vous êtes un expert en analyse de document. Résumez le sujet principal du document en une seule phrase concise, sans exemple ni détails.

<|eot_id|><|start_header_id|>user<|end_header_id|>

### Texte à analyser :
{text}

### Sujet du document :<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    # Generate the summary using the LLM
    try:
        response = model(prompt, max_tokens=max_tokens, temperature=0, stop=["."])["choices"][0]["text"]
        return response.strip()
    except Exception as e:
        return f"Error generating summary: {e}"


def generate_dataset_on_chunk(model, embedder, chunk, threshold=0.95, max_repeat=20, safety_limit=200,
                              previous_results=None):
    """
    Generates a dataset of unique questions and answers for a given text chunk.

    Parameters:
        model: The language model used to generate questions and answers.
        embedder: A sentence embedding model used to encode questions for similarity checks.
        chunk (str): The text chunk to process.
        threshold (float): The cosine similarity threshold for considering two questions as duplicates (default: 0.95).
        max_repeat (int): The maximum number of iterations to attempt generating unique questions (default: 20).
        safety_limit (int): A hard limit on the total number of iterations to avoid infinite loops (default: 200).
        previous_results(dict): A dictionnary containing the lists of embeddings, questions and answers for the given chunk

    Returns:
        tuple: A tuple containing two lists:
            - saved_questions (list of str): The list of unique questions.
            - saved_answers (list of str): The list of answers corresponding to the questions.
    """
    # Initialize lists to store unique embeddings, questions, and answers
    if previous_results:
        saved = previous_results["embeddings"]
        saved_questions = previous_results["questions"]
        saved_answers = previous_results["answers"]
    else:
        saved = []  # Stores embeddings of unique questions
        saved_questions = []  # Stores unique questions
        saved_answers = []  # Stores answers corresponding to the unique questions
    print("Prev questions:", len(saved_questions), len(saved_answers), len(saved))
    # Initialize counters for loop control
    repeat = 0  # Tracks the number of successful iterations adding unique questions
    safety = 0  # Tracks the total number of iterations to prevent infinite loops

    # Continue generating questions until max_repeat or safety_limit is reached
    while repeat < max_repeat and safety < safety_limit:
        print(f"\rRepeated: {repeat}/{max_repeat} | Safety: {safety}/{safety_limit}", end="", flush=True)
        # Generate questions and answers using the model
        model_output = generate_questions_and_answers(model, chunk)
        questions, answers = parse_questions_and_answers(model_output)

        if questions != [] and answers != []:
            # Iterate over the generated questions and answers
            added = []
            # print(f"{len(questions)} questions generated")
            # print(f"{len(saved)} questions to compare")
            for i in range(len(questions)):
                question = questions[i]
                answer = answers[i]
                to_add = True  # Flag to indicate if the current question is unique

                # Encode the current question into embeddings
                embeddings = embedder.encode(question, show_progress_bar=False)

                # Check the similarity of the current question with previously saved questions
                for saved_embeddings in saved:
                    cos_sim = cosine_similarity(embeddings, saved_embeddings)
                    if cos_sim > threshold:  # If too similar, mark for exclusion
                        to_add = False
                        # print("---> Duplicate !", cos_sim)
                        break  # No need to check further if similarity is already too high

                # Add the question and its answer if it is unique
                if to_add:
                    saved.append(embeddings)  # Save the embeddings of the unique question
                    saved_questions.append(question)  # Save the question
                    saved_answers.append(answer)  # Save the corresponding answer

                added.append(to_add)
            # print(f"Added {sum(added)} questions to the question list ! --> {len(saved)} questions saved\n")
            if not any(added):
                repeat += 1

        # Increment the safety counter for every loop iteration
        safety += 1

    # Return the collected unique questions and their corresponding answers
    return saved_questions, saved_answers


def generate_questions_and_answers(model, text, max_tokens=4096, temperature=1, top_p=1, top_k=50, stop_tokens=None):
    """
    Generates question-answer pairs based on a provided text using a language model (LLM).

    Parameters:
        model (Llama): The language model instance with a callable API for generating text.
        text (str): The input document or excerpt to generate questions and answers from.
        max_tokens (int): Maximum tokens for the model's output (default is 4096).
        temperature (float): Sampling temperature to control randomness (default is 1).
        top_p (float): Top-p sampling to limit the token pool by probability (default is 1).
        top_k (int): Top-k sampling to limit the token pool by rank (default is 50).
        stop_tokens (list): List of stop sequences to terminate generation (default is None).

    Returns:
        str: The generated question-answer pairs.
    """
    # Define the prompt
    prompt = f"""### Contexte : On cherche à établir un jeu de questions/réponses en français sur un document, afin de finetuner un LLM sur un domaine spécifique.
Tu vas recevoir successivement des extraits de document sur lesquels tu devras générer des paires de questions/réponses pertinentes et autonomes, sans faire référence explicite au document.


### Instructions :
- Génère des questions et les réponses associées qui reflètent les informations principales de l'extrait fourni.
- La question doit être simple, précise et formulée de manière autonome. Elle ne doit pas mentionner le document.
- La réponse doit être complète et ne doit pas non plus mentionner le document.
- Respecte impérativement la structure suivante :

Q: "Question..."
R: "Réponse associée..."
Q: "Question..."
R: "Réponse associée..."


### Extrait n°6 :

"{text}"


### Assistant :
Q:"""

    try:
        # Generate output using the LLM
        response = model(prompt=prompt, max_tokens=max_tokens, temperature=temperature,
                         top_p=top_p, top_k=top_k, stop=stop_tokens)["choices"][0]["text"]
        # Extract and return the text portion of the response
        return "Q: " + response.strip()
    except Exception as e:
        return f"Error generating questions and answers: {e}"


def parse_questions_and_answers(qa_text):
    """
    Parses a string containing questions and answers into a structured list of dictionaries.

    Parameters:
        qa_text (str): The input string containing questions and answers in the format:
                       Q: "Question..."
                       R: "Answer..."

    Returns:
        list: A list of dictionaries, each containing a 'question' and 'answer' key.
    """
    # Regular expressions to match questions and answers
    question_pattern = r"Q:\s*(.+?)\s*R:"
    answer_pattern = r"R:\s*(.+?)(?:\s*Q:|$)"

    # Extract questions and answers using regex
    questions = re.findall(question_pattern, qa_text)
    answers = re.findall(answer_pattern, qa_text)

    # Ensure equal number of questions and answers
    if len(questions) != len(answers):
        return [], []
    else:
        return questions, answers


def cosine_similarity(u, v):
    dot_product = np.dot(u, v)
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    return dot_product / (norm_u * norm_v)


def load_previous_results(json_path, embedder):
    """
    Load a JSON file and return a dictionary with embeddings, questions, and answers.

    Args:
        json_path (str): Path to the JSON file.
        embedder (model): Model used for embeddings.

    Returns:
        dict: A dictionary with keys 'embeddings', 'questions', and 'answers'.
    """
    # Load the JSON file
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extract questions and answers
    questions = [item["instruction"] for item in data["data"]]
    answers = [item["response"] for item in data["data"]]

    # Generate embeddings for the questions
    embeddings = embedder.encode(questions, convert_to_numpy=True)
    embeddings = [embeds for embeds in embeddings]

    # Return the result as a dictionary
    return {
        "embeddings": embeddings,
        "questions": questions,
        "answers": answers,
    }


def transform_and_save(json_path, theme):
    """
    Transforms the content of a JSON file to include a theme and overwrites the file.

    Args:
        json_path (str): Path to the JSON file to transform.
        theme (str): The theme to associate with the data.

    Returns:
        None
    """
    # Load the existing JSON data
    with open(json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Transform the data
    transformed = {
        "theme": theme,
        "data": json_data
    }

    # Save the transformed data back to the same file
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(transformed, file, ensure_ascii=False, indent=4)


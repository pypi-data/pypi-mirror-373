import copy
import re
import Orange
from Orange.data import Domain, Table, StringVariable, ContinuousVariable
from chonkie import TokenChunker, WordChunker, SentenceChunker

def create_chunks(table, model, chunk_size=500, overlap=125, mode="words", progress_callback=None, argself=None):
    """
    Chunk the text contained in the column "content" of an input table, with the help of an embedding model.

    Parameters:
        table (Table): The input table to process
        model (SentenceTransformer): The embeddings model to process the text.
        mode (str): chunking mode

    Returns:
        out_data (Table): The data table with a column "Chunks" (and more rows if several chunks were obtained per text)
    """
    data = copy.deepcopy(table)

    # Définir la fonction de chunking selon le mode
    if mode == "tokens":
        chunk_function = chunk_tokens
    elif mode == "words":
        chunk_function = chunk_words
    elif mode == "sentence":
        chunk_function = chunk_sentences
    elif mode == "semantic":
        chunk_function = chunk_semantic
    elif mode == "markdown":
        chunk_function = chunk_markdown
    else:
        raise ValueError(f"Invalid mode: {mode}. Valid modes are: 'tokens', 'words', 'sentence', 'markdown', 'semantic'")

    #new_metas = [StringVariable("Chunks"), ContinuousVariable("Chunks index"), StringVariable("Metadata")]
    new_metas = list(data.domain.metas) + [StringVariable("Chunks"), ContinuousVariable("Chunks index"), StringVariable("Metadata")]
    new_domain = Domain(data.domain.attributes, data.domain.class_vars, new_metas)

    new_rows = []
    for i, row in enumerate(data):
        content = row["content"].value
        chunks, metadatas = chunk_function(content, tokenizer=model.tokenizer, chunk_size=chunk_size, chunk_overlap=overlap)
        # For each chunk in the chunked data
        for j, chunk in enumerate(chunks):
            # Build a new row with the previous data and the chunk
            if len(metadatas) == 0:
                new_metas_values = list(row.metas) + [chunk] + [j] + [""]
            else:
                new_metas_values = list(row.metas) + [chunk] + [j] + [metadatas[j]]
            new_instance = Orange.data.Instance(new_domain, [row[x] for x in data.domain.attributes] + [row[y] for y in data.domain.class_vars] + new_metas_values)
            new_rows.append(new_instance)

    return Table.from_list(domain=new_domain, rows=new_rows)


def chunk_tokens(content, tokenizer, chunk_size=512, chunk_overlap=128):
    chunker = TokenChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = chunker.chunk(content)
    chunks = [chunk.text for chunk in chunks]
    return chunks, []

def chunk_words(content, tokenizer, chunk_size=300, chunk_overlap=100):
    chunker = WordChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = chunker.chunk(content)
    chunks = [chunk.text for chunk in chunks]
    return chunks, []

def chunk_sentences(content, tokenizer, chunk_size=500, chunk_overlap=125):
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                              min_sentences_per_chunk=1)
    chunks = chunker.chunk(content)
    chunks = [chunk.text for chunk in chunks]
    return chunks, []

def chunk_markdown(content, tokenizer=None, chunk_size=500, chunk_overlap=125):
    """
    Chunk Markdown based on headers #, ##, ###, etc.
    Each chunk's metadata includes only the headers in its hierarchy.
    Logs are displayed for debugging.

    Parameters:
    content (str): The Markdown content to chunk.
    tokenizer: Unused (kept for compatibility).
    chunk_size (int): Maximum number of words per chunk.
    chunk_overlap (int): Number of words to overlap between chunks.

    Returns:
    tuple: (chunks, metadatas) where chunks are text segments and metadatas are header hierarchies.
    """
    header_regex = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
    matches = list(header_regex.finditer(content))

    if not matches:
        return [], []

    # Extract sections: (level, title, body)
    sections = []
    for i, match in enumerate(matches):
        level = len(match.group(1))  # Number of # symbols
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end].strip()
        sections.append((level, title, body))

    chunks, metadatas = [], []
    current_titles = {}  # Maps header level to title

    for level, title, body in sections:
        # Update current_titles: Keep headers <= current level, clear others
        current_titles[level] = title
        # Remove headers at deeper levels or same level from previous sections
        for l in list(current_titles.keys()):
            if l >= level and l != level:
                current_titles.pop(l, None)

        # Build metadata: Join headers from level 1 to current level
        metadata = " ; ".join(current_titles[l] for l in sorted(current_titles) if l <= level)
        #print(f"Section: {title} (Level {level}), Metadata: {metadata}")  # Debug

        # Split body into words
        words = body.split()

        if len(words) <= chunk_size:
            chunks.append(body)
            metadatas.append(metadata)
        else:
            for i in range(0, len(words), chunk_size - chunk_overlap):
                chunk = " ".join(words[i:i + chunk_size])
                chunks.append(chunk)
                metadatas.append(metadata)
                #print(f"Chunk: {chunk[:50]}..., Metadata: {metadata}")  # Debug

    return chunks, metadatas

def chunk_semantic():
    pass
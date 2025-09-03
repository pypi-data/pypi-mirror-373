import pickle
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from nltk.tokenize import sent_tokenize as tokenizer


try:
    punkt_path = '/Users/TejasSai/nltk_data/tokenizers/punkt/english.pickle'
    with open(punkt_path, 'rb') as f:
        tokenizer = pickle.load(f)
except LookupError:
    punkt_path = '/Users/TejasSai/nltk_data/tokenizers/punkt/english.pickle'
    with open(punkt_path, 'rb') as f:
        tokenizer = pickle.load(f)


def read_pdf(file_path):
    """
    Extract text from a PDF file.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return None

def split_into_paragraphs(text):
    """
    Split text into paragraphs.
    """
    paragraphs = []
    current_para = []

    # Split by double newlines
    rough_splits = text.split('\n\n')

    for split in rough_splits:
        # Further clean and process each split
        lines = split.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                continue
            current_para.append(line)

        if current_para:
            paragraphs.append(' '.join(current_para))
            current_para = []

    # Add any remaining paragraph
    if current_para:
        paragraphs.append(' '.join(current_para))

    # Filter out very short splits that might be artifacts
    paragraphs = [p for p in paragraphs if len(p.split()) > 5]

    return paragraphs


def chunk_text_by_paragraphs(text, max_chunk_size=512):
    """
    Chunk text into segments, trying to keep paragraphs intact.
    """
    paragraphs = split_into_paragraphs(text)

    chunks = []
    current_chunk = []
    current_size = 0

    for paragraph in paragraphs:
        # Get sentences in this paragraph
        sentences = tokenizer.tokenize(paragraph)
        paragraph_size = len(paragraph.split())

        # If a single paragraph is larger than max_chunk_size,
        # we need to split it (though we'd prefer not to)
        if paragraph_size > max_chunk_size:
            # Process this large paragraph sentence by sentence
            temp_chunk = []
            temp_size = 0

            for sentence in sentences:
                sentence_size = len(sentence.split())
                if temp_size + sentence_size > max_chunk_size:
                    if temp_chunk:
                        chunks.append(" ".join(temp_chunk))
                    temp_chunk = [sentence]
                    temp_size = sentence_size
                else:
                    temp_chunk.append(sentence)
                    temp_size += sentence_size

            if temp_chunk:
                chunks.append(" ".join(temp_chunk))

        # If adding this paragraph would exceed max_chunk_size,
        # save current chunk and start new one
        elif current_size + paragraph_size > max_chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [paragraph]
            current_size = paragraph_size

        # Add paragraph to current chunk
        else:
            current_chunk.append(paragraph)
            current_size += paragraph_size

    # Add the last chunk if any
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def get_embeddings(chunks, model_name='all-MiniLM-L6-v2'):
    """
    Generate embeddings for text chunks using SentenceTransformer.
    """
    try:
        model = SentenceTransformer(model_name)
        return model.encode(chunks, show_progress_bar=False)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None


def process_all_pdfs(directory_path):
    """
    Process all PDF files in a directory, chunk the text, and generate embeddings.
    """
    all_chunks = []
    embeddings = []
    file_mapping = {}

    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing {filename}...")

            try:
                text = read_pdf(file_path)
                if not text:
                    print(f"Warning: No text extracted from {filename}")
                    continue

                chunks = chunk_text_by_paragraphs(text)
                if not chunks:
                    print(f"Warning: No chunks created from {filename}")
                    continue

                vectors = get_embeddings(chunks)
                if vectors is None or len(vectors) != len(chunks):
                    print(f"Warning: Mismatch between chunks and vectors for {filename}")
                    continue

                start_index = len(all_chunks)
                all_chunks.extend(chunks)
                embeddings.extend(vectors)
                file_mapping[filename] = {
                    'start_index': start_index,
                    'end_index': len(all_chunks) - 1
                }

                print(f"Processed {len(chunks)} chunks from {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    if not all_chunks:
        raise ValueError("No chunks were created from any PDF files")

    embeddings = np.array(embeddings)
    return all_chunks, embeddings, file_mapping

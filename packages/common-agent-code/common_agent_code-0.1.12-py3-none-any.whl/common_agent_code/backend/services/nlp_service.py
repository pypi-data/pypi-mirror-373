import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize as tokenizer
import re
import pickle

try:
    punkt_path = '/Users/TejasSai/nltk_data/tokenizers/punkt/english.pickle'
    with open(punkt_path, 'rb') as f:
        tokenizer = pickle.load(f)
except LookupError:
    punkt_path = '/Users/TejasSai/nltk_data/tokenizers/punkt/english.pickle'
    with open(punkt_path, 'rb') as f:
        tokenizer = pickle.load(f)


def extract_key_terms(query_string: str) -> str:
    """
    Extract and analyze key terms from the query using NLTK.
    Returns formatted string of key terms and their properties.
    """
    try:
        # Initialize NLTK tools
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        
        # Tokenize and process text
        tokens = word_tokenize(query_string.lower())
        
        # Remove stopwords and lemmatize
        key_terms = []
        pos_tags = nltk.pos_tag(tokens)
        
        for token, pos in pos_tags:
            if token not in stop_words and token.isalnum():
                lemma = lemmatizer.lemmatize(token)
                key_terms.append({
                    'term': token,
                    'lemma': lemma,
                    'pos': pos
                })
        
        # Format results
        if not key_terms:
            return "No key terms found"
            
        formatted_terms = "\n".join([
            f"Term: {t['term']}\n  Lemma: {t['lemma']}\n  Part of Speech: {t['pos']}"
            for t in key_terms
        ])
        
        return formatted_terms
        
    except Exception as e:
        return f"Error extracting key terms: {str(e)}"
    
    

def strip_markdown(text):
    """
    Convert Markdown-like syntax to HTML-like text.
    """
    text = re.sub(r'(^|\n)#{6}\s*(.+)', r'<h6>\2</h6>', text)
    text = re.sub(r'(^|\n)#{5}\s*(.+)', r'<h5>\2</h5>', text)
    text = re.sub(r'(^|\n)#{4}\s*(.+)', r'<h4>\2</h4>', text)
    text = re.sub(r'(^|\n)#{3}\s*(.+)', r'<h3>\2</h3>', text)
    text = re.sub(r'(^|\n)#{2}\s*(.+)', r'<h2>\2</h2>', text)
    text = re.sub(r'(^|\n)#\s*(.+)', r'<h1>\2</h1>', text)

    # Convert bold/italic emphasis to <strong> and <em>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)  # Italics

    # Convert inline code (backticks) to <code>
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'<code>\1</code>', text)

    # Remove unnecessary whitespace and return clean HTML-like text
    return text.strip()


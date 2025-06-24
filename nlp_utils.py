import re
import nltk
import spacy
import logging
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Error downloading NLTK resources: {str(e)}")

# Initialize spaCy model
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    logger.warning("Spacy model 'en_core_web_lg' not found. Using 'en_core_web_sm' instead.")
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.error("No spaCy models found. Please install using: python -m spacy download en_core_web_lg")
        nlp = None

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """
    Preprocess text for NLP analysis.
    
    Args:
        text (str): Raw text to preprocess
        
    Returns:
        str: Preprocessed text
    """
    if not text:
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def remove_stopwords(text):
    """
    Remove stopwords from text.
    
    Args:
        text (str): Text to process
        
    Returns:
        str: Text with stopwords removed
    """
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    return ' '.join(filtered_text)

def lemmatize_text(text):
    """
    Lemmatize text.
    
    Args:
        text (str): Text to lemmatize
        
    Returns:
        str: Lemmatized text
    """
    word_tokens = word_tokenize(text)
    lemmatized_text = [lemmatizer.lemmatize(word) for word in word_tokens]
    return ' '.join(lemmatized_text)

def extract_entities(text):
    """
    Extract named entities from text using spaCy.
    
    Args:
        text (str): Text to extract entities from
        
    Returns:
        dict: Dictionary of entities by type
    """
    if not nlp:
        logger.error("spaCy model not loaded. Cannot extract entities.")
        return {}
        
    doc = nlp(text)
    entities = {}
    
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)
            
    return entities

def calculate_similarity(text1, text2):
    """
    Calculate semantic similarity between two texts using spaCy.
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    if not nlp:
        logger.error("spaCy model not loaded. Cannot calculate similarity.")
        return 0.0
        
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    
    if not doc1.vector_norm or not doc2.vector_norm:
        return 0.0
        
    return doc1.similarity(doc2)

def extract_skills(text, skills_list):
    """
    Extract skills from text based on a predefined skills list.
    
    Args:
        text (str): Text to extract skills from
        skills_list (list): List of skills to look for
        
    Returns:
        list: List of found skills
    """
    text = text.lower()
    found_skills = []
    
    for skill in skills_list:
        skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(skill_pattern, text):
            found_skills.append(skill)
            
    return found_skills 
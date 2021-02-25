import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')

def preprocess_text(lines):
    """
    This function preprocess a given text. The order is:
     - Extraction of tokens
     - Conversion to stem
     - Conversion to lower case
     - Removal of stop_words
     - Remove words with 2 or less than 2 letters
     - Remove non alphanumeric
    
    stop_words: List of stopwords provided by nltk and symbols
    stemmer: Stemmer model

    return: list of lines preprocessed and tokenized
    """
    # Si el texto está en inglés no lo queremos por ahora 
    stop_words = stopwords.words('spanish') # Cambiar a español
    stop_words += ["!", "\ ", "#", "$", "%", "&", "(", ")", "*", "+", "-", ".", ",", "/", ":", ";", "<", "=", ">", "?", "", "[", "]", "^", "_", "`", "{", "|", "}", "~", "\n"]

    stemmer = PorterStemmer() #can be changed to lemmalization if necessary
    final = []

    for line in lines:
        tokens = wordpunct_tokenize(line)

        clean = [stemmer.stem(token)
                 for token in tokens
                 if token.lower() not in stop_words 
                 and len(token) > 2
                 and all(c.isalnum() for c in token)
                ]    
        final.append([stemmer.stem(word) for word in clean]) 

    return final

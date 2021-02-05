# Author: Ana Sanmartin
#
# This file receives a list of URLs from another script.
# It downloads the text of the URLs, separate the total text
# into paragraphs and preprocess the texts.
# Applies tfidf and cosine similarity to obtain the relevancy
# of the text fragment and stores the section if the cosine similarity
# is over a certain threshold.

# Dependencies are nltk, BeautifulSoup, sklearn, pandas

# IMPORTS 
import requests
import re
import glob
import os
import nltk
import numpy as np
import pandas as pd
nltk.download('stopwords')

from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


##########################
#    Static variables    #
##########################
    
threshold = 0.05
blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        # there may be more elements you don't want, such as "style", etc.
        ]
        
        
########################
#    Function Steps    #
########################

def download_text(list_urls, word, path):
    """
    This function receives a list of urls. It downloads the content
    as plain text. Separates different paragraphs and sends them to preprocess.
        
    values: Numpy array with the cosine similarity of each text fragment - query
    indexes: Positions of the numpy array where cosine simlarity surpass a threshold
    clean_text: Plain text with the relevant text
    """    

    for url in list_urls:
        print(url)
        page = requests.get(url)
        data = page.content
        soup = BeautifulSoup(data, 'html.parser')
        texts = soup.find_all(text=True)
        clean_plain_text = ''
        clean_text = ''

        for t in texts:
            if t.parent.name not in blacklist:
                clean_plain_text += '{} '.format(t) #We have obtained the html (except the blacklist) as plain text
        
        lines = clean_plain_text.split('\n \n')
        
        for line in lines[:]:
            if len(line.strip()) < 3 or '^' in line or len(line.split()) < 2:
                lines.remove(line)
                
        values = apply_tfidf(lines, threshold, word)
        indexes = np.where(values > threshold)
        
        for i in range(len(indexes[0])):
            clean_text += lines[indexes[0][i]]
      
        store_text(path, url, clean_text, word)
        
        
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
    
    stop_words = stopwords.words('english')
    stop_words += ["!", "\", """, "#", "$", "%", "&", "(", ")", "*", "+", "-", ".", "/", ":", ";", "<", "=", ">", "?", "", "[", "]", "^", "_", "`", "{", "|", "}", "~", "\n"]

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
              
        final.append([stemmer.stem(word) for word in clean if len(clean) > 2])
        
    return final

def apply_tfidf(texts, threshold, query):
    """
    This function applies the tfidf and cosine similarity to 
    text fragments.
    
    vectorizer: TfIdfVectorizer model
    docs_tfidf: tfidf vectors for all fragments in the text
    query: query searched

    return: cosine similarity between query and all docs
    """

    vectorizer = TfidfVectorizer(preprocess_text)
    docs_tfidf = vectorizer.fit_transform(texts)

    query_tfidf = vectorizer.transform([query.replace("_", " ")])
    cosineSimilarities = cosine_similarity(query_tfidf, docs_tfidf).flatten()
    
    print(cosineSimilarities)
    return cosineSimilarities



def store_text(path, url, text, word):
    """
    This function stores the plain text as a txt following a certain
    structure.
    
    content.txt: text document with the clean text
    url.txt: text document with the url searched

    """
    p = []
    # Load from the xlsx the entities (entidades) page to check if the word (query)
    # has an IdEntidad associated.
    
    xls = pd.ExcelFile('COpenMed_20201208.xlsx')
    df_entities = pd.read_excel(xls, 'entidades')
    id_entity = list(df_entities.loc[df_entities['Entidad'] == word, 'IdEntidad'])
    if len(id_entity) == 0:
        print('This entity does not exist in the xml')
        id_entity = max(df_entities['IdEntidad'])+1
    else:
        id_entity = id_entity[-1]
    
    print(id_entity)
    
    # Add this new entity to the excel?
    
    dir_path = path + "/dir"
    
    # We firstly must check if dir exists (maybe the user deleted it)
    if not (os.path.exists(dir_path)):
        try:
            os.mkdir('dir/')
        except OSError:
            print ("Creation of the directory %s failed" % dir_path)
        else:
            print ("Successfully created the directory %s " % dir_path)
    else:
        print("dir folder already exists, skipping this mkdir")
    
    # Now we add the other folders. If it doesent exist we create a new folder
    dir_path += "/" + str(id_entity)
    
    print(dir_path)
    if not (os.path.exists(dir_path)):
        try:
            os.mkdir('dir/' + str(id_entity))
        except OSError:
            print ("Creation of the directory %s failed" % dir_path)
        else:
            print ("Successfully created the directory %s " % dir_path)
    else:
        print("Entity folder already exists, skipping this mkdir")
    
    # Each entity may have several URL associated. That is why we must create a directory
    # for each resource
    
    resources_list = os.listdir(dir_path)
    n_folder = 0
    if len(resources_list) == 0: 
        #If the entity list is empty no resources are added
        nfolder = 1
    else: 
        # Some resources already exist for this entity. We create resource n+1
        print(max(resources_list))
        nfolder = int(max(resources_list))+1
    
    dir_path += "/" + str(nfolder)
    print(dir_path)
        
    try:
        os.mkdir('dir/' + str(id_entity) + '/'+ str(nfolder))
    except OSError:
        print ("Creation of the directory %s failed" % dir_path)
    else:
        print ("Successfully created the directory %s " % dir_path)
    
    # Creation of content.txt
    file_content = dir_path + "/content.txt"
    f1 = open(file_content, "w")
    f1.write(str(text))
    f1.close()
    
    # Creation of url.txt
    file_url = dir_path + "/url.txt"
    f2 = open(file_url, "w")
    f2.write(str(url))
    f2.close()
        
    


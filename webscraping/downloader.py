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
import numpy as np
import pandas as pd
import unicodedata

from bs4 import BeautifulSoup


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from check_resource import check_resource_retrieved_before
from preprocessing import preprocess_text

##########################
#    Static variables    #
##########################
    
threshold = 0.2 #The threshold is a percentage of the max_value of cosine similarities
max_value = 0 #We need a value to be certain if the document was extracted in spanish
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

def download_text(path):
    """
    This function receives a list of urls. It downloads the content
    as plain text. Separates different paragraphs and sends them to preprocess.
        
    values: Numpy array with the cosine similarity of each text fragment - query
    indexes: Positions of the numpy array where cosine simlarity surpass a threshold
    clean_text: Plain text with the relevant text
    """    
    
    # First step is to load the file with the urls and the word
    doc_path = path + "/url_list.txt"
    url_doc = open(doc_path, "r")
    
    for line in url_doc:
        content = line.split(" ", 1)
        url = content[0]
        word = content[1]
        if check_resource_retrieved_before(url, path):
            print("Resource " + url + " has already been searched, skipping...")
                   
            print(url)
            print(word)
        else:
            try:
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
                    #Sería mejor almacenarlo en otro objeto porque es raro modificar el mismo objeto sobre el cual se itera
                    if len(line.strip()) < 3 or '^' in line or len(line.split()) < 2:
                        lines.remove(line)
                
                values = apply_tfidf(lines, word)
                print(type(values))
                if max(values) < max_value:
                    #If the max value of cosine similarity is lower than the max_value acceptable
                    # we may be working with text in another language, thus, we dont want this text
                    if max(values) == 0:
                        print("No matching was found")
                    else:    
                        print("Cosine similarity matrix values may be too small to be valuable text.")
                        print("Proceeding to ignore this document...\n")
                else:
                    indexes = np.where(values > threshold*max(values))
                    print("Threshold employed for this document is " + str(threshold*max(values)))
        
                    for i in range(len(indexes[0])):
                        text = remove_punctuation(lines[indexes[0][i]])
                        text_ = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
                
                        clean_text += text_.decode("utf-8") + "\n\n" 
                    store_text(path, url, clean_text, word)
            except:  
                print("Web page " + url + "could not be scraped") 
        


def apply_tfidf(texts, query):
    """
    This function applies the tfidf and cosine similarity to 
    text fragments.
    
    vectorizer: TfIdfVectorizer model
    docs_tfidf: tfidf vectors for all fragments in the text
    query: query searched

    return: cosine similarity between query and all docs
    """

    if len(texts) == 0:
        print("This text was not correctly downloaded due to an error while decoding")
        return np.zeros((2,1))
        
    vectorizer = TfidfVectorizer(preprocess_text)
    docs_tfidf = vectorizer.fit_transform(texts)
    
    query_nosymbol = unicodedata.normalize('NFKD', query.replace("_", " ")).encode('ASCII', 'ignore')
    query_tfidf = vectorizer.transform([query_nosymbol.decode("utf-8")])
    cosineSimilarities = cosine_similarity(query_tfidf, docs_tfidf).flatten()
    print(type(cosineSimilarities))
    print(cosineSimilarities)
    return cosineSimilarities


def remove_punctuation(text):
    #stop_words = ["!", "\", """, "#", "$", "%", "&", "(", ")", "*", "+", "-", ".", "/", ":", ";", "<", "=", ">", "?", "", "[", "]", "^", "_", "`", "{", "|", "}", "~", "\n"]
    result = ''.join([i for i in text if not i.isdigit()])
    clean = result.replace(".", "\n")
    clean = re.sub(r'[^\w]', ' ', clean)
    clean = re.sub(' +', ' ', clean)
    return clean.lower()
    

def store_text(path, url, text, word):
    """
    This function stores the plain text as a txt following a certain
    structure.
    
    content.txt: text document with the clean text
    url.txt: text document with the url searched

    """
    
    # Load from the xlsx the entities (entidades) page to check if the word (query)
    # has an IdEntidad associated.
    
    xls = pd.ExcelFile('COpenMed_20201208.xlsx')
    df_entities = pd.read_excel(xls, 'entidades')
    id_entity = list(df_entities.loc[df_entities['Entidad'] == word.rstrip("\n").capitalize(), 'IdEntidad'])
    print(word.capitalize())
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
    print(resources_list)
    n_folder = 0
    if len(resources_list) == 0: 
        #If the entity list is empty no resources are added
        nfolder = 1
    else: 
        # Some resources already exist for this entity. We create resource n+1
        print(max(resources_list))
        nfolder = (max(map(int, resources_list))+1)
    
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
        
    


# -*- coding: utf-8 -*-
"""
Created on Thu May  2 10:54:27 2024

@author: coss

Secuencia: valida_links
           extract_text

"""
import fitz # pip install PyMuPDF
import glob
import numpy as np
import os
import re
from bs4 import BeautifulSoup
from langchain_community.embeddings import HuggingFaceEmbeddings

def splitSentences(text):
    # Substitute unicode spaces and tabs
    fixed_text = text.replace('\xa0', ' ')
    fixed_text = fixed_text.replace('\t', ' ')
    
    # Fix broken words
    fixed_text = fixed_text.replace('- ', '')
    fixed_text = fixed_text.replace('-\n', '')

    # Remove URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    fixed_text = re.sub(url_pattern, '', fixed_text)
    
    # Remove numbers
    fixed_text = re.sub(r'\b\d+(\.\d+)?\b', '', fixed_text)

    # Remove stopwords
    fixed_text = fixed_text.lower()
    stopWords = ['keywords', 'palabras clave']
    for stopWord in stopWords:
        fixed_text = fixed_text.replace(stopWord,' ')

    # Split by .
    sentenceList = [sentence.strip() for sentence in 
                    fixed_text.split('.')]

    # Remove empty lines
    sentenceList = [sentence for sentence in sentenceList if sentence]
    
    # Susbtitute multiple spaces by a single space
    sentenceList = [re.sub(r'\s+', ' ', sentence) for sentence in sentenceList]
    return sentenceList

def cleanSentences(sentenceList):
    newSentenceList=[]
    stopWords = ['cookies', 'página', 'pagina', 'page', 'web','javascript'
                 'inglés', 'español', 'English', 'Spanish',
                 'política', 'policy', 'privacidad', 'privacy',
                 'cláusulas', 'clauses','empresas','companies',
                 'correo electrónico', 'email', 'e-mail',
                 'rechazar', 'reject', 'noticias', 'news',
                 '>', '<', '→', '®', '/', '↑', '?', '*', '[', ']', '©', '@',
                 'gobierno', 'government', 'departamento', 'department',
                 'licencia', 'license', 'print', 'imprimir', 'artículo',
                 'lock', 'biblioteca', 'library', 'wikipedia', 'medline',
                 'bethesda', 'www', 'department', 'et al', 'elsevier',
                 'national institute', 'university', 'universidad', '911',
                 'autorización', 'authorization', ', inc', 'reviewed',
                 'no significa que se les apruebe',
                 'la información aquí contenida no debe utilizarse',
                 'siga leyendo', 'cumple los rigurosos estándares',
                 'auditor independiente', 'in:', 'eds', 'acreditación',
                 'llame al', 'primer plano', 'revisada', 'revised',
                 'traducido', 'translated', 'comercial', 'curr opin',
                 'copyright', 'hable con un profesional', 'encyclopedia',
                 'vademécum', 'informed', 'méxico', 'publicidad',
                 'vademecum', 'spain', 'aemps', 'fda', 'publicidad',
                 'descarga', 'download', 'gratis', 'aceptado', 'revisado',
                 'mayo clinic', 'textbook', 'chile', 'fax', 'pide cita',
                 'cedidos', 'lucro', 'aviso', 'contact us', 
                 'contacte con nosotros', 'ánimo de lucro', 'este aviso',
                 'pediamecum', 'muchas gracias', 'commercial'
                 ]
    for sentence in sentenceList:
        ok=True
        for stopWord in stopWords:
            if stopWord in sentence:
                ok=False
                break
        ok=ok and len(sentence)>30
        ok=ok and len(sentence.split())>4
        if ok:
            newSentenceList.append(sentence)
            
    return newSentenceList

def readHTML(fnHTML):
    text=''
    with open(fnHTML, 'r', encoding = 'utf-8') as fh:  
        contentHTML = fh.read()
        fh.close()
    soup = BeautifulSoup(contentHTML, 'html.parser')
    try:
         text = soup.get_text(' ')
    except AttributeError:
        try:
            text = soup.find_all('p').text
        except AttributeError:
            try:
                text = soup.body.get_text(' ')
            except AttributeError:
                pass
    return text

def readPDF(fnPDF):
    text = ''
    with fitz.open(fnPDF) as pdf_document:
        num_pages = pdf_document.page_count
        
        for page_num in range(num_pages):
            page = pdf_document[page_num]
            page_text = page.get_text()
            text+=" "+page_text
    return text
    

if __name__=="__main__":
    model_name = "sentence-transformers/distiluse-base-multilingual-cased"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs)
    for idURL in glob.glob(os.path.join('data','recursos','*')):
        try:
            fnText=os.path.join(idURL,'content.txt')
            sentenceList = []
            if not os.path.exists(fnText):
                fnHTML=os.path.join(idURL,'content.html')
                fnPDF=os.path.join(idURL,'content.pdf')
                if os.path.exists(fnHTML):
                    text=readHTML(fnHTML)
                elif os.path.exists(fnPDF):
                    text=readPDF(fnPDF)
                print("Processing %s"%idURL)
                if text:
                    sentenceList=cleanSentences(splitSentences(text))
                    with open(fnText,'w',encoding = 'utf-8') as fh:
                        fh.write('.\n'.join(sentenceList))
                        fh.close()
            
            fnEmbedding=os.path.join(idURL,'content.npy')
            if not os.path.exists(fnEmbedding):
                print("Embedding %s"%idURL)
                if len(sentenceList)==0:
                    with open(fnText, 'r', encoding = 'utf-8') as fh:
                        sentenceList = fh.readlines()
                        sentenceList=[sentence.strip() for sentence in sentenceList]
                embedding = np.array(hf.embed_documents(sentenceList))
                np.save(fnEmbedding, embedding)
        except FileNotFoundError:
            continue
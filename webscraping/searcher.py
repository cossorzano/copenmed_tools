# Author: Ana Sanmartin
#
# This file obtains from command line the list of words inserted by the user

#Dependencies are
#pip install beautifulsoup4
#pip install google

# IMPORTS 

import argparse
import os
from downloader import download_text
#import numpy as np
try: 
    from googlesearch import search 
except ImportError:  
    print("No module named 'google' found") 


## CAN BE ESTABLISHED BY THE USER ##
n = 10;
searcher = 'www.google.com'
out_path = os.getcwd()

def main(word, n, searcher, out_path):

    """
    query : query string that we want to search for.
    tld : tld stands for top level domain which means we want to search our result on google.com or google.in or some other domain.
    lang : lang stands for language.
    num : Number of results we want.
    start : First result to retrieve.
    stop : Last result to retrieve. Use None to keep searching forever.
    pause : Lapse to wait between HTTP requests. Lapse too short may cause Google to block your IP. Keeping significant lapse will make your program slow but its safe and better option.
    Return : Generator (iterator) that yields found URLs. If the stop parameter is None the iterator will loop forever. 
    """
    dir_path = out_path + "/" + word + "/"
    list_searches = []
    query = word.replace("_", " ")
    counter = 0
    
    for i in search(query, tld="es", num=n, start=0, stop=None, pause=2):
        if (os.path.isfile(dir_path+i.replace("/","_")+".txt")):
            print("we have encountered a match")
        else:
            list_searches.append(i)
            counter = counter + 1
            print(counter)
        if (counter == n):
           break
        print(i)
        print(list_searches)
    download_text(list_searches, word, out_path)

 


######################
# PROGRAMA PRINCIPAL #
######################

# Argparse - Insert parameters from command line
parser = argparse.ArgumentParser(description="Search by terms")

parser.add_argument('-w',
                    "--word",
                    type=str,
                    help="Word to search")
                    
parser.add_argument('-n',
                    "--n",
                    type=int,
                    help="Number of pages to store")

parser.add_argument('-s',
                    "--search",
                    type=str,
                    help="Search engine to use.")

parser.add_argument('-o',
                    "--output",
                    type=str,
                    help="Output path where files are going to be stored")

# Parseo de los argumentos
arguments = vars(parser.parse_args())

if arguments['word']:
    word = arguments['word']
else:
    print("ERROR: Please enter valid words")
    exit()
if arguments['n']:
    if arguments['n'] > 0:
        n = arguments['n']
    else:
        print("ERROR: N must be bigger than 0")
        exit()
if arguments['search']:
    if isinstance(arguments['search'], str):
        searcher = arguments['search']
    else:
        print("ERROR: Please enter a valid search engine.")
        exit()
if arguments['output']:
    if isinstance(arguments['output'], str):
        if(os.path.isdir()):
            output_type = arguments['output']
        else:
            print("ERROR: Please enter a valid path.")
            exit()
    else:
        print("ERROR: Please enter a valid path.")
        exit()

main(word, n, searcher, out_path)


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
from check_resource import check_resource_retrieved_before
#import numpy as np

try: 
    from googlesearch import search 
except ImportError:  
    print("No module named 'google' found") 


## CAN BE ESTABLISHED BY THE USER ##
n = 10;
url = ''
searcher = 'www.google.com'
out_path = os.getcwd()
word = ''

def google_search(word, url, n, searcher, out_path):

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
    list_searches = []
    

    #We have two different functionalities: The user enters a word for searching or a specific url
    if len(url) != 0:
        # User has entered a specific URL
        print(check_resource_retrieved_before(url, out_path))
        if (check_resource_retrieved_before(url, out_path)):
            print("This URL already was searched before. Thus, we will not search again for the text")
            
        else:
            urls2doc(url, word.replace("_", " "), out_path)
            download_text(out_path)

    else: 
        query = word.replace("_", " ")
        
        print(query)
        print(out_path)
        
        list_searches = search_only(query, n, out_path)
        if len(list_searches) != 0:
            for url in list_searches:
                urls2doc(url, query, out_path)
            download_text(out_path)
        else:
            print("Nothing was retrieved")


def search_only(query, n, out_path):
    list_searches = []
    counter = 0
    
    for i in search(query, tld="es", num=n, start=0, stop=None, pause=2):
            if (check_resource_retrieved_before(i, out_path)):
                print("we have encountered a match")
            else:
                list_searches.append(i)
                counter = counter + 1
                #print(counter)
            if (counter == n):
               break
    return list_searches
    
        

 
def urls2doc(url, word, dir_path):

    dir_path += "/url_list.txt"
        
    doc = open(dir_path, "a")
    #print(doc.read())

    doc.write(url + " " + word + "\n")
    doc.close()
                        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Search by terms")

    parser.add_argument('-w',
                    "--word",
                    type=str,
                    help="Word to search")
                    
    parser.add_argument('-u',
                    "--url",
                    type=str,
                    help="Specific url to search") 
                                       
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
        if isinstance(arguments['word'], str):
            word = arguments['word']
        else:
            print("ERROR: Please enter valid words")
            exit()
    
    if arguments['url']:
        if isinstance(arguments['url'], str):
            url = arguments['url']
        else:
            print("ERROR: Please enter a valid search engine.")
            exit()
        
    if arguments['n']:
        if isinstance(arguments['n'], int):
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

    google_search(word, url, n, searcher, out_path)


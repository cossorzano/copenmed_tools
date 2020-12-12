# Author: Ana Sanmartin
#
# This file receives a list of URLs from another script and downloads the contents into a specified folder.

#Dependencies are


# IMPORTS 
import requests
import re
import glob
import os
from bs4 import BeautifulSoup

def download_text(list_urls, word, path):

    for url in list_urls:
        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        text = soup.find_all(text=True)
        #print(set([t.parent.name for t in text]))
        output = ''
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
        #print(soup.find('section').getText())
        for t in text:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)
        #print(output)
        
        store_text(path, url, output, word)


def store_text(path, url, text, word):

    #We need to check if the folder we are going to store the data exists
    dir_path = path + "/" + word + "/"
    
    #If it doesent exist we create a new folder and store the first file
    if not (os.path.exists(dir_path)):
        try:
            os.mkdir(dir_path)
            #file_name = dir_path + word + "_1.txt"
            #file_name = url + ".txt"
            #print(file_name)
            #f = open(file_name, "w")
            #f.write(str(text))
            #f.close()
        except OSError:
            print ("Creation of the directory %s failed" % dir_path)
        else:
            print ("Successfully created the directory %s " % dir_path)
    
    
    #If it exists we skip the step above and proceed to: 
    #    1: Obtain the list of all the .txt files in the folder
    #    2: Select the file with the latest number
    #    3: Add 1 to out file name 
    #    4: Store the data
    
    #else:
    #1
        #os.chdir(dir_path)
    #This stores all the elements in a list from a specific directory
        #myFiles = glob.glob('*.txt') 
    
        #if (len(myFiles) == 0): #Maybe the user created the folder but it's empty
            #file_name = dir_path + word + "_1.txt"
    file_name = dir_path + url.replace("/","_") + ".txt"
    f = open(file_name, "w")
    f.write(str(text))
    f.close()
        #else:
            #number_of_files = []
            #for name in myFiles:
            #    number_of_files.append(re.split(r'(_|.txt|\s)\s*', name)[-3])
                #print(number_of_files)
        #2 
            #max_index = max(int(name) for name in number_of_files)

        #3
            #file_name = word + '_' + str(max_index+1) +".txt"
           # file_name = url + ".txt"
           # f = open(file_name, "w")
           # f.write(str(text))
           # f.close()
    


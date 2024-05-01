<<<<<<< HEAD
from datetime import date
import os
import pickle
import sys
from pandas import read_excel
import requests
import glob
import codecs
import chardet

def make_request(url):
    userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"
    try:
        print("Trying: %s"%url)
        req = requests.get(url, headers={"USER-AGENT": userAgent})
        if req.reason=="OK" or req.reason=='200':
            encoding = chardet.detect(req.content)['encoding']
            if encoding is not None:
                return (True, req.content.decode(encoding))
            else:
                return (True, req.content)
        else:
            return (False, req.reason)
    except:
        print("Problem in decoding: %s"%url)
        return (False, "Exception")

def loadValidated(fnValidated):
    if os.path.exists(fnValidated):
        infile = open(fnValidated,'rb')
        validatedLinks = pickle.load(infile)
        infile.close()        
    else:
        validatedLinks={}
    return validatedLinks

def loadDownloaded():
    downloadedUrls={}
    nextId=0
    for idURL in glob.glob(os.path.join('data','recursos','*')):
        fnUrl=os.path.join(idURL,'url.txt')
        if os.path.exists(fnUrl):
            with open(fnUrl) as f:
                url = f.readline().strip('\n')
            downloadedUrls[url]=idURL
            numId=int(idURL.split('\\')[-1])
            if numId>=nextId:
                nextId=numId+1
    return downloadedUrls, nextId

def writeWebContent(idUrl, link, textOrReason, binary=False):
    imgExts = [".jpg", ".jpeg", ".tif", ".tiff", ".gif"]
    isImage = False
    for ext in imgExts:
        if link.endswith(ext):
            isImage=True
            break
    if isImage:
        return False
    dirUrl=os.path.join('data','recursos', str(idUrl))
    if not os.path.exists(dirUrl):
        os.mkdir(dirUrl)
    fnUrl=os.path.join(dirUrl,'url.txt')
    with open(fnUrl,'w') as f:
        f.write(link+"\n")
    fnContent=os.path.join(dirUrl,'content')
    if link.endswith('.pdf') or binary:
        fnContent+=".pdf"
        with open(fnContent,"wb") as f:
            f.write(textOrReason)
    else:
        fnContent+=".html"
        f = codecs.open(fnContent, "w", "utf-8")
        f.write(textOrReason)
        f.close()
    return True

def writeValidated(fnValidated, validatedLinks):
    fnValidated="validatedLinks.pkl"
    outfile = open(fnValidated,'wb')
    pickle.dump(validatedLinks,outfile)
    outfile.close()    

if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 valida_links.py <excelfile>")
        print("   <excelfile> must contain the Excel sheets of COpenMed")
        sys.exit(1)
    
    fnExcel=sys.argv[1]
    fnValidated="validatedLinks.pkl"
    validatedLinks=loadValidated(fnValidated)
    downloadedUrls, idUrl=loadDownloaded()

    df_sheet_index = read_excel(fnExcel, sheet_name="recursos")
    today = date.today()
            
    Nerrors=0
    Nwebs=0
    for index, row in df_sheet_index.iterrows():
        Nwebs+=1
        idRecurso=row['IdRecurso']
        idEntidad=row['IdEntidad']
        link=row['URL']
        okToCheck=True
        if link in validatedLinks:
            correct, lastCheck=validatedLinks[link]
            timeDiff = lastCheck-today
            if timeDiff.days<240:
                okToCheck=False
        if okToCheck:
            (ok, textOrReason) = make_request(link)
            validatedLinks[link]=(ok,today)
            if not ok:
                Nerrors+=1
                print("Error: %d/%d, %s: %s (IdEntidad=%d)"%\
                      (Nerrors, Nwebs, textOrReason, link, idEntidad))
        else:
            ok,_=validatedLinks[link]
        if ok and not link in downloadedUrls:
            try:
                if writeWebContent(idUrl, link, textOrReason):
                    downloadedUrls[link]=idUrl
                    idUrl+=1
            except:
                validatedLinks[link]=(False,today)
                print("Problem: %s"%link)
        if not ok:
            print("Problem: %s"%link)
        if Nwebs%25==0:
            writeValidated(fnValidated, validatedLinks)
            print("Nwebs=%d"%Nwebs)
=======
from datetime import date
import os
import pickle
import sys
from pandas import read_excel
import requests
import glob
import codecs
import chardet

def make_request(url):
    userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"
    try:
        print("Trying: %s"%url)
        req = requests.get(url, headers={"USER-AGENT": userAgent})
        if req.reason=="OK" or req.reason=='200':
            encoding = chardet.detect(req.content)['encoding']
            if encoding is not None:
                return (True, req.content.decode(encoding))
            else:
                return (True, req.content)
        else:
            return (False, req.reason)
    except:
        print("Problem in decoding: %s"%url)
        return (False, "Exception")

def loadValidated(fnValidated):
    if os.path.exists(fnValidated):
        infile = open(fnValidated,'rb')
        validatedLinks = pickle.load(infile)
        infile.close()        
    else:
        validatedLinks={}
    return validatedLinks

def loadDownloaded():
    downloadedUrls={}
    nextId=0
    for idURL in glob.glob(os.path.join('data','recursos','*')):
        fnUrl=os.path.join(idURL,'url.txt')
        if os.path.exists(fnUrl):
            with open(fnUrl) as f:
                url = f.readline().strip('\n')
            downloadedUrls[url]=idURL
            numId=int(idURL.split('\\')[-1])
            if numId>=nextId:
                nextId=numId+1
    return downloadedUrls, nextId

def writeWebContent(idUrl, link, textOrReason, binary=False):
    imgExts = [".jpg", ".jpeg", ".tif", ".tiff", ".gif"]
    isImage = False
    for ext in imgExts:
        if link.endswith(ext):
            isImage=True
            break
    if isImage:
        return False
    dirUrl=os.path.join('data','recursos', str(idUrl))
    if not os.path.exists(dirUrl):
        os.mkdir(dirUrl)
    fnUrl=os.path.join(dirUrl,'url.txt')
    with open(fnUrl,'w') as f:
        f.write(link+"\n")
    fnContent=os.path.join(dirUrl,'content')
    if link.endswith('.pdf') or binary:
        fnContent+=".pdf"
        with open(fnContent,"wb") as f:
            f.write(textOrReason)
    else:
        fnContent+=".html"
        f = codecs.open(fnContent, "w", "utf-8")
        f.write(textOrReason)
        f.close()
    return True

def writeValidated(fnValidated, validatedLinks):
    fnValidated="validatedLinks.pkl"
    outfile = open(fnValidated,'wb')
    pickle.dump(validatedLinks,outfile)
    outfile.close()    

if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 valida_links.py <excelfile>")
        print("   <excelfile> must contain the Excel sheets of COpenMed")
        sys.exit(1)
    
    fnExcel=sys.argv[1]
    fnValidated="validatedLinks.pkl"
    validatedLinks=loadValidated(fnValidated)
    downloadedUrls, idUrl=loadDownloaded()

    df_sheet_index = read_excel(fnExcel, sheet_name="recursos")
    today = date.today()
            
    Nerrors=0
    Nwebs=0
    for index, row in df_sheet_index.iterrows():
        Nwebs+=1
        idRecurso=row['IdRecurso']
        idEntidad=row['IdEntidad']
        link=row['URL']
        okToCheck=True
        if link in validatedLinks:
            correct, lastCheck=validatedLinks[link]
            timeDiff = lastCheck-today
            if timeDiff.days<240:
                okToCheck=False
        if okToCheck:
            (ok, textOrReason) = make_request(link)
            validatedLinks[link]=(ok,today)
            if not ok:
                Nerrors+=1
                print("Error: %d/%d, %s: %s (IdEntidad=%d)"%\
                      (Nerrors, Nwebs, textOrReason, link, idEntidad))
        else:
            ok,_=validatedLinks[link]
        if ok and not link in downloadedUrls:
            try:
                if writeWebContent(idUrl, link, textOrReason):
                    downloadedUrls[link]=idUrl
                    idUrl+=1
            except:
                validatedLinks[link]=(False,today)
                print("Problem: %s"%link)
        if not ok:
            print("Problem: %s"%link)
        if Nwebs%25==0:
            writeValidated(fnValidated, validatedLinks)
            print("Nwebs=%d"%Nwebs)
>>>>>>> c79b8ea472b68ecb4fb2b58da2699dc3ca20083d
    writeValidated(fnValidated, validatedLinks)
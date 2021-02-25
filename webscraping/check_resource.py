import os

def check_resource_retrieved_before(url, dir_path):
 
    dir_path += "/dir"
    if os.path.exists(dir_path):
    
        entities_list = os.listdir(dir_path)
    
        #print(entities_list)
    
        if len(entities_list) != 0: 
            # Some resources already exist we must check the url does not exist in
            # an url.txt
            for f in entities_list:
                resources_list = os.listdir(dir_path + "/" + f)
                for r in resources_list:
                    pathdoc_url = dir_path + "/" + f + "/" + r + "/url.txt"
                    doc = open(pathdoc_url, "r")
                    #print(doc.read())

                    if(doc.read() == url):
                        # The url has been searched before
                        return True
        else:
            return False
    else:
        return False
        
def write_resource_status(url, dir_path, status):
    dir_path += "/dir"
    if os.path.exists(dir_path):
    
        entities_list = os.listdir(dir_path)
        
        if len(entities_list) != 0: 
            for entity in entities_list:
                try:
                    with open(dir_path + "/" + entity +'/dictionary_urls.txt') as f: 
                        data = f.read() 
                        dic = json.loads(data) 
                        dic[url] = status
                        f.write( str(dic) )
                        f.close()
                except IOError:
                    print("Error while writing a new resource status")

def modify_resource_status(url, dir_path,status):
    pass
        
def check_resource_status(url, dir_path):
 
    dir_path += "/dir"
    if os.path.exists(dir_path):
    
        entities_list = os.listdir(dir_path)
        
        if len(entities_list) != 0: 
            for entity in entities_list:
                try:
                    with open(dir_path + "/" + entity +'/dictionary_urls.txt') as f: 
                        data = f.read() 
                        dic = json.loads(data) 
                        for key, value in dic.items(): 
                            if key == url:
                                return value 
                except IOError:
                    print("dictionary urls file does not exist")
                    return 2
        else:
            return 2
    else:
        return 2

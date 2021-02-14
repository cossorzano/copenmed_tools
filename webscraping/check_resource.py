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

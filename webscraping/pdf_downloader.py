from tika import parser # pip install tika
#response = requests.get(url,proxies={"http": proxy, "https": proxy})
import requests

#response = requests.get("https://www.who.int/csr/resources/publications/ES_WHO_CDS_CSR_EPH_2002_12.pdf")
#with open('metadata.pdf', 'wb') as f:
#    f.write(response.content)
    
#response = requests.get(url,proxies={"http": proxy, "https": proxy})
raw = parser.from_file('metadata.pdf')
print(raw['content'])
print(type(raw['content']))

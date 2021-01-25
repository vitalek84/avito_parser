import requests
import re


catIdPat = re.compile("\"categoryId\":([0-9]+)")
subcatIdPat = re.compile("\"subcategoryId\":([0-9]+)")
cityIdPat = re.compile("\"cityId\":\"([0-9a-f]+)\"")

def parsePage(url): 
    response = requests.get(url).text #driver.page_source
    try:
        catId = catIdPat.search(response).group(1)
        subcatId = subcatIdPat.search(response).group(1)
        cityId = cityIdPat.search(response).group(1)

        return (catId, subcatId, cityId)
    except:
        return ("-", "-", "-")

f = open("urls.txt", "r")
d = f.read()
f.close()
lines = d.split("\n")

data = ""
for i, url in enumerate(lines):
    print("%d/%d" % (i, len(lines)))
    data += "%s;%s;%s\n" % parsePage(url)

f = open("res.txt", "w")
f.write(data)
f.close()

    
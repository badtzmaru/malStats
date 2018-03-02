import requests, os
from bs4 import BeautifulSoup

def getXML(user):
    url = "https://myanimelist.net/malappinfo.php?u=" + user + "&type=anime&status=all"
    r = requests.get(url, allow_redirects=True, stream=True)
    if len(str(r.content)) < 10:
        print("User: " + user + " could not be found.")
        return False
    else:
        open("xml/" + user  + ".xml", 'wb').write(r.content)
        return True

# getXML("Badtz13")

with open("xml/Badtz13.xml", encoding='utf8') as infile:
    soup = BeautifulSoup(infile, "html.parser")
    animeTags = soup.find_all("anime")
    for i in range(0,len(animeTags)):
        print(animeTags[i].find("series_title").text)
import requests, os, argparse, time
from tqdm import tqdm
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Generate a csv of anime scores for the given users')
parser.add_argument('inputValues', nargs='+', help='The names of the users you want added to the csv, with spaces in between')
args = parser.parse_args()

animeScores = []
# animeScores = [['tororo','9.5',[10,10]]]

def getMALScore(id):
    with requests.session() as browser:
        browser.headers['user-agent'] = 'Mozilla/5.0'
        r = browser.get("https://myanimelist.net/anime/" + id)
        soup = BeautifulSoup(r.text, 'html.parser')
        score = soup.find('div',{'class': 'fl-l score'})
        return(score.text.strip())

def getXML(user):
    url = "https://myanimelist.net/malappinfo.php?u=" + user + "&type=anime&status=all"
    r = requests.get(url, allow_redirects=True, stream=True)
    if len(str(r.content)) < 10:
        print("User: " + user + " could not be found.")
        return False
    else:
        open("xml/" + user  + ".xml", 'wb').write(r.content)
        return True

def parseList(user):
    with open("xml/" + user + ".xml", encoding='utf8') as infile:
        soup = BeautifulSoup(infile, "html.parser")
        animeTags = soup.find_all("anime")
        for i in tqdm(range(0,len(animeTags))):
            if animeTags[i].find("my_status").text ==  "2" and animeTags[i].find("series_type").text != "3":
                time.sleep(.5)
                
                title = animeTags[i].find("series_title").text
                found = False

                for k in range(0, len(animeScores)):
                    if animeScores[k][0] == title:
                        animeScores[k][2].append(int(animeTags[i].find("my_score").text))
                        found = True
                        break
                
                if found == False:
                    animeScores.append([title, getMALScore(animeTags[i].find("series_animedb_id").text), [int(animeTags[i].find("my_score").text)]])

def main():
    for user in args.inputValues:
        # getXML(user)
        parseList(user)

    print(len(animeScores))
    print(animeScores[0])


main()
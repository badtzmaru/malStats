import requests, os, argparse, time
from tqdm import tqdm
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Generate a csv of anime scores for the given users')
parser.add_argument('inputValues', nargs='+', help='The names of the users you want added to the csv, with spaces in between')
args = parser.parse_args()

animeScores = []
# animeScores = [['tororo','9.5',[10,10]]]

def getMALScore(id):
    # return "disabled"
    with requests.session() as browser:
        browser.headers['user-agent'] = 'Mozilla/5.0'
        r = browser.get("https://myanimelist.net/anime/" + id)
        time.sleep(1)
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

def parseList(user,index):
    with open("xml/" + user + ".xml", encoding='utf8') as infile:
        soup = BeautifulSoup(infile, "html.parser")
        animeTags = soup.find_all("anime")
        for i in tqdm(range(0,len(animeTags))):
            if animeTags[i].find("my_status").text ==  "2" and animeTags[i].find("series_type").text != "3":
                
                title = animeTags[i].find("series_title").text
                found = False

                for k in range(0, len(animeScores)):
                    if animeScores[k][0] == title:
                        animeScores[k][2][index] = int(animeTags[i].find("my_score").text)
                        found = True
                        break
                
                if found == False:
                    animeScores.append([title, getMALScore(animeTags[i].find("series_animedb_id").text), [""] * len(args.inputValues)])
                    animeScores[len(animeScores)-1][2][index] = int(animeTags[i].find("my_score").text)

def main():
    for m in range(0,len(args.inputValues)):
        user = args.inputValues[m]
        getXML(user)
        parseList(user,m)

    print(str(len(animeScores)) + " shows found")
    with open('scores.csv', 'w', encoding="utf-8") as file:
        for show in animeScores:
            print(show)
            file.write(show[0].replace(",","") + ",=AVERAGE(F2:K2)," + show[1] + ",")
            for score in show[2]:
                file.write(str(score) + ",")
            file.write("\n")
main()
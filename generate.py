# import dependencies 
import requests, os, argparse, time
from tqdm import tqdm
from bs4 import BeautifulSoup

# set up command line arguments 
parser = argparse.ArgumentParser(description='Generate a csv of anime scores for the given users')
parser.add_argument('minUsers', metavar='minUsers', type=int, nargs=1, help='The minimum number of users required to display a show in the csv')
parser.add_argument('-m', action='store_true', help='Add scores from MyAnimeList to the last column of the sheet')
parser.add_argument('inputValues', nargs='+', help='The names of the users you want added to the csv, with spaces in between')
args = parser.parse_args()

# define multidimensional list of shows and scores, format below
animeScores = []
# animeScores = [['tororo','9.5',[10,10]]]
# animeScores = [[title, malScore,[userscore1, userscore2, etc]]]

# get the score of a show on MyAnimeList using the MAL id
def getMALScore(id):
    if(args.m):
        with requests.session() as browser:
            browser.headers['user-agent'] = 'Mozilla/5.0'
            r = browser.get("https://myanimelist.net/anime/" + id)

            # if you hit MAL too fast, the lock you out, so there's a modest delay
            time.sleep(1)

            soup = BeautifulSoup(r.text, 'html.parser')
            score = soup.find('div',{'class': 'fl-l score'})
            return(score.text.strip())
    else:
        return ""
    
    
# get the xml version of the provided user's list and save it to /xml
def getXML(user):
    url = "https://myanimelist.net/malappinfo.php?u=" + user + "&type=anime&status=all"
    r = requests.get(url, allow_redirects=True, stream=True)
    if len(str(r.content)) < 10:
        print("User: " + user + " could not be found.")
        return False
    else:
        open("xml/" + user  + ".xml", 'wb').write(r.content)
        return True

# parse the given xml file, and add it to the animeScores list
def parseList(user,index):
    time.sleep(.5)
    with open("xml/" + user + ".xml", encoding='utf8') as infile:

        # find all <anime> tags
        soup = BeautifulSoup(infile, "html.parser")
        animeTags = soup.find_all("anime")

        # loop through list of shows
        for i in tqdm(range(0,len(animeTags))):
            
            # if it's not a movie and the user has completed the show
            if animeTags[i].find("my_status").text ==  "2" and animeTags[i].find("series_type").text != "3": 
                
                title = animeTags[i].find("series_title").text
                found = False

                # check through animeScores list to see if the show is already in it
                for k in range(0, len(animeScores)):
                    if animeScores[k][0] == title:
                        animeScores[k][2][index] = int(animeTags[i].find("my_score").text)
                        found = True
                        break
                
                # if the show was not found in the list, add it
                if found == False:
                    animeScores.append([title, getMALScore(animeTags[i].find("series_animedb_id").text), [""] * len(args.inputValues)])
                    animeScores[len(animeScores)-1][2][index] = int(animeTags[i].find("my_score").text)
# main function
def main():
    
    # for each user
    for m in range(0,len(args.inputValues)):
        user = args.inputValues[m]

        # download and parse each user's info
        getXML(user)
        parseList(user,m)

    # write data to csv
    showCounter = 0
    with open('scores.csv', 'w', encoding="utf-8") as file:
        for show in animeScores:
            userCounter = 0

            # count the number of users that have completed the show
            for u in range(0,len(show[2])):
                if show[2][u] != "":
                    userCounter += 1
            
            # if at least two users have completed the show, then add it to the csv
            if userCounter >= int(args.minUsers[0]):
                showCounter = showCounter + 1
                file.write(show[0].replace(",","") + ",")
                for score in show[2]:
                    file.write(str(score) + ",")
                file.write(show[1] + "\n")
                
    print(str(showCounter) + " shows found")

main()
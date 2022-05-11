import json
from operator import contains
from os import fdopen
from time import sleep
import requests
from os.path import exists
from time import sleep
import json
import csv
from random import randint

# includes the following candidate ids (currently BBM and Leni)
includeIds = [46444, 46447]

csvFile = open('results.csv','w')
csvWriter = csv.writer(csvFile)

# Some precincts returns access denied
problematicPresincts = [107938, 108265];

x = 1
for precinct in range(107786,217316):

    if precinct in problematicPresincts:
        continue;
    
    print(f"Precinct # {precinct}")

    shard = str(precinct)[0:3]
    fileName = 'responses/' + str(precinct)+ '.json';

    randomSleepTime = randint(100,400)/1000;
    #print("Sleep time: " + str(randomSleepTime))

    if exists(fileName):
        file = open(fileName,'r')
        responseText = content = file.read()

    else:
        url = 'https://2022electionresults.comelec.gov.ph/data/results/' + str(shard) +'/'+ str(precinct)+'.json'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        
        print(f"Fetching: {url}");
        try:
            response = requests.get(url, headers=headers)
            sleep(randomSleepTime)
        except Exception as error:
            print("Error: {0}".format(error))
            sleep(20)
        
        file = open(fileName,'w+')
        responseText = response.text
        file.write(responseText)
        file.close()

    if "<Code>AccessDenied</Code>" in responseText:
        continue;

    data = json.loads(responseText)
        
    for vote in data["rs"]:
        if vote["bo"] in includeIds:
            csvWriter.writerow([precinct] + list(vote.values()))
    
    x+=1

    #if x >= 10:
    #    break

csvFile.close()
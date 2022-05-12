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
import sys

def getJson(urlFormat, shard, id, cacheDir, fetch = True):

    fileName = cacheDir + '/' + str(id) + '.json';
    #print("Sleep time: " + str(randomSleepTime))

    responseText = ""

    if exists(fileName):
        file = open(fileName,'r')
        responseText = file.read()

    if responseText == "":
        if not fetch:
            return False

        randomSleepTime = randint(10,200)/1000;
        url = urlFormat.format(str(shard), str(id))
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        print(f"Fetching: {url}");
        try:
            response = requests.get(url, headers=headers)
            sleep(randomSleepTime)

            if response.status_code != 200:
                print(f"Skipping {url} status code: {response.status_code}")
                return False
        except Exception as error:
            print("Error: {0}".format(error))
            sleep(20)
            return False

        file = open(fileName,'w+')
        responseText = response.text
        file.write(responseText)
        file.close()

    try:
        data = json.loads(responseText)
    except Exception as error:
        print(responseText)
        print("Error: {0}".format(error))
        return False

    return data;

def getLocationData(locationId):
    shard = str(locationId)[0:2]
    return getJson('https://2022electionresults.comelec.gov.ph/data/regions/{0}/{1}.json', shard, int(locationId), 'region-responses')

def getResultData(presinctId, fetch = True):
    shard = str(presinctId)[0:3]
    return getJson('https://2022electionresults.comelec.gov.ph/data/results/{0}/{1}.json', shard, int(presinctId), 'responses', fetch)


phData = getLocationData("44021")

if (phData == False):
    print("Data not found")
    exit()


# includes the following candidate ids (currently BBM and Leni)
includeCandidateIds = [ 46444,46447 ]

fetchResults =  False if "--dont-fetch-results" in sys.argv else True


csvFile = open('location-results.csv','w')
csvWriter = csv.writer(csvFile)

csvWriter.writerow(["BBM\nVotes","BBM %","Leni\nVotes","Leni%","Presincts","Poll Place","Barangay","City","Province"])


for regionId in phData["srs"]:
    region = phData["srs"][regionId]
    regionData = getLocationData(region["rc"])

    for provinceId in regionData['srs']:
        province = regionData['srs'][provinceId]
        provinceData = getLocationData(province["rc"])

        for cityId in provinceData['srs']:
            city = provinceData['srs'][cityId]
            cityData = getLocationData(city["rc"])

            for barangayId in cityData['srs']:
                barangay = cityData['srs'][barangayId]
                barangayData = getLocationData(barangay["rc"])

                if barangayData == False:
                    exit()

                for presinct in barangayData['pps']:
                    
                    result = getResultData(presinct['ppc'], fetchResults)
                    

                    candidateVotes = {
                        includeCandidateIds[0]: 0,
                        includeCandidateIds[1]: 0
                    };
                    candidatePercent = {
                        includeCandidateIds[0]: 0,
                        includeCandidateIds[1]: 0
                    };

                    if result:
                        for vote in result["rs"]:
                            candidateId = vote["bo"];
                            if candidateId in includeCandidateIds:
                                candidateVotes[candidateId] = vote['v']
                                candidatePercent[candidateId] = vote['per']

                    presincts = []
                    # not sure what VB means
                    for vbs in presinct['vbs']:
                        presincts.append(vbs['cpre'])
                    
                    csvRow = [
                        candidateVotes[includeCandidateIds[0]],
                        candidatePercent[includeCandidateIds[0]],
                        candidateVotes[includeCandidateIds[1]],
                        candidatePercent[includeCandidateIds[1]],
                        ', '.join(presincts),
                        presinct["ppn"],
                        barangayData['rn'],
                        cityData['rn'],
                        provinceData['rn'],
                        regionData['rn']
                    ]
                    print(csvRow)

                    csvWriter.writerow(csvRow)


csvFile.close()
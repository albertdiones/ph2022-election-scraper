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

def getJson(urlFormat, id, cacheDir):
    shard = str(id)[0:2]

    fileName = cacheDir + '/' + str(id) + '.json';
    #print("Sleep time: " + str(randomSleepTime))

    responseText = ""

    if exists(fileName):
        file = open(fileName,'r')
        responseText = content = file.read()

    if responseText == "":

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

        file = open(fileName,'w+')
        responseText = response.text
        file.write(responseText)
        file.close()

    try:
        data = json.loads(responseText)
    except Exception as error:
        print(responseText)
        print("Error: {0}".format(error))
        return False;

    return data;


phData = getJson('https://2022electionresults.comelec.gov.ph/data/regions/{0}/{1}.json',44021, 'region-responses')

if (phData == False):
    print("Data not found")
    exit()

for regionId in phData["srs"]:
    region = phData["srs"][regionId]
    regionData = getJson('https://2022electionresults.comelec.gov.ph/data/regions/{0}/{1}.json',int(region["rc"]), 'region-responses')

    for provinceId in regionData['srs']:
        province = regionData['srs'][provinceId]
        provinceData = getJson('https://2022electionresults.comelec.gov.ph/data/regions/{0}/{1}.json',int(province["rc"]), 'region-responses')

        for cityId in provinceData['srs']:
            city = provinceData['srs'][cityId]
            cityData = getJson('https://2022electionresults.comelec.gov.ph/data/regions/{0}/{1}.json',int(city["rc"]), 'region-responses')

            for barangayId in cityData['srs']:
                barangay = cityData['srs'][barangayId]
                barangayData = getJson('https://2022electionresults.comelec.gov.ph/data/regions/{0}/{1}.json',int(barangay["rc"]), 'region-responses')

                if barangayData == False:
                    exit();

                for presinct in barangayData['pps']:
                    print(str(presinct["ppc"]) + ": " + presinct['ppn'])
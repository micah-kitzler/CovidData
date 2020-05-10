from datetime import date,timedelta
from PIL import Image, ImageDraw, ImageFont

futurePaths = []

##pathDictExample = {
##    "date": date object of the expected date of trasmission,
##    "countries": [array of two country names connected by this path]
##    }


pathedCountries = [] #arrays of country names, each country should only be in one of these at any one time
infectedCountries = []
pathedAndInfected = [] #only countries both pathed and infected will be on the map

futureInfectionData = []

##infectionDataDictExample = {
##    "country": name of country,
##    "date": date object of this datapoint,
##    "cases": number of infected
##    }

countries = {} #dict of country dicts, keys will be country names

##countyDictExample = {
##    "numInfected": current number infected,
##    "center": [x,y] coordinates of country center on map,
##    "id": number id to represent this country in the map array,
##    "paths" : dict of connected countries and number of connections i.e.:{"china":3},
##    "border" : [[x1,y1],[x2,y2]] array of coordinates on the border of the country (next points to claim on the map),
##    "requestedBuffer" : buffer to increase distance between countries in case we run out of room,
##    "numPaths" : total number of paths 
##    }

mapMatrix = [[0]*1536 for x in range(2048)] #will hold country id's for each pixel
popUnit = 1 #global scale for how many pops per pixel

f = open("paths.csv","r")
f.readline()
for line in f:
    data = line.split(',')
    futurePaths.append({
        "date": date.fromisoformat(data[0]),
        "countries": [data[1].strip(),data[2].strip()]
        })
f.close()

f = open("owid-covid-data.csv","r")
f.readline()
for line in f:
    data = line.split(',')
    if (int(data[3])>0):
        futureInfectionData.append({
            "country": data[1].strip(),
            "date": date.fromisoformat(data[2]),
            "cases": int(data[3])
            })
f.close()


def claim(coordinate,country): #function for a country to claim a pixel for itself
    x = int(coordinate[0])
    y = int(coordinate[1])
    mapMatrix[x][y] = countries[country]["id"]
    countries[country]["border"].remove([x,y])
    if (mapMatrix[(x+1)%2048][y] == 0):
        countries[country]["border"].append([(x+1)%2048,y])
    if (mapMatrix[(x-1)%2048][y] == 0):
        countries[country]["border"].append([(x-1)%2048,y])
    if (mapMatrix[x][(y+1)%1536] == 0):
        countries[country]["border"].append([x,(y+1)%2048])
    if (mapMatrix[x][(y-1)%1536] == 0):
        countries[country]["border"].append([x,(y-1)%2048])

def dist(coordinate1,coordinate2): #distance formula
    return (float(min(abs(coordinate1[0]-coordinate2[0]),(abs(coordinate1[0]-coordinate2[0])+2048)%2048))**2 + float(min(abs(coordinate1[1]-coordinate2[1]),(abs(coordinate1[1]-coordinate2[1])+1536)%1536))**2)**0.5

def scorePix(coordinate,country,pathCountry): #function to score a given coordinate on how fitting it would be to have a pop hear
    x = int(coordinate[0])
    y = int(coordinate[1])
    if (pathCountry in pathedAndInfected and not countries[pathCountry]["id"] in [mapMatrix[(x+1)%2048][y],mapMatrix[(x-1)%2048][y],mapMatrix[x][(y+1)%1536],mapMatrix[x][(y-1)%1536]]):
        return dist(coordinate,countries[pathCountry]["center"]) - (countries[pathCountry]["numInfected"]/popUnit)**0.5/2 + 10*dist(coordinate,countries[country]["center"])**3/(countries[country]["numInfected"]/popUnit)
    else:
        return 10*dist(coordinate,countries[country]["center"])**3/(countries[country]["numInfected"]/popUnit)

def scoreCenter(coordinate,country): #function to score given coordinate on how fitting it would be for the country to be centered here
    for otherCountry in pathedAndInfected:
        if (otherCountry == country or len(countries[otherCountry]["center"])<2):
            continue
        if (dist(coordinate,countries[otherCountry]["center"]) < ((countries[country]["numInfected"]/popUnit)**0.5 + (countries[otherCountry]["numInfected"]/popUnit)**0.5)/2 + countries[country]["requestBuffer"]/popUnit + countries[otherCountry]["requestBuffer"]/popUnit):
            return -1
    scoreSum = 0
    for otherCountry in countries[country]["paths"].keys():
        if (otherCountry in pathedAndInfected and len(countries[otherCountry]["center"])==2):
            scoreSum += countries[country]["paths"][otherCountry]*(dist(coordinate,countries[otherCountry]["center"]) - ((countries[country]["numInfected"]/popUnit)**0.5 + (countries[otherCountry]["numInfected"]/popUnit)**0.5)/2)
    return scoreSum

def shuffle(country): #function to move country around bit by bit to try and fing the best location for the center
    bestCenter = countries[country]["center"]
    bestScore = scoreCenter(bestCenter,country)
    resolution = 16
    while (resolution>=1):
        hasMoved = True
        while (hasMoved):
            hasMoved = False
            pendingScore = bestScore
            pendingCenter = bestCenter
            testCenter = [(bestCenter[0]+resolution)%2048,bestCenter[1]] 
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [(bestCenter[0]-resolution)%2048,bestCenter[1]]
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [bestCenter[0],(bestCenter[1]+resolution)%1536]
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [bestCenter[0],(bestCenter[1]-resolution)%1536]
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [(bestCenter[0]+resolution)%2048,(bestCenter[1]+resolution)%1536] 
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [(bestCenter[0]-resolution)%2048,(bestCenter[1]+resolution)%1536]
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [(bestCenter[0]+resolution)%2048,(bestCenter[1]-resolution)%1536]
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            testCenter = [(bestCenter[0]-resolution)%2048,(bestCenter[1]-resolution)%1536]
            testScore = scoreCenter(testCenter, country)
            if (testScore != -1 and testScore<pendingScore):
                hasMoved = True
                pendingScore = testScore
                pendingCenter = testCenter
            bestCenter = pendingCenter
            bestScore = pendingScore
        resolution = resolution/2
    countries[country]["center"] = bestCenter
    return minScore

today = date(2019,12,1)

while today<date.today():
    print("check for new infections")
    for dataPoint in futureInfectionData: #check for new infection data
        if (dataPoint["date"]<=today):
            if (not dataPoint["country"] in countries.keys()):
                infectedCountries.append(dataPoint["country"])
                print("infected " + dataPoint["country"])
                countries[dataPoint["country"]] = {
                    "numInfected":dataPoint["cases"],
                    "center":[],
                    "id":len(countries.keys())+1,
                    "paths":{},
                    "border":[],
                    "requestBuffer":0,
                    "numPaths": 0
                    }
            else:
                countries[dataPoint["country"]]["numInfected"] = dataPoint["cases"]
            futureInfectionData.remove(dataPoint)
    print("check for new paths")
    for path in futurePaths: #check for new infection paths
        if (path["date"]<=today):
            if (path["countries"][0] in countries.keys()):
                countries[path["countries"][0]]["numPaths"]+=1
                if (path["countries"][1] in countries[path["countries"][0]]["paths"].keys()):
                    countries[path["countries"][0]]["paths"][path["countries"][1]]+=1
                else:
                    countries[path["countries"][0]]["paths"][path["countries"][1]]=1
            else:
                pathedCountries.append(path["countries"][0])
                print("pathed " + path["countries"][0])
                countries[path["countries"][0]] = {
                    "numInfected":0,
                    "center":[],
                    "id":len(countries.keys())+1,
                    "paths":{path["countries"][1]:1},
                    "border":[],
                    "requestBuffer":0,
                    "numPaths": 1
                    }
            if (path["countries"][1] in countries.keys()):
                countries[path["countries"][1]]["numPaths"]+=1
                if (path["countries"][0] in countries[path["countries"][1]]["paths"].keys()):
                    countries[path["countries"][1]]["paths"][path["countries"][0]]+=1
                else:
                    countries[path["countries"][1]]["paths"][path["countries"][0]]=1
            else:
                pathedCountries.append(path["countries"][1])
                print("pathed " + path["countries"][1])
                countries[path["countries"][1]] = {
                    "numInfected":0,
                    "center":[],
                    "id":len(countries.keys())+1,
                    "paths":{path["countries"][0]:1},
                    "border":[],
                    "requestBuffer":0,
                    "numPaths": 1
                    }
            futurePaths.remove(path)
    for country in infectedCountries: #update infectedCountries array and move to pathedAndInfected if now pathed
        if (len(countries[country]["paths"].keys())>0):
            print(country + " now pathed and infected")
            pathedAndInfected.append(country)
            infectedCountries.remove(country)
    for country in pathedCountries: #see above, but for pathed countries now infected
        if (countries[country]["numInfected"]>0):
            print(country + " now pathed and infected")
            pathedAndInfected.append(country)
            pathedCountries.remove(country)

    for i in range(2048):
        for j in range(1536):
            mapMatrix[i][j] = 0
            
    if ("World" in countries.keys()):
        worldPop = countries["World"]["numInfected"]
        popUnit = max(1,min(10,worldPop/20000))
    else :
        worldPop = 0
    mapFinished = len(pathedAndInfected) == 0 #only make a map if we have countries to map
    if (not mapFinished):
        print("making map")
    else:
        print("no countries to map")
    while (not mapFinished):
        canPlacePops = True
        print("placing country centers")
        if (len(pathedAndInfected)==1 and len(countries[pathedAndInfected[0]]["center"])<2):
            countries[pathedAndInfected[0]]["center"] = [1024,768]
            countries[pathedAndInfected[0]]["border"] = [[1024,768]]
            print("center for " + pathedAndInfected[0] + " at [1024,768]")
        elif(len(pathedAndInfected)>1):
            for country in pathedAndInfected:
                countries[country]["requestBuffer"]=max(0,countries[country]["requestBuffer"]-3)
                #place country centers for all pathed and infected countries
                if (len(countries[country]["center"])<2): #country has not yet been placed
                    print("finding location for " + country)
                    minScore = scoreCenter([0,0],country)
                    bestCenter = [0,0]
                    for i in range(62):
                        for j in range(46):
                            thisScore = scoreCenter([32+32*i,32+32*j],country)
                            if (thisScore == -1 or (minScore!=-1 and thisScore>minScore)):
                                continue
                            minScore = thisScore
                            bestCenter = [32+32*i,32+32*j]
                            #print("new best center: " + str(bestCenter))
                    if (minScore == -1):
                        print("could not find center for " + country)
                        break
                    else:
                        print( country + " placed at " + str(bestCenter))
                        countries[country]["center"] = bestCenter
                newScore = shuffle(country)
                if (newScore == -1):
                    countries[country]["requestBuffer"]+=5
                    canPlacePops = False
                    mapFinished = False
                    print(country + " is too crowded, could not shuffle to suitable center.")
                countries[country]["border"] = [countries[country]["center"]]
        PopsPlaced = 0
        if (canPlacePops):
            print("placing pops")
        while (canPlacePops):
            hasPlacedPops = False
            for country in pathedAndInfected:
                if (countries[country]["numInfected"]<popUnit*PopsPlaced): #placed all pops for this country
                    continue
                if (len(countries[country]["border"]) == 0): #no more place to put pops
                    print(country + " is too crowded, could not place all needed pops.")
                    canPlacePops = False
                    mapFinished = False
                    countries[country]["requestBuffer"]+=5
                    break
                pathIndex = PopsPlaced % countries[country]["numPaths"] #choose path for pop to move towards
                pathCountry = ""
                for path in countries[country]["paths"].keys():
                    if (pathIndex<countries[country]["paths"][path]):
                        pathCountry = path
                        break
                    pathIndex -= countries[country]["paths"][path]
                bestPix = countries[country]["border"][0]
                minScore = scorePix(bestPix,country,pathCountry)
                for coordinate in countries[country]["border"]:
                    thisScore = scorePix(coordinate,country,pathCountry)
                    if (thisScore<minScore):
                        minScore = thisScore
                        bestPix = coordinate
                claim(bestPix, country)
                hasPlacedPops = True
            PopsPlaced+=1
            mapFinished = canPlacePops and not hasPlacedPops
            canPlacePops = canPlacePops and hasPlacedPops
    
    if (len(pathedAndInfected) >= 1):
        print("painting picture")
        img = Image.new("RGB",(2048,1536))
        imgMatrix = img.load()
        for i in range(2048):
            for j in range(1536):
                if (mapMatrix[i][j]!=mapMatrix[(i+1)%2048][j] or mapMatrix[i][j]!=mapMatrix[i][(j+1)%1536]):
                    imgMatrix[i,j] = (255,255,255)
                elif (mapMatrix[i][j]!=0):
                    imgMatrix[i,j] = ((169*mapMatrix[i][j])%256,(121*mapMatrix[i][j])%255,(49*mapMatrix[i][j])%255)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 30)
        draw.text((0,0), today.isoformat(), font=font)
        draw.text((0,40), "Total Infected: "+str(worldPop), font=font)
        draw.text((0,80), "Scale (Population per Pixel): "+str(popUnit), font=font)
        for country in pathedAndInfected:
            if (countries[country]["numInfected"]/popUnit>1024):
                fontSize = int(min(30, max(10, countries[country]["numInfected"]**0.5/10)))
                draw.text((max(countries[country]["center"][0]-len(country)/4*fontSize , 0),max(countries[country]["center"][1]-fontSize/2 , 0)), country, font=ImageFont.truetype("arial.ttf", fontSize))
        #img.show()
        img.save(str(today)+".png")
        img.close()
        #if(input("s to stop:") == 's'):
        #    break
    print(today)
    #print(len(infectedCountries))
    #print(len(pathedCountries))
    #print(len(pathedAndInfected))
    #print(countries.keys())
    today = today+timedelta(days=1)

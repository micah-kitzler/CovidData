from lxml import etree
import chord
import time

svg = etree.parse("nextstrain_ncov_global.svg")
root = svg.getroot()
countries = {}
for element in root:
    #print(element.get("id"))
    if (element.get("id") == "treeLegend"):
        lastColor = 0
        for country in element.iter():
            #print(country.tag)
            #print(country.text)
            if(country.tag == "{http://www.w3.org/2000/svg}rect"):
                lastColor = country.get("stroke")
            if(country.tag == "{http://www.w3.org/2000/svg}title"):
                #print(str(country.text) + " " + str(lastColor))
                countries[country.text] = {"color":lastColor, "coordinates":""}

paths = []
countries['South America']['coordinates'] = '449,365'
for element in root:
    if (element.get("id") == "map"):
        for div in element.iter():
            #print(element.tag)
            if (div.tag == "{http://www.w3.org/2000/svg}circle"):
                #print("circle")
                transform = div.get("transform")
                thisCoordinate = transform.split('(')[1][:-1]
                thisX = int(thisCoordinate.split(',')[0])%1024
                thisCoordinate = str(thisX)+','+thisCoordinate.split(',')[1]
                style = str(div.get("style")).split()
                thisColor = style[1+style.index("stroke:")] + ' ' + style[2+style.index("stroke:")] + ' ' + style[3+style.index("stroke:")][:-1]
                for country in countries:
                    if (countries[country]["color"] == thisColor):
                        countries[country]["coordinates"]=thisCoordinate
                        #print(countries[country])
        print("countries")
        print(countries)
        for div in element.iter():
            if (div.tag == "{http://www.w3.org/2000/svg}path"):
                data = str(div.get("d")).split('L')
                countryA = data[0][1:]
                thisX = int(countryA.split(',')[0])%1024
                countryA = str(thisX)+','+countryA.split(',')[1]
                countryB = data[-1]
                thisX = int(countryB.split(',')[0])%1024
                countryB = str(thisX)+','+countryB.split(',')[1]
                style = str(div.get("style")).split()
                thisColor = style[1+style.index("stroke:")] + ' ' + style[2+style.index("stroke:")] + ' ' + style[3+style.index("stroke:")][:-1]
                for country in countries:
                    if (countries[country]["color"] == thisColor):
                        thisColor = country
                    if (countryA == countries[country]["coordinates"]):
                        countryA = country
                    if (countryB == countries[country]["coordinates"]):
                        countryB = country
                src = thisColor
                dest = countryA
                if (src == dest):
                    dest = countryB
                paths.append({"src":src, "dest":dest})
                #if(src == "Japan" or dest=="Japan"):
                    #print(paths[-1])
                if(not all(x.isalpha() or x.isspace() for x in dest) or not all(x.isalpha() or x.isspace() for x in src)):
                    print(paths[-1])
                        
relationalMatrix = [[0]*len(countries) for x in range(len(countries))]
#print(relationalMatrix)
countryList = list(countries.keys())
for path in paths:
    relationalMatrix[countryList.index(path["src"])][countryList.index(path["dest"])]+=1
smallMatrix = []
for i in range(6):
    smallMatrix.append(relationalMatrix[i][0:5])
print(relationalMatrix)
print(smallMatrix)
chord.Chord(relationalMatrix, countryList, wrap_labels=False, font_size="8px", font_size_large="8px").to_html()


import plotly.graph_objects as go

def make_sankey(countryName):
    links = dict(
        source = [],
        target = [],
        value = [],
        hovertemplate='%{value} strains have spread from <a href = file:///C:/Users/Micah/Documents/covid_data_fun/%{source.label}_sankey.html>%{source.label}</a> to <a href = file:///C:/Users/Micah/Documents/covid_data_fun/%{target.label}_sankey.html>%{target.label}</a>' 
        )
    countryIndex = countryList.index(countryName)
    myCountryList = [countryName]
    for i in range(len(countryList)):
        if (i == countryIndex):
            if (relationalMatrix[i][i]>0):
                links["source"].append(0)
                links["target"].append(0)
                links["value"].append(relationalMatrix[i][i])
        else:
            if (relationalMatrix[countryIndex][i]>0):
                #myCountryList.append("<html><a href = file:///C:/Users/Micah/Documents/covid_data_fun/" + str(countryList[i]) + "_sankey.html>" + str(countryList[i]) + "</a></html>")
                myCountryList.append(str(countryList[i]))
                links["source"].append(0)
                links["target"].append(len(myCountryList)-1)
                links["value"].append(relationalMatrix[countryIndex][i])
            if (relationalMatrix[i][countryIndex]>0):
                #myCountryList.append("</html><a href = file:///C:/Users/Micah/Documents/covid_data_fun/" + str(countryList[i]) + "_sankey.html>" + str(countryList[i]) + "</a></html>")
                myCountryList.append(str(countryList[i]))
                links["source"].append(len(myCountryList)-1)
                links["target"].append(0)
                links["value"].append(relationalMatrix[i][countryIndex])
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = myCountryList,
          color = "blue",
          hovertemplate='<a href = file:///C:/Users/Micah/Documents/covid_data_fun/%{label}_sankey.html>%{label}</a>: %{value}'
        ),
        link = links
        )])

    fig.update_layout(title_text= str(countryName) + " Sankey Diagram", font_size=10)
    fig.write_html(str(countryName) + '_sankey.html', auto_open=False)

for country in countryList:
    make_sankey(country)

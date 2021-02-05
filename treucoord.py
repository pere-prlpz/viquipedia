#-*- coding: utf-8 -*-

import math
import pywikibot as pwb
import mwparserfromhell as hell

def distancia(lat1, lat2, lon1, lon2):
    dlat = lat1-lat2
    if dlat>180:
        dlat=360-dlat
    dlon = (lon1-lon2)*math.cos((lat1+lat2)/2)
    return 6371*math.sqrt(dlat**2+dlon**2)*math.pi/180

def coordwd(pag, repo = pwb.Site('ca').data_repository()):
    item = pwb.ItemPage.fromPage(pag)
    item_dict = item.get()
    clm_dict = item_dict["claims"]
    coords = clm_dict["P625"][0].toJSON()["mainsnak"]["datavalue"]["value"]
    lat = coords["latitude"]
    lon = coords["longitude"]
    return lat,lon

def esnum(x):
    try:
        a=(float(str(x)))
        return True
    except ValueError:
        return False

def coorpar(par):
    nums = [float(str(x)) for x in par if esnum(x)]
    if len(par)>3 and par[1] in ["N", "S"] and par[3] in ["E","W"] and len(nums)==2:
        lat = nums[0]
        lon = nums[1]
        if par[1] == "S":
            lat= -lat
        if par[3] == "W":
            lon= -lon
    elif len(par)>5 and par[2] in ["N", "S"] and par[5] in ["E","W"] and len(nums)==4:
        lat = nums[0]+nums[1]/60
        lon = nums[2]+nums[3]/60
        if par[2] == "S":
            lat= -lat
        if par[5] == "W":
            lon= -lon
    elif len(par)>7 and par[3] in ["N", "S"] and par[7] in ["E","W"] and len(nums)==6:
        lat = nums[0]+nums[1]/60+nums[2]/3600
        lon = nums[3]+nums[4]/60+nums[5]/3600
        if par[3] == "S":
            lat= -lat
        if par[7] == "W":
            lon= -lon
    elif len(nums)==2:
        lat = nums[0]
        lon = nums[1]
    else:
        lat=False
        lon=False
        print (par)
        print (nums)
    return (lat, lon)

site=pwb.Site('ca')
repo = site.data_repository()
articles = site.search("no hi pot haver més d'una etiqueta primària per pàgina")
print (articles)
infotaules = ["indret", "infotaula geografia política", "IGP"]
i=0
for article in articles:
    i=i+1
    print(i, article)
    text=article.get()
    code = hell.parse(text)
    plantilles=code.filter_templates();
    #print(plantilles)
    hihainfotaula=False
    pcoord =False
    ncoord=0
    for plantilla in plantilles:
        #print (plantilla.name)
        if plantilla.name.matches("coord"):
            print (plantilla.params)
            pcoord = plantilla.params
            ncoord = ncoord+1
            if (ncoord>1):
                print (ncoord, "PLANTILLES COORD")
        else:
            for infotaula in infotaules:
                if plantilla.name.matches(infotaula):
                    hihainfotaula = True
                    print(plantilla.name)
    if hihainfotaula and pcoord and 'display=title' in pcoord:
        print("coordenades a comprovar i eliminar")
        lat,lon = coorpar(pcoord)
        print (lat, lon)
        latwd, lonwd = coordwd(article)
        print (latwd, lonwd)
        d = distancia(latwd, lat, lonwd, lon)
        print (d, "km")
        if d<0.025 and ncoord==1:
            print("Es pot treure")
            for plantilla in plantilles:
                if plantilla.name.matches("coord"):
                    code.remove(plantilla)
                    textnou=str(code)
                    if textnou != text:
                        textnou = textnou.replace("\n\n\n\n","\n\n")
                        textnou = textnou.replace("\n\n\n","\n\n")
                        print ("Ha canviat. Desar.")
                        sumari = "Robot elimina plantilla coord redundant amb coordenades a "+str(d)+" km de les de Wikidata"
                        print(sumari)
                        article.put(textnou, sumari)
                    else:
                        print ("Segueix igual")
        else:
            print("Massa lluny")

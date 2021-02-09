#-*- coding: utf-8 -*-
# Treu la plantilla coord redundant amb la infotaula
# després de comprovar que les coordenades són al mateix lloc.

import math
import pywikibot as pwb
import mwparserfromhell as hell

def distancia(lat1, lat2, lon1, lon2):
    dlat = lat1-lat2
    if dlat>180:
        dlat=360-dlat
    dlon = (lon1-lon2)*math.cos((lat1+lat2)/2*math.pi/180)
    return 6371*math.sqrt(dlat**2+dlon**2)*math.pi/180

def coordwd(pag, repo = pwb.Site('ca').data_repository()):
    try:
        item = pwb.ItemPage.fromPage(pag)
        item_dict = item.get()
        clm_dict = item_dict["claims"]
        if "P625" in clm_dict:
            coords = clm_dict["P625"][0].toJSON()["mainsnak"]["datavalue"]["value"]
            lat = coords["latitude"]
            lon = coords["longitude"]
        else:
            lat=False
            lon=False
        claims ={}
        try:
            if "P2046" in clm_dict:
                supcl = clm_dict["P2046"][0].toJSON()["mainsnak"]["datavalue"]["value"]
                if supcl["unit"]== 'http://www.wikidata.org/entity/Q712226': #km2
                    claims["sup"] = float(supcl["amount"])
        except KeyError:
            print("Superfície sense valor a Wikidata")
        try:
            if "P2049" in clm_dict:
                supcl = clm_dict["P2049"][0].toJSON()["mainsnak"]["datavalue"]["value"]
                if supcl["unit"]== 'http://www.wikidata.org/entity/Q828224': #km
                    claims["ample"] = float(supcl["amount"])
        except KeyError:
            print("Amplada sense valor a Wikidata")
        try:
            if "P2043" in clm_dict:
                supcl = clm_dict["P2043"][0].toJSON()["mainsnak"]["datavalue"]["value"]
                if supcl["unit"]== 'http://www.wikidata.org/entity/Q828224': #km
                    claims["llarg"] = float(supcl["amount"])
        except KeyError:
            print("Llargada sense valor a Wikidata")
        return lat,lon,claims
    except pwb.NoUsername:
        print("Error .NoUsername")
        return False, False, False

def esnum(x):
    try:
        a=(float(str(x)))
        return True
    except ValueError:
        return False

def coorpar(par):
    nums = [float(str(x)) for x in par if esnum(x)]
    if len(par)>3 and par[1] in ["N", "S"] and par[3] in ["E","W","O"] and len(nums)==2:
        lat = nums[0]
        lon = nums[1]
        if par[1] == "S":
            lat= -lat
        if par[3] in ["W","O"]:
            lon= -lon
    elif len(par)>5 and par[2] in ["N", "S"] and par[5] in ["E","W","O"] and len(nums)==4:
        lat = nums[0]+nums[1]/60
        lon = nums[2]+nums[3]/60
        if par[2] == "S":
            lat= -lat
        if par[5] in ["W","O"]:
            lon= -lon
    elif len(par)>7 and par[3] in ["N", "S"] and par[7] in ["E","W","O"] and len(nums)==6:
        lat = nums[0]+nums[1]/60+nums[2]/3600
        lon = nums[3]+nums[4]/60+nums[5]/3600
        if par[3] == "S":
            lat= -lat
        if par[7] in ["W","O"]:
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

def posainforme(llista, final=False, paginfo=pwb.Page(pwb.Site('ca'),"Usuari:PereBot/coordenades duplicades")):
    text = "Pàgines a les que el bot no ha pogut comprovar que les coordenades en local "
    text = text+"són a la pràctica les mateixes que les de Wikidata.\n\n"
    llista.sort()
    text = text+"\n".join(llista)
    text = text+"\n\n[[Especial:Cerca/\"no hi pot haver més d'una etiqueta primària per pàgina\"]]\n\n"
    if final:
        acabat="Llista finalitzada."
    else:
        acabat="Llista en curs."
    text = text+""+acabat+"--~~~~"
    paginfo.put(text, "Informe articles amb coordenades duplicades")
    #print(text)
    return

site=pwb.Site('ca')
repo = site.data_repository()
articles = site.search("no hi pot haver més d'una etiqueta primària per pàgina")
print (articles)
infoIGP = ["infotaula geografia política", "IGP", "infotaula de bisbat", "Infotaula de geografia política"]
infoindret =["indret"]
infotaules = infoIGP+infoindret+["infotaula de vial urbà", "infotaula edifici", "edifici", "infotaula d'obra artística"]
i=0
it=0
ino=0
informetot = []
for article in articles:
    d=False
    altreswd=" "
    i=i+1
    print(i, article)
    informe = "# [["+article.title()+"]]: "
    text=article.get()
    code = hell.parse(text)
    plantilles=code.filter_templates();
    #print(plantilles)
    hihainfotaula=False
    present = ""
    pcoord =[]
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
                    present = infotaula
                    print(plantilla.name)
                    informe = informe+infotaula+"; "
    treure=False
    sumariextra=""
    if hihainfotaula and pcoord and 'display=title' in pcoord and ncoord==1:
        #print("coordenades a comprovar i eliminar")
        lat,lon = coorpar(pcoord)
        print (lat, lon)
        latwd, lonwd, altreswd = coordwd(article)
        print (latwd, lonwd, altreswd)
        if lat is False or latwd is False:
            print("Coordenades no trobades")
            continue
        d = distancia(latwd, lat, lonwd, lon)
        print (d, "km")
        if d<0.025 and ncoord==1:
            #print("Es pot treure")
            treure=True
        elif present in infoIGP and d<0.4:
            treure=True
            sumariextra=", suficient per articles amb infotaula geografia política"
        elif "ample" in altreswd and d<0.25*altreswd["ample"]:
            treure=True
            sumariextra=", suficient per un element de "+str(altreswd["ample"])+" km d'amplada"        
        elif "llarg" in altreswd and d<0.15*altreswd["llarg"]:
            treure=True
            sumariextra=", suficient per un element de "+str(altreswd["llarg"])+" km de llargada"        
        elif "sup" in altreswd and d<0.3*math.sqrt(altreswd["sup"]/5):
            treure=True
            sumariextra=", suficient per elements de "+str(altreswd["sup"])+" km2 de superfície"        
        else:
            print("Massa lluny")
    else:
        if "display=inline,title" in pcoord or "display= inline,title" in pcoord:
            altreswd=altreswd+"display=inline,title "
        if ncoord != 1:
            altreswd=altreswd+str(ncoord)+" coordenades"
        print("Coordenades no trobades o no hi ha infotaula")
    if treure:
        for plantilla in plantilles:
            if plantilla.name.matches("coord"):
                code.remove(plantilla)
        textnou=str(code)
        if textnou != text:
            textnou = textnou.replace("\n\n\n\n","\n\n")
            textnou = textnou.replace("\n\n\n","\n\n")
            #print ("Ha canviat. Desar.")
            sumari = "Robot elimina plantilla coord redundant amb coordenades a "+str(d)+" km de les de Wikidata"
            sumari = sumari+sumariextra
            it = it+1
            print(it, sumari)
            article.put(textnou, sumari)
        else:
            print ("Segueix igual")
            treure = False
            informe = informe +" No s'ha pogut trure coord. "
    if not treure:
        informe = informe+str(d)+" km "+str(altreswd)
        informetot.append(informe)
        ino = ino+1
        if ino==40 or ino % 200 == 0:
            posainforme(informetot)
posainforme(informetot, final=True)


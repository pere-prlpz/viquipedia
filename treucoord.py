#-*- coding: utf-8 -*-
# Treu la plantilla coord redundant amb la infotaula
# després de comprovar que les coordenades són al mateix lloc.

import math
import pywikibot as pwb
import mwparserfromhell as hell
from collections import Counter

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
        try:
            if "P1082" in clm_dict:
                popcl = clm_dict["P1082"][0].toJSON()["mainsnak"]["datavalue"]["value"]["amount"]
                claims["pop"] = float(popcl)
        except KeyError:
            print("No puc recuperar la població de Wikidata")
        try:
            if "P31" in clm_dict:
                claims["inst"] = [x.toJSON()["mainsnak"]["datavalue"]["value"]["numeric-id"] for x in clm_dict["P31"]]
        except KeyError:
            print("No puc recuperar la instància de Wikidata")
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

def tipuslim():
    tipus = {515:(.8, "una ciutat"), 1549591:(1.5, "una gran ciutat"), 123705:(.5, "un barri"),  
             184188:(1, "un cantó francès"), 18524218:(1, "un cantó francès"), 
             1402592:(1.5, "un grup d'illes"), 33837:(3, "un arxipèlag"),
             612741:(3, "un bosc nacional"), 4421:(0.3, "un bosc"),
             44782:(0.6, "un port"), 721207:(.6, "un port esportiu"), 1248784:(.8, "un aeroport"),
             152081:(.4, "un camp de concentració"), 46169:(3, "un parc nacional"),
             23397:(.15, "un llac"), 39594:(.3, "una badia"), 46831:(.8, "una serralada"),
             400080:(.1, "una platja"), 4022:(3, "un riu"), 12284:(.8, "un canal"), 39816:(.8, "una vall")}
    return(tipus)

def posainforme(llista, llistano, llistainst, final=False, 
                paginfo=pwb.Page(pwb.Site('ca'),"Usuari:PereBot/coordenades duplicades")):
    text = "Pàgines a les que el bot no ha pogut comprovar que les coordenades en local "
    text = text+"són a la pràctica les mateixes que les de Wikidata.\n\n"
    llista.sort()
    text = text+"\n== Amb infotaula ==\n\n"+"\n".join(llista)
    recompte = sorted(Counter(llistainst).items(), key=lambda item: item[1], reverse=True)
    puntrecompte = ["# {{Q|"+str(x[0])+"}}: "+str(x[1]) for x in recompte]
    text = text+"\n=== Instància (P31) ===\n\n"+"\n".join(puntrecompte)
    llistano.sort()
    text = text+"\n== Sense infotaula detectada ==\n\n"+"\n".join(llistano)
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
infoIGP = ["infotaula geografia política", "IGP", "infotaula de bisbat", 
           "Infotaula de geografia política", "Infotaula d'entitat de població",
           "Infotaula de municipi"]
infoindret =["indret", "infotaula muntanya","infotaula d'indret", "Infotaula indret"]
infotaules = infoIGP+infoindret+["infotaula de vial urbà", "infotaula edifici", 
                                 "edifici", "infotaula d'obra artística",
                                 "Infotaula Perfil Torneig Tennis", "Infotaula conflicte militar",
                                 "Jaciment arqueològic", "infotaula de lloc antic",
                                 "Infotaula element hidrografia"]
calcoors = ["cal coor", "cal coor esp", "cal coor cat"]
tipus = tipuslim()
i=0
it=0
ino=0
informetot = []
informeno = []
vistos = []
instancies = []
for article in articles:
    d=False
    altreswd=" "
    i=i+1
    print(i, article)
    try:
        if article in vistos:
            print ("ja vist")
            continue
        vistos.append(article)
        informe = "# [["+article.title()+"]]: "
        text=article.get()
    except pwb.NoPage:
        print("pàgina inexistent")
        continue
    code = hell.parse(text)
    plantilles=code.filter_templates();
    #print(plantilles)
    hihainfotaula=False
    present = ""
    pcoord =[]
    ncoord=0
    jatret=False
    for plantilla in plantilles:
        #print (plantilla.name)
        if plantilla.name.matches("coord"):
            print (plantilla.params)
            if plantilla.has("display") and "inline" in plantilla.get("display") and "title" in plantilla.get("display"):
                plantilla.add("display", "inline")
                textnou=str(code)
                if textnou != text:
                    textnou = textnou.replace("\n\n\n\n","\n\n")
                    textnou = textnou.replace("\n\n\n","\n\n")
                    #print ("Ha canviat. Desar.")
                    sumari = "Robot elimina display=title redundant de plantilla coord"
                    it = it+1
                    print(it, sumari)
                    article.put(textnou, sumari)
                    jatret=True
                else:
                    print ("Segueix igual")
                    treure = False
                    informe = informe +" No s'ha pogut treure title"
            elif plantilla.has("display") and "title" in plantilla.get("display"):
                pcoord = plantilla.params
                ptrobada = plantilla
                ncoord = ncoord+1
                if (ncoord>1):
                    print (ncoord, "PLANTILLES COORD")
            else:
                print("Plantilla coord sense title", str(plantilla))
                print(plantilla.has("display"))
        else:
            for infotaula in infotaules:
                if plantilla.name.matches(infotaula):
                    hihainfotaula = True
                    present = infotaula
                    print(plantilla.name)
                    informe = informe+infotaula+"; "
            for calcoor in calcoors:
                if plantilla.name.matches(calcoor):
                    code.remove(plantilla)
                    textnou=str(code)
                    if textnou != text:
                        textnou = textnou.replace("\n\n\n\n","\n\n")
                        textnou = textnou.replace("\n\n\n","\n\n")
                        #print ("Ha canviat. Desar.")
                        sumari = "Robot elimina plantilla "+calcoor+" redundant"
                        it = it+1
                        print(it, sumari)
                        article.put(textnou, sumari)
                        jatret=True
                    else:
                        print ("Segueix igual")
                        treure = False
                        informe = informe +" No s'ha pogut treure "+calcoor+". "
    if jatret:
        continue
    treure=False
    sumariextra=""
    if hihainfotaula and pcoord and ncoord==1: # and ptrobada.has("display") and ptrobada.get("display").strip()=="title" 
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
        elif "sup" in altreswd and d<0.3*math.sqrt(altreswd["sup"]/4):
            treure=True
            sumariextra=", suficient per elements de "+str(altreswd["sup"])+" km2 de superfície"        
        elif "pop" in altreswd and d<0.3*math.sqrt(altreswd["pop"]/8000/4):
            treure=True
            sumariextra=", suficient per elements de "+str(altreswd["pop"])+" habitants"
        elif "inst" in altreswd and any([tipus[x][0]>d for x in altreswd["inst"] if x in tipus]):
            tipusi = ", ".join([tipus[x][1] for x in altreswd["inst"] if x in tipus and tipus[x][0]>d])
            treure = True
            sumariextra=", suficient per "+tipusi
        elif "inst" in altreswd and 23442 in altreswd["inst"] and "pop" in altreswd and altreswd["pop"]>50 and d<1:
            treure = True
            sumariextra=", suficient per illa habitada"       
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
            if plantilla.name.matches("coord") and plantilla.has("display") and "title" in plantilla.get("display"):
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
    else:
        informe = informe+str(d)+" km "+str(altreswd) + " " + ", ".join([str(x) for x in pcoord if "source" in x])
        if hihainfotaula:
            informetot.append(informe)
            if "inst" in altreswd:
                instancies = instancies+altreswd["inst"]
        else:
            informeno.append(informe)
        ino = ino+1
        if ino==40 or ino % 200 == 0:
            posainforme(informetot, informeno, instancies)
posainforme(informetot, informeno, instancies, final=True)


#-*- coding: utf-8 -*-
# Treu la plantilla coord redundant amb la infotaula
# després de comprovar que les coordenades són al mateix lloc.

import math
from collections import Counter
from random import sample
import urllib
from urllib.parse import unquote
import sys
import itertools
from SPARQLWrapper import SPARQLWrapper, JSON
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

def posainforme(llista, llistano, llistainst, quickstatements, final=False, 
                paginfo=pwb.Page(pwb.Site('ca'),"Usuari:PereBot/coordenades duplicades")):
    text = "Pàgines a les que el bot no ha pogut comprovar que les coordenades en local "
    text = text+"són a la pràctica les mateixes que les de Wikidata.\n\n"
    llista.sort()
    text = text+"\n== Amb infotaula ==\n\n"+"\n".join(llista)
    recompte = sorted(Counter(llistainst).items(), key=lambda item: item[1], reverse=True)
    puntrecompte = ["# {{Q|"+str(x[0])+"}}: "+str(x[1]) for x in recompte]
    text = text+"\n=== Instància (P31) ===\n\n"+"\n".join(puntrecompte)
    text = text+"\n=== Quickstatements (P625) ===\n\n"+quickstatements+"\n"
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

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_parts(lloc):
    # monuments existents amb codi IPAC
    query = """# coordenades subdivisions d'un cantó
    SELECT ?lat ?lon
    WHERE {
      ?lloc wdt:P7938|wdt:P131? wd:Q"""+lloc+""".
    ?lloc p:P625 ?coordinate.
    ?coordinate psv:P625 ?coordinate_node .
    ?coordinate_node wikibase:geoLatitude ?lat .
    ?coordinate_node wikibase:geoLongitude ?lon .
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    llista=[]
    for mon in results["results"]["bindings"]:
        llista.append((float(mon["lat"]["value"]), float(mon["lon"]["value"])))
    return(llista)
    
def prodvect(centre, v1, v2):
    # producte vectorial (v1-centre)x(v2-v1)
    #print("centre:",centre, "v1:", v1, "v2:", v2)
    radi = (v1[0]-centre[0], v1[1]-centre[1])
    costat = (v2[0]-v1[0], v2[1]-v1[1])
    return(radi[0]*costat[1]-radi[1]*costat[0])

def punttriangle(punt, triangle):
    #print("punt:", punt, "triangle:", triangle)
    if prodvect(punt, triangle[0], triangle[1])>0:
        if prodvect(punt, triangle[1], triangle[2])>0:
            if prodvect(punt, triangle[2], triangle[0])>0:
                return(True)
            else:
                return(False)
        else:
            return(False)
    else:
        if prodvect(punt, triangle[1], triangle[2])<0:
            if prodvect(punt, triangle[2], triangle[0])<0:
                return(True)
            else:
                return(False)
        else:
            return(False)

def puntsdins(centre, llocs):
    #triangles d'un núvol de llocs que contenen el centre i total de triangles
    #print("centre:", centre, "llocs:", llocs)
    if len(llocs)>220:
        llocs=sample(llocs, 220)
    dins=[punttriangle(centre,x) for x in itertools.combinations(llocs,3)]
    return(sum(dins), len(dins))
   
def puntsadinslloc(qlloc, centres):
    llocs=get_parts(qlloc)
    return([puntsdins(x, llocs) for x in centres])

def urlloc(lloc, llarg=True):
    if llarg:
        url= "https://query.wikidata.org/#SELECT%20%3Flloc%20%3FllocLabel%20%3Fcoordinate%20%3Flayer%0AWHERE%20%7B%0A%20%20%3Flloc%20wdt%3AP7938%7Cwdt%3AP131%3F%20wd%3AQ"
        url= url+lloc
        url=url+".%0A%20%20%3Flloc%20wdt%3AP625%20%3Fcoordinate.%0A%20%20%3Flloc%20wdt%3AP31%20%3Flayer.%0ASERVICE%20wikibase%3Alabel%20%7Bbd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cca%2Cen%2Ces%22.%7D%20%20%20%0A%7D%0A%23defaultView%3AMap"
    else:
        url= "https://query.wikidata.org/#SELECT%20%3Fll%20%3FllLabel%20%3Fcoordinate%20%3Flayer%0AWHERE%20%7B%0A%20%20%3Fll%20wdt%3AP7938%7Cwdt%3AP131%3F%20wd%3AQ"
        url= url+lloc
        url=url+'.%0A%3Fll%20wdt%3AP625%20%3Fcoordinate.%0A%3Fll%20wdt%3AP31%20%3Flayer.%0ASERVICE%20wikibase%3Alabel%20%7Bbd%3AserviceParam%20wikibase%3Alanguage%20"ca".%7D%20%20%20%0A%7D%0A'
    return(url)

def quickcoord(lloc, latwd, lonwd, lat, lon):
    indexq="Q"+lloc
    #Treu
    instruccio = "-"+indexq+"|"+"P625"+"|"+"@"+str(latwd)+"/"+str(lonwd) +"||"
    #Posa
    instruccio = instruccio + indexq+"|"+"P625"+"|"+"@"+str(lat)+"/"+str(lon)
    instruccio = instruccio + "|S143|Q199693"+"||"
    return(instruccio)

# el programa comença aquí
site=pwb.Site('ca')
repo = site.data_repository()
articles = site.search("no hi pot haver més d'una etiqueta primària per pàgina")
print (articles)
infoIGP = ["infotaula geografia política", "IGP", "infotaula de bisbat", 
           "Infotaula de geografia política", "Infotaula d'entitat de població",
           "Infotaula de municipi"]
infoindret =["indret", "infotaula muntanya","infotaula d'indret", "Infotaula indret"]
infoedifici =["infotaula de vial urbà", "infotaula edifici", "edifici"]
infoaltres = ["infotaula d'obra artística",
                "Infotaula Perfil Torneig Tennis", "Infotaula conflicte militar",
                "Jaciment arqueològic", "infotaula de lloc antic",
                "Infotaula element hidrografia", "infotaula esdeveniment"]
infotaules = infoIGP+infoindret+infoedifici+infoaltres
calcoors = ["cal coor", "cal coor esp", "cal coor cat"]
tipus = tipuslim()
entitatsadm = [18524218, 184188, 2469744, 28006240, 3141478, 61763799, 1518096, 2039348,
               1149652, 2177636, 16543169, 192287, 211690, 41067667, 1093829, 1146429]
entitatsadmtreure = [18524218, 184188]
i=0
it=0
ino=0
informetot = []
informeno = []
vistos = []
instancies = []
quick = ""
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
    infotaulesart = []
    present = ""
    pcoord =[]
    ncoord=0
    jatret=False
    for plantilla in plantilles:
        #print (plantilla.name)
        if (plantilla.name.matches("coord") or plantilla.name.matches("coordenades")):
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
                    infotaulesart.append(plantilla)
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
    if len(infotaulesart)>1:
        print("Dues infotaules:", infotaulesart)
        plantillaIGP=False
        plantillaedifici=False
        for infotaulart in infotaulesart:
            for infotaula in infoIGP:
                if infotaulart.name.matches(infotaula):
                    plantillaIGP=infotaulart
            for infotaula in infoedifici:
                if infotaulart.name.matches(infotaula):
                    plantillaedifici=infotaulart
        if plantillaIGP and plantillaedifici:
            print("Infotaula de geografia política i infotaula d'edifici")
            if (not plantillaIGP.has("coord_display")) and (not plantillaedifici.has("coord_display")):
                plantillaedifici.add("coord_display", "inline")
                print("Posat coord_display=inline a la infotaula d'edifici")
                textnou=str(code)
                if textnou != text:
                    textnou = textnou.replace("\n\n\n\n","\n\n")
                    textnou = textnou.replace("\n\n\n","\n\n")
                    #print ("Ha canviat. Desar.")
                    sumari = "Robot posa coord_display=inline a la infotaula d'edifici"
                    it = it+1
                    print(it, sumari)
                    article.put(textnou, sumari)
                    jatret=True
                else:
                    print ("Segueix igual")
                    treure = False
                    informe = informe +" No s'ha pogut posar coord_display=inline a la infotaula d'edifici"
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
    if not treure and "inst" in altreswd and any([x in altreswd["inst"] for x in entitatsadm]):
        print ("provant triangles formats per entitats contingudes a l'entitat (P131)")
        centres=[(latwd, lonwd), (lat, lon)]
        lloc = pwb.ItemPage.fromPage(article).title()[1:]
        compara = puntsadinslloc(lloc, centres)
        print (compara)
        if compara[0][1]>5 and compara[0][0]>compara[1][0]:
            treure = True
            sumariextra = ", i no tan al mig dels elements localitzats aquí "+"["+urlloc(lloc, llarg=False)+"]"
        else:
            informe = informe +" triangles: wd:"+str(compara[0])+" wp:"+str(compara[1])+"["+urlloc(lloc)+"] "
            informe = informe + quickcoord(lloc, latwd, lonwd, lat, lon)+" "
            if compara[0][1]>5 and compara[0][0]<compara[1][0]:
                if any([x in altreswd["inst"] for x in entitatsadmtreure]):
                    quick = quick + quickcoord(lloc, latwd, lonwd, lat, lon)+"\n"
                    informe = informe + "Pujar. "
                else:
                    informe = informe + "Pujaria. "
    if treure:
        for plantilla in plantilles:
            if (plantilla.name.matches("coord") or plantilla.name.matches("coordenades")) and plantilla.has("display") and "title" in plantilla.get("display"):
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
            posainforme(informetot, informeno, instancies, quick)
posainforme(informetot, informeno, instancies, quick, final=True)


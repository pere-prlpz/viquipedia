#-*- coding: utf-8 -*-

# posa categories de premiats a partir de Wikidata.
# La versió actual només tracta persones. 
# Pendent fer servir les categories abans excloses (encara hi ha la llista i el patró)
# per posar coses que no són persones a les altres.

import pywikibot as pwb
from pywikibot import pagegenerators
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import pickle
import sys
import urllib
from urllib.parse import unquote

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_catprals():
    print("Carregant categories principals de premis de Wikidata")
    query="""# Categories principals de premis
    SELECT DISTINCT ?premi ?cat ?categoria 
    WHERE {
      ?persona wdt:P166 ?premi.
      ?persona wdt:P31 wd:Q5.
      ?premi wdt:P910 ?cat.
      MINUS {?premi wdt:P2517 []}
      ?categoria schema:about ?cat.
      ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def get_catpremiats():
    print("Carregant categories de receptors de premis de Wikidata")
    query="""# Categories de receptors de premis
    SELECT DISTINCT ?premi ?cat ?categoria 
    WHERE {
      ?premi wdt:P2517 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def dicccategories():
    premis = get_catprals()
    diccpral = {}
    print("Categories principals",len(premis))
    for premi in premis:
        if "categoria" in premi:
            #print(premi)
            qpremi = premi["premi"]["value"].replace("http://www.wikidata.org/entity/","")
            #print(qpremi)
            diccpral[qpremi] = urllib.parse.unquote(premi["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
    premis = get_catpremiats()
    print("Categories premiats",len(premis))
    diccprem = {}
    for premi in premis:
       if "categoria" in premi:
            #print(premi)
            qpremi = premi["premi"]["value"].replace("http://www.wikidata.org/entity/","")
            #print(qpremi)
            diccprem[qpremi] = urllib.parse.unquote(premi["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
    return(diccpral, diccprem)

# restringit a persones
def get_premiats():
    print("Carregant articles de premiats de Wikidata")
    query="""# Articles de premiats
    SELECT DISTINCT ?persona ?article ?premi ?inst
    WHERE {
      ?persona wdt:P166 ?premi.
      ?persona wdt:P31 ?inst.
        ?article schema:about ?persona.
        ?article schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def classifica(res, qprem=[]):
    print ("Agrupant articles per premi rebut")
    dicsi={}
    dicno={}
    for registre in res:
        article = registre["article"]["value"].replace("https://ca.wikipedia.org/wiki/", "")
        article = urllib.parse.unquote(article).replace("_"," ")
        if "inst" in registre.keys():
            inst = registre["inst"]["value"].replace("http://www.wikidata.org/entity/","")
            if inst != "Q5":
                print ("No és una persona:", registre)
                continue
        if "premi" in registre.keys():
            premi = registre["premi"]["value"].replace("http://www.wikidata.org/entity/","")
            if premi in qprem:
                if premi not in dicsi.keys():
                    #print(premi)
                    dicsi[premi]=[]
                dicsi[premi].append(article)
            else:
                if premi in dicno.keys():
                    dicno[premi] = dicno[premi]+1
                else:
                    dicno[premi] = 1
        else:
            print ("Error: s'esperava un premi i al registre no n'hi ha")
    return(dicsi, dicno)

def artcat(catnom, site=pwb.Site('ca'), profunditat=5):
    # llista d'articles d'una categoria
    cat = pwb.Category(site,catnom)
    articles = pagegenerators.CategorizedPageGenerator(cat, recurse=profunditat)
    llistart = []
    for art in articles:
        llistart.append(art.title())
    return(llistart)

def posacat(cat, catsno=[], arts=[], site=pwb.Site('ca')):
    #print(cat)
    for art in arts:
        print(art)
        pag=pwb.Page(site, art)
        try:
            textvell=pag.get()
        except pwb.exceptions.IsRedirectPageError:
            print("Redirecció")
            continue
        except pwb.exceptions.NoPageError:
            print("La pàgina no existeix")
            continue
        if re.search("\[\["+cat+"(\|.*)?\]\]", textvell):
            print("La categoria ja hi és")
            continue
        if re.search("\]\]( *\n *)*$", textvell):
            #print("Categoria al final")
            textnou = re.sub("\]\]( *\n *)*$","]]\n[["+cat+"]]\n", textvell, count=1)
        elif re.search("\[\[[Cc]ategor(ia|y) ?:", textvell):
            print ("Categoria al principi")
            textnou = re.sub("\[\[[Cc]ategor(ia|y) ?:","[["+cat+"]]\n[[Categoria:", textvell, count=1)
        else:
            print ("No trobat on posar la categoria")
            continue
        if textnou != textvell and False: # anul·lat (només per proves)
            pagprova = pwb.Page(site, "Usuari:PereBot/taller")
            sumari = "Robot copia [["+art+"]] tot fent proves"
            pagprova.put(textnou, sumari)
        sumtreu=""
        if textnou != textvell:
            for catno in catsno:
                if catno == cat:
                    print(catno, "redundant amb si mateixa")
                    continue
                if re.search("\[\["+catno+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+catno+"\]\]\n?", "", textnou)
                    #textnou=re.sub("\[\["+catno+"\|.*\]\]", "", textnou)
                    sumtreu=" i treu la [["+catno+"]] redundant"
            sumari = "Robot posa la [["+cat+"]] a partir de Wikidata"+sumtreu
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
    return

def miracat(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, vell=False, prof=20):
    print(catnom, prof)
    if catnom in dicc:
        font = "dicc nou"
        art0 = dicc[catnom]["art0"]
        cat0 = dicc[catnom]["cat0"]
    elif vell and catnom in diccvell:
        font = "dicc vell"
        art0 = diccvell[catnom]["art0"]
        cat0 = diccvell[catnom]["cat0"]
    else:
        font = "llegit"
        cat = pwb.Category(site,catnom)
        articles = pagegenerators.CategorizedPageGenerator(cat, recurse=0)
        art0 = []
        for art in articles:
            art0.append(art.title())
        categories = pagegenerators.SubCategoriesPageGenerator(cat, recurse=0)
        cat0 = []
        for cat in categories:
            cat0.append(cat.title())
        dicc[catnom] = {"art0":art0, "cat0":cat0}
        diccvell[catnom] = {"art0":art0, "cat0":cat0}
    art1 = set(art0)
    cat1 = set(cat0)
    if prof<=0:
        print("Arribat al límit de profunditat")
        print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
        return(art0, cat0, dicc, diccvell, art1, cat1)
    for cat in cat0:
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, prof=prof-1)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)

def desadicc(diccatvell):
    fitxer = r"C:\Users\Pere\Documents\perebot\categories.pkl"
    pickle.dump(diccatvell, open(fitxer, "wb")) 
    print("Diccionari vell desat. Diccionari:",lencats,"Diccionari vell:", len(diccatvell))
    return

# el programa comença aquí
try:
    diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
except FileNotFoundError:
    print ("Fitxer de categories no trobat. Començant de nou.")
    diccatvell={}
# versió de quan la query no filtrava el que no són persones
notocar = ["Categoria:Grammy a l'àlbum de l'any", "Categoria:Pel·lícules guanyadores de l'Ós d'Or",
"Categoria:BAFTA", "Categoria:Guanyadors del Globus d'Or al millor director",
"Categoria:Guanyadores del Globus d'Or a la millor actriu secundària",
"Categoria:Guanyadors del Premi Booker", "Categoria:Premis Ramon Llull de novel·la",
"Categoria:Premis de traducció","Categoria:Figueres", "Categoria:Copa Intertoto de la UEFA",
"Categoria:Premis", "Categoria:Guanyadors del Premi Laurence Olivier",
"Categoria:Guanyadors del Premi Tony"]
notocarreg = "Categoria:(Jocs Olímpics|Festival|Foment|.*(premi Oscar|[Pp]el·lícules|BAFTA|Goncourt|[Pp]remi Goya)|Globus d.Or|actriu|cançó)"
# versió que anul·la filtres de categories perquè ja s'elimina el que no són persones
notocar = []
notocarreg = "Categoria:Pel·lícules"
#
diccpral, diccprem = dicccategories()
#print(diccpral)
#print(diccprem)
print("Diferència (categories principals usades per premiats):", len(set(diccpral.keys())-set(diccprem.keys())))
qpremis = list(set(diccpral.keys()).union(set(diccprem.keys())))
#print(qpremis) 
print("Premis a mirar:",len(qpremis))
premiats = get_premiats()
print("Premiats:", len(premiats))
premisi, premino = classifica(premiats, qpremis)
print("Categories a posar", len(premisi))
print("Categories a no posar", len(premino))
print ("Informació: categories per crear")
tunino = []
qunino = []
unino=premino
for uni in unino.keys():
    if unino[uni]>=5:
        #print(uni, unino[uni])
        tunino.append((unino[uni],uni.replace("http://www.wikidata.org/entity/Q","")))
tunino = sorted(tunino, reverse=True)
#print(tunino)
textunino = "Premis que apareixen a {{P|166}} de persones amb article "
textunino = textunino + "però sense categoria a la Viquipèdia, i nombre "
textunino = textunino + "d'articles que hi anirien si existís.\n\n"
textunino = textunino + "No tots són categories a crear.\n\n"
totalunino = 0
for tuni in tunino:
    textunino = textunino + "# {{Q|"+tuni[1]+"}}:"+str(tuni[0])+"\n"
    #print("* {{Q|"+tuni[1]+"}}", tuni[0]) 
    qunino.append("Q"+tuni[1])
    totalunino = totalunino+tuni[0]
print ("Total", totalunino)
textunino = "\n"+textunino + "Total: "+str(totalunino)+"\n\n"
if True: #edita or creacat:
    pag = pwb.Page(pwb.Site('ca'), "Usuari:PereBot/premis")
    pag.put(textunino, "Robot actualitza premis sense categoria")
total = len(premisi)
icat=0
diccat={}
lencats = 0
inferrors=""
for premi in list(premisi.keys()):
    icat=icat+1
    print(icat,"/", total, premi)
    print("Wikidata:",len(premisi[premi]))
    if premi in diccpral:
        print("Principal:", diccpral[premi])
        catposa = diccpral[premi]
        catred = []
    if premi in diccprem:
        print("Premiats:", diccprem[premi])
        catposa = diccprem[premi]
        if premi in diccpral:
            catred = [diccpral[premi]]
        else:
            catred = []
    print(catposa, catred)
    # comprovació treta d'universitats.py que s'hauria d'adaptar aquí
    #if not(re.match("[Cc]ategor(ia|y):", catposa)):
    #    print("No és una categoria")
    #    inferrors = inferrors + cat + " no és una categoria\n"
    #    continue
    if catposa in notocar or re.search(notocarreg, catposa):
        print("Categoria complicada. No faig res.")
        continue
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(catposa, dicc=diccat, diccvell=diccatvell, vell=True, prof=5)
    #print(articles)
    print("Categoria:",len(articles))
    if len(diccat)>lencats:
        lencats=len(diccat)
        desadicc(diccatvell)
    posar=set(premisi[premi])-set(articles)
    print("Posar (provisionalment):", posar, len(posar))
    if len(posar)>0:
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(catposa, dicc=diccat, diccvell=diccatvell, vell=False, prof=5)
        posar=set(premisi[premi])-set(articles)
        print("Posar (definitivament):", posar, len(posar))
        if len(diccat)>lencats:
            lencats=len(diccat)
            desadicc(diccatvell)
        posacat(catposa, catred, arts=posar)
print("Total:",total)
print(inferrors)
        
#-*- coding: utf-8 -*-
# Categoritza per lloc de la mort d'acord amb Wikidata

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

def get_no(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# categories de nascuts o relacionats amb estats, comunitats, etc.
    SELECT DISTINCT ?lloc ?cat ?categoria
    WHERE {
        VALUES ?grans {wd:Q5107 wd:Q3624078 wd:Q10742 wd:Q35657 wd:Q15304003 wd:Q83057 wd:Q3336843 wd:Q3024240}
        ?lloc wdt:P31 ?grans.
        ?lloc wdt:P1465 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\noorigen.pkl"
        pickle.dump(wd, open(fitxer, "wb")) 
    return (wd)

def carrega_no(disc=False):
    try:
        a=pickle.load(open(r"C:\Users\Pere\Documents\perebot\noorigen.pkl", "rb"))
    except FileNotFoundError:
        print ("Fitxer origens no mirar no trobat. Important de Wikidata.")
        a=get_no()
    return(a)

def get_catwd(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# categories persones per lloc
    SELECT DISTINCT ?lloc ?cat ?categoria
    WHERE {
        ?lloc wdt:P1465 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\catorigen.pkl"
        pickle.dump(wd, open(fitxer, "wb")) 
    return (wd)

def carrega_catwd(desa=True, disc=False):
    if disc:
        print("llegint dades del disc")
        a=pickle.load(open(r"C:\Users\Pere\Documents\perebot\catorigen.pkl", "rb"))
    else:
        a=get_catwd(desa)
    return(a)

def get_nascutswd(qllocs):
    print("Carregant articles de Wikidata")
    query="""# articles de persones nascudes en uns llocs
    SELECT DISTINCT ?lloc ?persona ?article
    WHERE {
        VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
        ?persona wdt:P31 wd:Q5.
        ?persona wdt:P20 ?lloc.
        ?article schema:about ?persona.
        ?article schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def get_redundantswd(qllocs):
    print("Carregant categories redundants de Wikidata")
    query="""# categories redundants per origen
    SELECT DISTINCT ?lloc ?redundant ?llocLabel ?categoria
    WHERE {
      VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
      ?lloc wdt:P131+ ?redundant.
        ?redundant wdt:P1465 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ca" .
    }
    }"""
    #print(query)
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def artcat(catnom, site=pwb.Site('ca'), profunditat=8):
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
        except pwb.IsRedirectPage:
            print("Redirecció")
            continue
        except pwb.NoPage:
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


# el programa comença aquí
disc=False
discvp=False
desa=True
edita=True
editacat=True
creacat=False
arguments = sys.argv[1:]
if len(arguments)>0:
    if "-disc" in arguments:
        disc=True
        arguments.remove("-disc")
    if "-discvp" in arguments:
        discvp=True
        arguments.remove("-discvp")
    if "-discwp" in arguments:
        discvp=True
        arguments.remove("-discwp")
    if "-nodesis" in arguments:
        desa=False
        arguments.remove("-nodesis")
    if "-noeditis" in arguments:
        edita=False
        editacat=False
        arguments.remove("-noeditis")
    if "-creacat" in arguments:
        creacat=True
        edita=False
        arguments.remove("-creacat")
    if "-max" in arguments:
        imax=arguments.index("-max")
        if len(arguments)>imax:
            maxcats=int(arguments.pop(imax+1))
        arguments.remove("-max")
    else:
        maxcats=4
nomirar = carrega_no()
#print (nomirar)
catwd = carrega_catwd(disc=disc)
#print(catwd)
if False: #True canviar per ignorar els grans
    qno = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in nomirar]
else:
    qno = []
print ("Llocs grans a ignorar:", qno)
print(len(qno))
qllocs = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in catwd]
#print (qllocs)
print(len(qllocs))
qsi = list(set(qllocs)-set(qno))
#print(qsi)
print("Llocs a mirar:",len(qsi))
dcats = {x["lloc"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in catwd}
#print(dcats)
print(len(dcats))
dcats = {x: dcats[x] for x in qsi}
#print(dcats)
print(len(dcats))
ncats=len(dcats)
midagrup = 25
qgrups = [qsi[x:x+midagrup] for x in range(0,len(qsi), midagrup)]
#print(qgrups)
print(len(qgrups))
total=0
icat=0
for qgrup in qgrups:
    print(qgrup)
    nascutswd = get_nascutswd(qgrup) 
    #print(nascutswd)
    total = total+len(nascutswd)
    print(len(nascutswd))
    nascutsllocwd = {}
    for art in nascutswd:
        lloc = art["lloc"]["value"].replace("http://www.wikidata.org/entity/","")
        article = urllib.parse.unquote(art["article"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
        if lloc in nascutsllocwd:
            nascutsllocwd[lloc].append(article)
        else:
            nascutsllocwd[lloc]=[article]
    #print(nascutsllocwd)
    print (len(nascutsllocwd), len(qgrup))
    for qlloc in qgrup:
        icat=icat+1
        cat=dcats[qlloc]
        print(icat,"/", ncats, cat, qlloc)
        if not(qlloc in nascutsllocwd):
            print("No cal buscar")
            continue
        articles=artcat(cat)
        #print(articles)
        print(len(articles))
        posar=set(nascutsllocwd[qlloc])-set(articles)
        print("Posar:", posar, len(posar))
        if len(posar)>0:
            redundantswd = get_redundantswd([qlloc])
            #print(redundantswd)
            redundants = []
            for red in redundantswd:
                #print(red)
                redundants.append(urllib.parse.unquote(red["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "))
            print(redundants)
            posacat(cat, redundants, arts=posar)
        
print(total)

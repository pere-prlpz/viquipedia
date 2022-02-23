#-*- coding: utf-8 -*-

# posar categories per ocupació i origen

import pywikibot as pwb
from pywikibot import pagegenerators
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import pickle
import sys
import urllib
import urllib.request
#import json
from urllib.parse import unquote

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_query(query):
    print("Carregant query")
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    #print(wd)
    return (wd)

def miracatinv(cat, dicc, prof=20, noinc=[]):
    lliures = {cat}
    super = {cat}
    while len(lliures)>0 and prof>0:
        lliures = {x for x in dicc if (not lliures.isdisjoint(set(dicc[x]["cat0"])) and x not in noinc)}
        #print("Directes:", lliures)
        lliures = lliures - super
        super = lliures | super
        #print("Tots:", super)
        #print("Lliures:", lliures)
    return(super) 

def miracat(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, vell=False, prof=20, noseg=[], noinc=[]):
    # noseg: categories que llegeix però no continua més avall
    # noinc: categories que no llegeix
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
        if cat in noinc:
            continue
        if cat in noseg:
            profseguent = 0
        else:
            profseguent = prof-1
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, prof=profseguent, noseg=noseg, noinc=noinc)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)

def desadicc(diccatvell, diccatnou=[1], lendic=0):
    if len(diccatnou)>lendic:
        fitxer = r"C:\Users\Pere\Documents\perebot\categories.pkl"
        pickle.dump(diccatvell, open(fitxer, "wb")) 
        lennou = len(diccatnou)
        print("Diccionari vell desat. Diccionari:",lennou,"Diccionari vell:", len(diccatvell))
        return (lennou)
    else:
        return(lendic)

def inicialitzadicc():
    # carregar fitxer de categories
    try:
        diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
    except FileNotFoundError:
        print ("Fitxer de categories no trobat. Començant de nou.")
        diccatvell={}
    diccat = {}
    lencats = 0
    return(diccat, diccatvell, lencats)

def posacat(cat, catsno=[], arts=[], site=pwb.Site('ca'), extrasumari=""):
    #print(cat)
    if not(re.search("^[Cc]ategoria:", cat)):
        print("Això no sembla una categoria:",cat)
        return
    for art in arts:
        print(art)
        pag=pwb.Page(site, art)
        try:
            textvell=pag.get()
        except pwb.IsRedirectPage:
            print("Redirecció:", pag)
            continue
        except pwb.NoPage:
            print("La pàgina no existeix:", pag)
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
            print ("No trobat on posar la categoria. Categoria al final.")
            textnou = textvell + "\n[["+cat+"]]\n"
        if textnou != textvell and False: # anul·lat (només per proves)
            pagprova = pwb.Page(site, "Usuari:PereBot/taller")
            sumari = "Robot copia [["+art+"]] tot fent proves"
            pagprova.put(textnou, sumari)
        sumtreu=""
        if textnou != textvell:
            for catno in catsno:
                if catno == cat:
                    #print(catno, "redundant amb si mateixa")
                    continue
                if re.search("\[\["+re.escape(catno)+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+re.escape(catno)+"\]\]\n?", "", textnou)
                    #textnou=re.sub("\[\["+catno+"\|.*\]\]", "", textnou)
                    sumtreu=" i treu la [["+catno+"]] redundant"
            sumari = "Robot posa la [["+cat+"]] "+extrasumari+sumtreu
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
    return


# el programa comença aquí ----------------------------------------

# llegir dades de Wikidata
ocupawd = get_query("""# Categories d'ocupacions
SELECT DISTINCT ?ocupacio ?ocupacioLabel ?cat ?categoria ?conte ?conteLabel
WHERE {
  ?ocupacio wdt:P31 wd:Q28640.
  ?ocupacio wdt:P910 ?cat.
    ?categoria schema:about ?cat.
    ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
  OPTIONAL{?cat wdt:P4224 ?conte}
  SERVICE wikibase:label {bd:serviceParam wikibase:language "ca" . } 
}""")
#print(ocupawd)
docucat = {x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in ocupawd}
#print(docucat)
print("docucat",len(docucat))
dcatocu = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):\
x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/","")\
for x in ocupawd}
print("dcatocu",len(dcatocu))

llocswd = get_query("""# categories persones per lloc
SELECT DISTINCT ?lloc ?cat ?categoria
WHERE {
    ?lloc wdt:P1464|wdt:P1792 ?cat.
    ?categoria schema:about ?cat.
    ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
dlloccat = {x["lloc"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in llocswd}
#print(dlloccat)
print("dlloccat", len(dlloccat))
dcatlloc = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):\
x["lloc"]["value"].replace("http://www.wikidata.org/entity/","")\
for x in llocswd}
#print(dcatlloc)
print("dcatlloc", len(dcatlloc))

cat2wd=get_query("""# categories de persones amb temes associats
SELECT DISTINCT ?cat ?categoria ?associat WHERE {
  ?cat wdt:P31 wd:Q4167836.
  ?cat wdt:P4224 wd:Q5.
  ?categoria schema:about ?cat.
  ?cat wdt:P971 ?associat.
  ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
dcatrel = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):[]\
for x in cat2wd}
#print(dcatrel)
for x in cat2wd:
    cat = urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
    tema = x["associat"]["value"].replace("http://www.wikidata.org/entity/","")
    dcatrel[cat].append(tema)
#print(dcatrel)
print("dcatrel", len(dcatrel))
dintercat = {}
for cat in dcatrel:
    if len(dcatrel[cat]) != 2:
        continue
    qlloc = ""
    qocu = ""
    for tema in dcatrel[cat]:
        if tema in docucat and qocu=="":
            qocu = tema
        if tema in dlloccat and qlloc =="":
            qlloc = tema
    if qlloc != "" and qocu !="":
        dintercat[cat] = {"qocu":qocu, "qlloc":qlloc, "cocu":docucat[qocu], "clloc":dlloccat[qlloc]}
#print(dintercat, len(dintercat))
#for cat in dintercat: print(cat, dintercat[cat]["cocu"], dintercat[cat]["clloc"])
print("dintercat", len(dintercat))

cat1perswd = get_query("""# categories principals d'una persona
SELECT ?item ?cat ?categoria WHERE {
  ?item wdt:P31 wd:Q5.
  ?item wdt:P910 ?cat.
  ?categoria schema:about ?cat.
  ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
cat1pers = [urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in cat1perswd]
print(cat1pers)
print("cat1pers", len(cat1pers))

# carregar fitxer de categories
diccat, diccatvell, lencats = inicialitzadicc()
# Comencem a buscar i posar categories
for cat in dintercat:
    print (cat)
    if re.search("catalans del sud|històrics|contemporanis|nord-catalans|catalans del nord", cat.casefold()):
        continue
    catA= dintercat[cat]["cocu"]
    catB= dintercat[cat]["clloc"]   
    print("Intersecant:",catA, catB)
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, prof=14, noseg=cat1pers)
    desadicc(diccatvell, diccat, lencats)
    art0, cat0, diccat, diccatvell, articlesA, cat1=miracat(catA, dicc=diccat, diccvell=diccatvell, vell=True, prof=14, noinc=cat1pers)
    desadicc(diccatvell, diccat, lencats)
    art0, cat0, diccat, diccatvell, articlesB, cat1=miracat(catB, dicc=diccat, diccvell=diccatvell, vell=True, prof=14, noinc=cat1pers)
    desadicc(diccatvell, diccat, lencats)
    posar = (articlesA & articlesB) - articles
    print("Posar provisionalment:", posar, len(posar))
    if len(posar)>0:
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, noseg=cat1pers)
        desadicc(diccatvell, diccat, lencats)
        if len(posar-articles)==0:
            print("Ja hi són tots")
            continue
        art0, cat0, diccat, diccatvell, articlesA, cat1=miracat(catA, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, noinc=cat1pers)
        desadicc(diccatvell, diccat, lencats)
        art0, cat0, diccat, diccatvell, articlesB, cat1=miracat(catB, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, noinc=cat1pers)
        desadicc(diccatvell, diccat, lencats)
        posar = (articlesA & articlesB) - articles
        print("Posar definitivament:", posar, len(posar))
        redundants = miracatinv(cat, diccatvell, noinc=cat1pers)
        print("Redundants:",redundants)
        sumari = "intersecant [["+catA+"]] i [["+catB+"]]"
        posacat(cat, catsno=redundants, arts=posar, extrasumari=sumari)
        diccat[cat]["art0"].extend(posar)
        diccatvell[cat]["art0"].extend(posar)    

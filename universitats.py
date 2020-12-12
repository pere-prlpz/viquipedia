#-*- coding: utf-8 -*-

# programa per posar les categories d'estudiants per universitat
# Arguments:
# -noeditis No edita. Només dóna informació de les categories que falten.
# -disc No fa una query sinó que agafa els resultats del disc
# -discvp No llegeix la viquipèdia sinó el disc (per decidir què ha d'editar)
# Exemple:
# python universitats.py -noeditis

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

def get_wd(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# articles i categories d'estudiants i universitats
    SELECT DISTINCT ?persona ?uni ?article ?cat ?categoria
    WHERE {
      ?persona wdt:P69 ?uni.
      ?article schema:about ?persona.
      ?article schema:isPartOf <https://ca.wikipedia.org/>.
      OPTIONAL {
        ?uni wdt:P3876 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
      }
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    uniwd = results["results"]["bindings"]
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\estunibrut.pkl"
        pickle.dump(uniwd, open(fitxer, "wb")) 
    return (uniwd)

def carrega_wd(desa=True, disc=False):
    if disc:
        print("llegint dades del disc")
        unibrut=pickle.load(open(r"C:\Users\Pere\Documents\perebot\estunibrut.pkl", "rb"))
    else:
        unibrut=get_wd(desa)
    return(unibrut)

def classifica(res, desa=True):
    print ("Agrupant articles per universitat")
    dicsi={}
    dicno={}
    for registre in res:
        article = registre["article"]["value"].replace("https://ca.wikipedia.org/wiki/", "")
        article = urllib.parse.unquote(article).replace("_"," ")
        if "categoria" in registre.keys():
            cat = registre["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/", "")
            cat = urllib.parse.unquote(cat).replace("_"," ")
            if cat not in dicsi.keys():
                print(cat)
                dicsi[cat]=[]
            dicsi[cat].append(article)
        else:
            uni = registre["uni"]["value"]
            if uni in dicno.keys():
                dicno[uni] = dicno[uni]+1
            else:
                dicno[uni] = 1
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\estuni.pkl"
        pickle.dump((dicsi,dicno), open(fitxer, "wb")) 
    return(dicsi, dicno)

def artcat(catnom, site=pwb.Site('ca')):
    # llista d'articles d'una categoria
    cat = pwb.Category(site,catnom)
    articles = pagegenerators.CategorizedPageGenerator(cat, recurse=5)
    llistart = []
    for art in articles:
        llistart.append(art.title())
    return(llistart)

def artcats(catnoms, desa=True, disc= False, site=pwb.Site('ca')):
    # diccionari amb llistes d'articles d'una llista de categoria
    if disc:
        print("llegint categories del disc")
        dicc=pickle.load(open(r"C:\Users\Pere\Documents\perebot\estcats.pkl", "rb"))
    else:   
        print ("llegint categories")
        dicc = {}
        for cat in catnoms:
            print(cat)
            dicc[cat]=artcat(cat)
        if desa:
            fitxer = r"C:\Users\Pere\Documents\perebot\estcats.pkl"
            pickle.dump(dicc, open(fitxer, "wb")) 
    return(dicc)

def posacat(cat, arts, site=pwb.Site('ca')):
    print(cat)
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
        if re.search("\[\["+cat+"\]\]", textvell):
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
        if textnou != textvell:
            sumari = "Robot posa la [["+cat+"]] a partir de Wikidata"
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
arguments = sys.argv[1:]
if len(arguments)>0:
    if "-disc" in arguments:
        disc=True
        arguments.remove("-disc")
    if "-discvp" in arguments:
        discvp=True
        arguments.remove("-discvp")
    if "-nodesis" in arguments:
        desa=False
        arguments.remove("-nodesis")
    if "-noeditis" in arguments:
        edita=False
        arguments.remove("-noeditis")

estuniwdbrut = carrega_wd(desa=desa, disc=disc)
unisi, unino = classifica(estuniwdbrut, desa=True)
#print(unisi[list(unisi)[1]])
uniwp = artcats(list(unisi), disc=discvp, desa=True)
#print(uniwp[list(uniwp)[1]])
total = 0
tots= set([])
print ("Informació: categories per crear")
tunino = []
for uni in unino.keys():
    if unino[uni]>50:
        print(uni, unino[uni])
        tunino.append((unino[uni],uni.replace("http://www.wikidata.org/entity/Q","")))
tunino = sorted(tunino, reverse=Truegit)
print(tunino)
for tuni in tunino:
    print("* {{Q|"+tuni[1]+"}}", tuni[0]) 
# comptar:
print ("Comptant articles:")
for cat in unisi:
    print(cat)
    posar = set(unisi[cat])-set(uniwp[cat])
    print(len(posar))
    total=total+len(posar)
    #print(posar)
    tots=tots|posar
print("Total:",total)
print("Diferents:", len(tots))
if edita:
    for cat in unisi:
        print(cat)
        posar = set(unisi[cat])-set(uniwp[cat])
        posacat(cat, posar)

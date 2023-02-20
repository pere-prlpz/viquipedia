# Fa una llista d'articles que tenen dins del viquitext la imatge del P18 de Wikidata.
# La sortida va a una pàgina d'usuari.
# Opcionalment, admet com a paràmetre una propietat de Wikidata i aleshores
# busca només entre els articles amb aquella propietat. Si no, busca entre tots
# els que tinguin P18.
# Exemples:
# python imatgesrepe.py
# python imatgesrepe.py P625
# python imatgesrepe.py P21

import pywikibot as pwb
from pywikibot import pagegenerators
from pywikibot.exceptions import IsRedirectPageError
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

def get_articles(prop=""):
    print("Carregant articles i imatges de Wikidata")
    if prop=="":
        clausula="\n"
    else:
        clausula="\n?subjecte wdt:"+prop+" [].\n"
    print(clausula)
    query="""#articles amb foto de la infotaula
    SELECT DISTINCT ?article ?imatge WHERE {
      ?article schema:about ?subjecte;
        schema:isPartOf <https://ca.wikipedia.org/>.
      ?subjecte wdt:P18 ?imatge.""" + clausula + "}"
    print(query)
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    #print(wd)
    return (wd)

# el programa comença aquí
arguments = sys.argv[1:]
if len(arguments)>0:
    if "-infotaula" in arguments: # comprovar que l'article tingui infotaula (no implementat)
        infotaula=True
        arguments.remove("-infotaula")
    propietat = arguments[0]
    explica = " Elements amb {{P|"+propietat+"}} a Wikidata."
    explicatitol = "  amb {{P|"+propietat+"}}" 
else:
    propietat = ""
    explica = ""
    explicatitol = ""
# recollida de dades a Wikidata
site=pwb.Site('ca')
dades = get_articles(prop=propietat)
print(explica)
print(dades[0:5])
# endreça les dades per convertir-les en diccionari
dicc = {}
for el in dades:
    nomart = unquote(el["article"]["value"]).replace("https://ca.wikipedia.org/wiki/","")
    nomimatge = unquote(el["imatge"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/","")
    pag=pwb.Page(site,nomart)
    #print(pag)
    #print(dicc)
    if pag in dicc:
        try:
            #print(pag, dicc[pag])
            dicc[pag].append(nomimatge)
            #print(pag, dicc[pag])
        except AttributeError:
            print("AttributeError:", pag, dicc[pag])
            dicc[pag] = [nomimatge]
    else:
        dicc[pag] = [nomimatge]
#print(dicc)
# busca imatges repetides
print(len(dades),"imatges o articles trobats")
print(len(dicc),"articles trobats")
total=len(dicc)
compta=0
comptatrobo=0
pubcompta=0
pubtrobo=0
resum = ""
paginfo=pwb.Page(pwb.Site('ca'),"Usuari:PereBot/imatges repetides")
resum0 = paginfo.get()
for art in pagegenerators.PreloadingGenerator(dicc.keys()):
    compta=compta+1
    print(compta,"/",total,art,dicc[art])
    try:
        text=art.get()
    except IsRedirectPageError:
        print("Redirecció")
        continue
    except NoPageError:
        print("Pàgina inexistent")
        continue
    if re.search("([Ii]mat?ge|[Ff]oto(grafia)?)2? *=.+",text):
        print("té una imatge local a la infotaula")
        continue
    for nomimatge in dicc[art]:
        if re.search("[:\n]"+re.escape(nomimatge), text):
            comptatrobo = comptatrobo+1
            print("imatge repetida\n********************************")
            nump18 = len(dicc[art])
            if nump18 > 1:
                textdup = f"({nump18} imatges a Wikidata)"
                print (nump18, "imatges a P18")
            else:
                textdup = ""
            nomart = art.title()
            resum = resum + f"# [[{nomart}]], [[:Fitxer:{nomimatge}]] {textdup}\n"
        if (compta - pubcompta >= 20000 or comptatrobo - pubtrobo >= 400) and len(resum)>0:
            resumpub = resum0+"\n\n== Imatges repetides"+explicatitol+" ==\n\n"
            resumpub = resumpub+"\nArticles amb la {{P|18}} fora de la infotaula."+explica+"\n\n"+resum
            resumpub = resumpub+f"Vistos {compta} de {total}.--~~~~"
            nores=paginfo.get()
            paginfo.put(resumpub, "Robot busca articles amb la imatge de la infotaula repetida")
            pubcompta=compta
            pubtrobo=comptatrobo
print(resum)
if len(resum)>0:
    resumpub = resum0+"\n\n== Imatges repetides"+explicatitol+" ==\n\n"
    resumpub = resumpub+"\nArticles amb la {{P|18}} fora de la infotaula."+explica+"\n\n"+resum
    resumpub = resumpub+f"Vistos {compta} de {total}.--~~~~"
    nores=paginfo.get()
    paginfo.put(resumpub, "Robot busca articles amb la imatge de la infotaula repetida")

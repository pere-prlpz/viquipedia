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

def get_articles():
    print("Carregant articles i imatges de Wikidata")
    query="""#articles amb foto de la infotaula
    SELECT DISTINCT ?article ?imatge WHERE {
      ?article schema:about ?animal;
        schema:isPartOf <https://ca.wikipedia.org/>.
      ?animal wdt:P18 ?imatge.
    }"""
    #alternativa menor Q134681
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    #print(wd)
    return (wd)

# el programa comença aquí
site=pwb.Site('ca')
repo = site.data_repository()
dades = get_articles()
print(dades[0:5])
titols = [x["article"]["value"] for x in dades]
print(len(dades),"imatges o articles trobats")
total=len(dades)
compta=0
comptatrobo=0
pubcompta=0
pubtrobo=0
resum = ""
paginfo=pwb.Page(pwb.Site('ca'),"Usuari:PereBot/imatges repetides")
resum0 = paginfo.get()
for el in dades:
    #print(el)
    nomart = unquote(el["article"]["value"]).replace("https://ca.wikipedia.org/wiki/","")
    nomimatge = unquote(el["imatge"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/","")
    compta=compta+1
    pag=pwb.Page(site,nomart)
    print(compta,"/",total,pag,nomimatge)
    try:
        text=pag.get()
    except pwb.IsRedirectPage:
        print("Redirecció")
        continue
    except pwb.NoPage:
        print("Pàgina inexistent")
        continue
    if re.search("[Ii]mat?ge *=.+",text):
        print("té una imatge local a la infotaula")
    elif nomimatge in text:
        comptatrobo = comptatrobo+1
        print("imatge repetida\n********************************")
        nump18 = titols.count(el["article"]["value"])
        if nump18 > 1:
            textdup = f"({nump18} imatges a Wikidata)"
            print (nump18, "imatges a P18")
        else:
            textdup = ""
        resum = resum + f"# [[{nomart}]], [[:Fitxer:{nomimatge}]] {textdup}\n"
    if (compta - pubcompta>1000 or comptatrobo - pubtrobo>20) and len(resum)>0:
        resumpub = resum0+"\n\n== Imatges repetides ==\n\n"
        resumpub = resumpub+"\nArticles amb la {{P|18}} fora de la infotaula\n\n"+resum
        resumpub = resumpub+f"Vistos {compta} de {total}.--~~~~"
        paginfo.put(resumpub, "Robot busca articles amb la imatge de la infotaula repetida")
        pubcompta=compta
        pubtrobo=comptatrobo
print(resum)
if len(resum)>0:
        resumpub = resum0+"\n\n== Imatges repetides ==\n\n"
        resumpub = resumpub+"\nArticles amb la {{P|18}} fora de la infotaula\n\n"+resum
        resumpub = resumpub+f"Vistos {compta} de {total}.--~~~~"    
        paginfo.put(resumpub, "Robot busca articles amb la imatge de la infotaula repetida")
    

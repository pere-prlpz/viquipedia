# el programa comença aquí

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

def get_catmorts():
    print("Carregant categories per any de la mort de Wikidata")
    query="""# Categories de morts per any no a cawiki
    SELECT DISTINCT ?cat ?any ?anyLabel 
    WITH {
      SELECT ?cat WHERE {
        ?cat wdt:P31 wd:Q4167836.
        ?cat wdt:P971 wd:Q21160456.
        ?cat wdt:P4224 wd:Q5.
      }
    }  AS %1
    WHERE {
      INCLUDE %1
      VALUES ?tipusany {wd:Q577 wd:Q3186692}
        ?any wdt:P31 ?tipusany.
        ?cat wdt:P971 ?any.
        MINUS {
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
        }
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ca,en,es" . } 
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def get_catnascuts():
    print("Carregant categories per any de naixement de Wikidata")
    query="""# Categories de nascuts per any no a cawiki
    SELECT DISTINCT ?cat ?any ?anyLabel 
    WITH {
      SELECT ?cat WHERE {
        ?cat wdt:P31 wd:Q4167836.
        ?cat wdt:P971 wd:Q21821348.
        ?cat wdt:P4224 wd:Q5.
      }
    }  AS %1
    WHERE {
      INCLUDE %1
      VALUES ?tipusany {wd:Q577 wd:Q3186692}
        ?any wdt:P31 ?tipusany.
        ?cat wdt:P971 ?any.
        MINUS {
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
        }
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ca,en,es" . } 
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def segle(nany):
    s = int((abs(nany)-1)/100)
    numsrom = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII"]
    seg = numsrom[s]
    if nany < 0:
        seg = seg+" aC"
    return (seg)

def catmortany(nany):
    nom = "Morts el "+str(nany)
    seg = segle(nany)
    descr = "'''[[:Categoria:Morts el "+str(nany)+"]]'''\n\n"
    catwikitext = """{{Commonscat}}
{{TOC Meta Dècada| categoria=Morts el| any="""+str(nany)+"""}}

[[Categoria:Biografies per data de defunció|"""+str(nany)+"""]]
[[Categoria:Biografies del segle """+seg+"""]]"""
    return(nom, descr, catwikitext, seg)

def catnascutany(nany):
    nom = "Naixements del "+str(nany)
    seg = segle(nany)
    descr = "'''[[:Categoria:Naixements del "+str(nany)+"]]'''\n\n"
    unitat = nany % 10
    desenes = int((nany-unitat)/10)
    catwikitext = """{{NascutsAnyCat|"""+str(desenes)+"""|"""+str(unitat)+"""}}
{{commonscat-inline}}
{{Consultes per gènere}}

[[Categoria:Biografies per data de naixement]]
[[Categoria:Biografies del segle """+seg+"""]]"""
    return(nom, descr, catwikitext, seg)

def link_creacat(catpral, contingut=""):
    link = "https://ca.wikipedia.org/wiki/Categoria:"
    link = link + urllib.parse.quote(catpral)
    link = link + "?action=edit&section=new&nosummary=true&preload=User:PereBot/categories/plantilla_blanc&preloadparams%5b%5d="
    link = link + urllib.parse.quote_plus(contingut)
    return(link)


# el programa comença aquí
# Nascuts
catnascuts = get_catnascuts()
#print(catmorts)
dicanys = {}
seg0 = "0"
for item in catnascuts:
    print(item)
    try:
        nany = int(item["anyLabel"]["value"])
    except ValueError:
        print("L'any no és un número", item["anyLabel"]["value"])
        continue
    print(nany)
    qcat = re.sub("http://www.wikidata.org/entity/", "", item["cat"]["value"])
    print(qcat)
    dicanys[nany]=qcat
#print(dicanys)
informe = "== Categories per any de naixement ==\n\n"
for nany in sorted(list(dicanys.keys())):
    print(nany, segle(nany))
    (nomcat, infcat, contcat, seg) = catnascutany(nany)
    if seg != seg0:
        informe = informe + "=== Segle "+seg+" ===\n\n"
        seg0=seg
    #print(nomcat, infcat, contcat)
    informe = informe + infcat
    quick = dicanys[nany]+'|Scawiki|"Categoria:'+nomcat+'"||'
    informe = informe + "* ["+link_creacat(nomcat, contcat) + " Crea categoria]\n\n"
    informe = informe + "* [https://quickstatements.toolforge.org/#/v1=" + urllib.parse.quote(quick)+" Afegeix categoria a Wikidata amb Quickstatements]\n\n"
# Morts
catmorts = get_catmorts()
#print(catmorts)
dicanys = {}
seg0 = "0"
for item in catmorts:
    print(item)
    try:
        nany = int(item["anyLabel"]["value"])
    except ValueError:
        print("L'any no és un número", item["anyLabel"]["value"])
        continue
    print(nany)
    qcat = re.sub("http://www.wikidata.org/entity/", "", item["cat"]["value"])
    print(qcat)
    dicanys[nany]=qcat
#print(dicanys)
informe = informe+"\n== Categories per any de la mort ==\n\n"
for nany in sorted(list(dicanys.keys())):
    print(nany, segle(nany))
    (nomcat, infcat, contcat, seg) = catmortany(nany)
    if seg != seg0:
        informe = informe + "=== Segle "+seg+" ===\n\n"
        seg0=seg
    #print(nomcat, infcat, contcat)
    informe = informe + infcat
    quick = dicanys[nany]+'|Scawiki|"Categoria:'+nomcat+'"||'
    informe = informe + "* ["+link_creacat(nomcat, contcat) + " Crea categoria]\n\n"
    informe = informe + "* [https://quickstatements.toolforge.org/#/v1=" + urllib.parse.quote(quick)+" Afegeix categoria a Wikidata amb Quickstatements]\n\n"
#print (informe)
site=pwb.Site('ca')
paginforme = pwb.Page(site, "Usuari:PereBot/categories per naixement i mort")
sumari = "Robot ajudant a crear categories"
paginforme.put(informe+"\n\n--~~~~\n", sumari)

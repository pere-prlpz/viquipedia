#-*- coding: utf-8 -*-
#
# Script per crear llistes de topònims de municipis del Rosselló i el Conflent
# instruccions:
# python crea_llista_topo.py Nom de la comuna
# modificadors:
# -prova Crea la llista en una pàgina de proves (valor per defecte)
# -noprova Crea la llista a l'espai principal

import pywikibot as pwb
from pywikibot import pagegenerators
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import math
import re
import pickle
import sys
import urllib
import time
from urllib.parse import unquote

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_comunes(mostra=False):
    query ="""# Comunes dels Pirineus Orientals sense data de finalització (o sigui, excloent les antigues comunes); amb comarca
SELECT ?item ?itemLabel ?comarca ?comarcaLabel ?lat ?lon WHERE {
  ?item p:P31 ?s31.
  ?s31 ps:P31 wd:Q484170.
  MINUS {?s31 pq:P582 []}
  ?item wdt:P131* wd:Q12709.
  OPTIONAL {
    ?comarca wdt:P31 wd:Q3573632.
    ?comarca wdt:P150 ?item.
  }
  ?item p:P625 ?coordinate .
  ?coordinate psv:P625 ?coordinate_node .
  ?coordinate_node wikibase:geoLatitude ?lat .
  ?coordinate_node wikibase:geoLongitude ?lon .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ca". }
}
ORDER by ?itemLabel
    """
    if mostra: print(query)
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    mons={}
    for mon in results["results"]["bindings"]:
        if "item" in mon.keys():
            qitem=mon["item"]["value"].replace("http://www.wikidata.org/entity/","")
            mons[qitem]=mon
    return(mons)

def troba_comunes():
    try:
        with open('C:/Users/Pere/Documents/perebot/comunes.pickle', 'rb') as f:
            comunes=pickle.load(f)
            print("Comunes llegides del disc")
            return (comunes)
    except FileNotFoundError:
        comunes = get_comunes()
        with open('C:/Users/Pere/Documents/perebot/comunes.pickle', 'wb') as f:
            print("Sense fitxer de comunes. Llegint una query.")
            pickle.dump(comunes, f)
        return(comunes)

def treu_dades_comuna(nom, comunes):
    for kcom in comunes:
        com = comunes[kcom]
        if com["itemLabel"]["value"].lower()==nom.lower():
            qid = kcom
            lat = com["lat"]["value"]
            lon = com["lon"]["value"]
            comarca = com["comarcaLabel"]["value"]
            dades = dict(nom=nom, qid=qid, comarca=comarca, lat=lat, lon=lon)
            return(dades)
    return([])
   
def de(nom, enllac=True):
    if re.match("^[AEIOUÀÈÉÍÒÓÚaeiouàèéíòóú]",nom):
        res = "d'"+nom
    else:
        res = "de "+nom
    res = re.sub("d'[Ee]l ", "del ", res)
    res = re.sub("d'[Ee]ls ", "dels ", res)
    if enllac:
        res = re.sub(nom, "[["+nom+"]]", res)
    return(res)

def caixa_wikishootme(dadesmun):
    adreca = "https://wikishootme.toolforge.org/#lat="+dadesmun["lat"]+"&lng="+dadesmun["lon"]+"&zoom=14&sparql_filter=%3Fq%20wdt%3AP131%2B%20wd%3A"+dadesmun["qid"]+".&worldwide=1"
    caixa = "{{caixa lateral|text='''Mapa amb tots els punts'''<br/>["+adreca+" "+dadesmun["nom"]+"]}}"
    return(caixa)

# el programa comença aquí
comunes = troba_comunes()
print(len(comunes), "comunes trobades")
arguments = sys.argv[1:]
prova = True
if len(arguments)>0:
    if "-prova" in arguments:
        prova=True
        arguments.remove("-prova")
    if "-noprova" in arguments:
        prova=False
        arguments.remove("-noprova")
if len(arguments)>0:
    nomcomuna=" ".join(arguments)
else:
    print("Manca el nom de la comuna. Agafem opció per defecte (per proves).")
    prova=True
    nomcomuna="Argelers"
dades_comuna = treu_dades_comuna(nomcomuna, comunes)
print(dades_comuna)
nomllista = "Llista de topònims "+de(nomcomuna, enllac=False)
print (nomllista)    
intro = "'''Llista de topònims (noms propis de lloc) "+de(nomcomuna)+" ([["+dades_comuna["comarca"]+"]]).'''"
print(intro)
caixa = caixa_wikishootme(dades_comuna)
#print(caixa)
conssi = """  {
  ?item wdt:P17 wd:Q142.
  ?item wdt:P131+ wd:"""+dades_comuna["qid"]+""".
  }
  UNION
  {wd:"""+dades_comuna["qid"]+""" wdt:P206 ?item}
"""
#print(conssi)
consminus = """  MINUS { ?item wdt:P31/wdt:P279* wd:Q7075.
         MINUS {?item wdt:P149 []}
        }
  MINUS { ?item wdt:P31/wdt:P279* wd:Q5341295.
         MINUS {?item wdt:P31/wdt:P279* wd:Q811979}
        } 
  MINUS { ?item wdt:P31 wd:Q1076486.
         MINUS {?item wdt:P31 wd:Q182676} 
         MINUS {?item wdt:P31 wd:Q1193438.}
         MINUS {?item wdt:P31 wd:Q483110.}
         MINUS {?item wdt:P31/wd:P279* wd:Q44782.}
         MINUS {?item wdt:P912 wd:Q721207}
         MINUS {?item wdt:P31/wd:P279* wd:Q20719696.}        
         MINUS {?item wdt:P31 wd:Q22746.}
        }
   MINUS { ?item wdt:P31 wd:Q27686. }
   MINUS { ?item wdt:P31 wd:Q11919491. }
   MINUS { ?item wdt:P31/wdt:P279* wd:Q847017. }
   MINUS { ?item wdt:P31 wd:Q11919687. }
   MINUS { ?item wdt:P31 wd:Q33506. }
   MINUS { ?item wdt:P361?/wdt:P1435 wd:Q61058403. }
   MINUS { ?item wdt:P1435 wd:Q61058419.}   
   MINUS { ?item wdt:P31 wd:Q30114662.}
   MINUS { ?item wdt:P31 wd:Q20860083.}
   MINUS { ?item wdt:P31 wd:Q119739087.}
   MINUS { ?item wdt:P31 wd:Q83554028.}
   MINUS { ?item wdt:P366 wd:Q569500.}
   MINUS { ?item wdt:P366 wd:Q124727760.}
   MINUS { ?item wdt:P31 wd:Q3578324.}
   MINUS { ?item wdt:P31 wd:Q41253.}
   MINUS { ?item wdt:P31 wd:Q179700.
           ?item wdt:P186 wd:Q287.
           MINUS {?item wdt:P625 [].}
          }
   MINUS { ?item wdt:P31 wd:Q187456.}
   MINUS { ?item wdt:P31 wd:Q15275719.}
   MINUS { ?item wdt:P31 wd:Q14645593.}
   MINUS { ?item wdt:P31 wd:Q43229.}
   MINUS { ?item wdt:P31 wd:Q18127.}
   MINUS { ?item wdt:P31 wd:Q131734.}
   MINUS { ?item wdt:P31 wd:Q1774898.}
   MINUS { ?item wdt:P31 wd:Q321839.}
   MINUS { ?item wdt:P31 wd:Q4618.}
   MINUS { ?item wdt:P31 wd:Q200538.}
   MINUS { ?item wdt:P31 wd:Q27968055.}
   MINUS { ?item wdt:P31 wd:Q169950.}
   MINUS { ?item wdt:P31 wd:Q1078765.}
   MINUS { ?item wdt:P31 wd:Q51785152.}
   MINUS { ?item wdt:P31 wd:Q483242.}
   MINUS { ?item wdt:P31 wd:Q30014735.}
   MINUS { ?item wdt:P31 wd:Q7309759.}
   MINUS { ?item wdt:P31/wdt:P279* wd:Q43501.}
   MINUS { ?item wdt:P31/wdt:P279* wd:Q625994.}
   MINUS { ?item wdt:P31 wd:Q98838181.}
   MINUS { ?item wdt:P31/wdt:P279* wd:Q4260475.}
   MINUS { ?item wdt:P31 wd:Q13226383.
           ?item wdt:P366 wd:Q2945655}   
"""
consunitats = """        OPTIONAL {?item p:P2043/psv:P2043/wikibase:quantityUnit/wdt:P5061 ?allarg.
                           FILTER(LANG(?allarg) = "ca").}
        OPTIONAL { ?item p:P2787/psv:P2787/wikibase:quantityUnit/wdt:P5061 ?allum.
                           FILTER(LANG(?allum) = "ca").}
        OPTIONAL {?item p:P2049/psv:P2049/wikibase:quantityUnit/wdt:P5061 ?aample.
                FILTER(LANG(?aample) = "ca").}
        OPTIONAL {?item p:P2048/psv:P2048/wikibase:quantityUnit/wdt:P5061 ?aalt.
                           FILTER(LANG(?aalt) = "ca").}
        OPTIONAL {?item p:P4511/psv:P4511/wikibase:quantityUnit/wdt:P5061 ?aprof.
                           FILTER(LANG(?aprof) = "ca").}
        OPTIONAL {?item p:P2547/psv:P2547/wikibase:quantityUnit/wdt:P5061 ?aperim.
                           FILTER(LANG(?aperim) = "ca").}
        OPTIONAL {?item p:P2046/psv:P2046/wikibase:quantityUnit/wdt:P5061 ?asuperf.
                           FILTER(LANG(?asuperf) = "ca").}
        OPTIONAL {?item p:P2234/psv:P2234/wikibase:quantityUnit/wdt:P5061 ?avolum.
                           FILTER(LANG(?avolum) = "ca").}
        OPTIONAL {?item wdt:P10241/wdt:P225 ?nomcient}
"""
indexcat = re.sub("^(el |la |els |les |l')", "", nomcomuna)
categoriescom = dict(Rosselló="Llistes auto-generades de topònims del Rosselló", 
    Conflent="Llistes auto-generades de topònims del Conflent")
categories = "[[Categoria:"+nomcomuna+"]]\n[[Categoria:"+categoriescom[dades_comuna["comarca"]]+"|"+indexcat+"]]"
#print(categories)
contingut = caixa+"\n\n"+intro+"""\n
{{Wikidata list
| sparql =  SELECT * WHERE {   
"""+conssi+"\n"+consminus+"\n"+consunitats+"""}
| columns = label,item,p18,p131,p31,p366,p84,p170,p149,p135,p571,p177,p2505,p403,p10241,?nomcient,p5816,p1082,p2043,p2787,p2049,p2048,p2547,p2046,p2234,p138,p825,p547,p4511,p625,p2795,p6375,p669,p669/p670,p276,p706,p2044,p1435,p373,?allarg:Ullarg,?allum:Ullum,?aample:Uample,?aalt:Ualt,?aprof:Uprof,?aperim:Uperim,?asuperf:Usuperf,?avolum:Uvolum| sort=label
| section = P31
| links = text
| thumb = 128
| freq = 30
| header_template = Wikidata list/headerrow/topònim
| row_template = Wikidata list/topònim
}}
{{Wikidata list end}}
\n
"""+categories
#print(contingut)
if prova:
    nomdesti="Usuari:PereBot/taller"
    contingut = contingut.replace("[[Categoria:", "[[:Categoria:")
    nomdisc = nomdesti.replace("Usuari:","Usuari Discussió:")
else:
    nomdesti=nomllista
    nomdisc="Discussió:"+nomdesti
site=pwb.Site('ca')
pag=pwb.Page(site, nomdesti)
pag.put(contingut, "Bot creant llista de topònims")
contingut_disc="""== Coses excloses de la llista ==

{{SPARQL|query=# Coses excloses de la llista
SELECT DISTINCT ?item ?itemLabel ?inst ?instLabel WHERE {   
\n"""+conssi+"""  OPTIONAL {?item wdt:P31 ?inst.}
  MINUS {?item wdt:P31 []. 
  # Aquí comencen els MINUS de la llista       
\n"""+consminus+"""   # fins aquí els MINUS de la llista
        }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ca,fr,en". }
}
}}\n\n--~~~~"""
pagdisc=pwb.Page(site, nomdisc)
if pagdisc.exists():
    disc0 = pagdisc.get()+"\n\n"
else:
    disc0=""
pagdisc.put(disc0+contingut_disc, "Robot posant consulta auxiliar per llista de topònims")

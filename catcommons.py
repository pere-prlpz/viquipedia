#-*- coding: utf-8 -*-
#
# Script per ajudar a crear categories d'edificis a Commons

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
import urllib.parse

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

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_dicc(query, treurl=True, mostra=False, primer=False):
    if mostra: print(query)
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    mons={}
    for mon in results["results"]["bindings"]:
        if "item" in mon.keys():
            qitem=mon["item"]["value"].replace("http://www.wikidata.org/entity/","")
            if primer == True and qitem in mons.keys():
                continue
            if treurl:
                monnet = {}
                for camp in mon:
                    campnou = mon[camp]
                    if campnou["type"]=="uri":
                        campnou["value"] = campnou["value"].replace("http://www.wikidata.org/entity/","")
                    monnet[camp]=campnou                
                mons[qitem]=monnet
            else:
                mons[qitem]=mon
    return(mons)

def get_edificis(mostra=False, nofoto=False):
    query0="""# elements amb identificador, amb foto sense commonscat (Catalunya)
SELECT DISTINCT ?item ?itemLabel ?itemLabelen ?div ?divLabel ?barri ?distr ?distrLabel ?mun ?munLabel ?ipac ?idbcn WHERE {
{{?item wdt:P11557 [].}
UNION
{?item wdt:P12802[].}}
UNION
{{?item wdt:P1600 [].}
UNION
{?item wdt:P12860 [].}}  
  ?item wdt:P18 [].
  OPTIONAL {
    ?item wdt:P131+ ?barri.
    ?barri wdt:P31 wd:Q75135432 
  }
  OPTIONAL {
    ?item wdt:P131+ ?distr.
    ?distr wdt:P31 wd:Q790344 
  }
  OPTIONAL {
    ?item wdt:P131+ ?mun.
    ?mun wdt:P31 wd:Q33146843 
  }
  OPTIONAL {?item wdt:P11557 ?idbcn}
  OPTIONAL {?item wdt:P1600 ?ipac}
  BIND(COALESCE(?barri, ?distr, ?mun) as ?div)
  MINUS {?item wdt:P373 []}
  MINUS {?item wdt:P910 []}
  MINUS {
    ?commonslink schema:isPartOf <https://commons.wikimedia.org/>.
    ?commonslink schema:about ?item.
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ca" }  
  SERVICE wikibase:label {
   bd:serviceParam wikibase:language "en".
   ?item rdfs:label ?itemLabelen.
  }
}
ORDER BY ?munLabel ?distrLabel ?divLabel ?itemLabel ?item"""
    if nofoto:
        query0 = query0.replace("?item wdt:P18 [].", "MINUS {?item wdt:P18 [].}")
        query0 = query0.replace("""{{?item wdt:P1600 [].}
UNION
""", "{")
    mons = get_dicc(query=query0, mostra=mostra, primer=True)
    return(mons)
    
# torna la categoria d'edificis en funció de tota l'entrada de la consulta
def cat_edifici(dicc):
    llocs_edif = {"Q3321657":"Sant Gervasi-la Bonanova",
                  "Q3321805":"el Putget i Farró",
                  "Q1404773":"Poblenou",
                  "Q980253":"Poble-sec (Sants-Montjuïc)",
                  "Q3296693":"Les Corts neighbourhood",
                  "Q3291762":"Esquerra de l'Eixample",
                  "Q1026658":"Esquerra de l'Eixample",
                  "Q17154":"El Gòtic (Barcelona)",
                  "Q1758503":"El Raval",
                  "Q16722":"Mura (Spain)"}
    if not "div" in dicc:
        return ("Buildings in Catalonia")
    qlloc = dicc["div"]["value"]
    if qlloc in llocs_edif:
        lloc = llocs_edif[qlloc]
    else:
        lloc = dicc["divLabel"]["value"].replace(" - ", "-")
        if "barri" not in dicc:
            #lloc = lloc[0].upper()+lloc[1:]
            pass
    cat = "Buildings in "+ lloc
    return(cat)

# torna la categoria de monuments en funció de tota l'entrada de la consulta
def cat_monument(dicc):
    if "ipac" in dicc or "idbcn" in dicc:
        llocs_mon = {"Q16722":"Mura (Spain)",
                     "Q941385":"Ciutat Vella, Barcelona",
                     "Q15470":"L'Hospitalet de Llobregat",
                     "Q17154":"El Gòtic, Barcelona"}
        distr_sempre = {"Q1765582":"Sarrià-Sant Gervasi",
                        "Q852697":"Gràcia District",
                        "Q250935":"Sant Martí District",
                        "Q1650230":"Sant Andreu District",
                        "Q959944":"Les Corts District",
                        "Q64124":"Eixample, Barcelona"} # districtes amb categoria de monuments irregular
        distr_a_barri = ["Q941385"] # districtes on els monuments van per barris
        if not "div" in dicc:
            return ("Cultural heritage monuments in Catalonia")
        qlloc = dicc["div"]["value"]
        if qlloc in llocs_mon:
            llocmon = llocs_mon[qlloc]
        elif "distr" in dicc and dicc["distr"]["value"] in distr_sempre:
            llocmon = distr_sempre[dicc["distr"]["value"]]
        elif "distr" in dicc and dicc["distr"]["value"] in distr_a_barri and "barri" in dicc:
            llocmon = dicc["divLabel"]["value"].replace(" - ", "-")
        elif "distr" in dicc:
            llocmon = dicc["distrLabel"]["value"].replace(" - ", "-")
        else:
            llocmon = dicc["divLabel"]["value"]
            #llocmon = llocmon[0].upper()+llocmon[1:]
        cat = "Cultural heritage monuments in "+llocmon
    else:
        cat = False
    return(cat)

def nom_commons(dicc):
    nomen = dicc["itemLabelen"]["value"]
    if re.match("^[Bb]uilding in ", nomen):
        nc = nomen
        if re.match("^[Bb]uilding in (carrer del Rec|[Rr]ambla del Poblenou),", nomen): # ampliar amb els carrers que s'hagin de deixar
            nc = re.sub("^[Bb]uilding in ", "", nc)
        nc = re.sub("^[Bb]uildings? in carrer (del |de (l'|la ))", "", nc)
        nc = re.sub("^[Bb]uildings? in carrer (de |d')", "", nc)
        nc = re.sub("^[Bb]uildings? in carrer ", "", nc)
        nc = re.sub("^[Bb]uildings? in ", "", nc)
        if nomen != nc:
            return(nc)
    nc = dicc["itemLabel"]["value"]
    nc = re.sub("^([Cc]asa|[Ee]difici|[Hh]abitatges?)( (d'habitatges|[Uu]nifamiliars?|[Pp]lurifamiliars?|d'oficines))? (al|del) carrer (del? |d')?", "", nc)
    nc = re.sub("^([Cc]asa|[Ee]difici|[Hh]abitatges?)( (d'habitatges|[Uu]nifamiliars?|[Pp]lurifamiliars?|d'oficines))? (a|de) l'[Aa]vinguda (del? |d')?", "Avinguda ", nc)
    nc = re.sub("^([Cc]asa|[Ee]difici|[Hh]abitatges?)( (d'habitatges|[Uu]nifamiliars?|[Pp]lurifamiliars?|d'oficines))? (a|de) la [Pp]laça (del? |d')?", "Plaça ", nc)
    nc = re.sub("^([Cc]asa|[Ee]difici|[Hh]abitatges?)( (d'habitatges|[Uu]nifamiliars?|[Pp]lurifamiliars?|d'oficines))? (a|de) la [Rr]ambla (del? |d')?", "Rambla ", nc)
    nc = re.sub("^([Ee]scultura) ", "", nc)
    return(nc)

def cat_tipus(dicc):
    nom = dicc["itemLabel"]["value"]
    if not "munLabel" in dicc:
        return False
    mun = dicc["munLabel"]["value"]
    if re.match("^([Cc]as(a|es)|[Hh]abitatges?|[Vv]il·?la) ", nom):
        ct = "Houses in "+mun
        return(ct)
    if re.match("^([Pp]alau) ", nom):
        ct = "Palaces in "+mun
        return(ct)
    if re.match("^([Ee]s(cultur|tatu)(a|es)) ", nom):
        ct = "Sculptures in "+mun
        return(ct)
    if re.match("^([Rr]ellotge de [Ss]ol) ", nom):
        ct = "Sundials in "+mun
        return(ct)
    else:
        return(False)

def link_creacat(catpral, nom="", categories=[]):
    cats = ["[[Category:"+x+"]]" for x in categories if x]
    #print(cats)
    scats = "\n".join(cats)
    link = "https://commons.wikimedia.org/wiki/Category:"
    link = link + urllib.parse.quote(catpral)
    link = link + "?action=edit&section=new&nosummary=true&preload=User:PereBot/categories/plantilla&preloadparams%5b%5d="
    link = link + urllib.parse.quote_plus(nom)
    link = link + "&preloadparams%5b%5d="
    link = link + urllib.parse.quote_plus(scats)
    return(link)

# el programa comença aquí
arguments = sys.argv[1:]
nofoto=False
if len(arguments)>0:
    if "-nofoto" in arguments:
        nofoto=True
        arguments.remove("-nofoto")
    lloc=" ".join(arguments)
else:
    print("Manca el nom del lloc. Agafem opció per defecte")
    lloc="tot" #"prova"
edificis = get_edificis(mostra=True, nofoto=nofoto)
print(len(edificis))
#print(edificis)
#objectiu = [x for x in edificis.keys() if edificis[x]["divLabel"]["value"]=="Sant Gervasi-Galvany"]
if lloc == "tot":
    objectiu = edificis.keys()
    paginf = 'User:PereBot/categories'    
elif lloc == "prova":
    objectiu = [x for x in edificis.keys() if "distrLabel" in edificis[x].keys() and edificis[x]["distrLabel"]["value"]=="Sarrià - Sant Gervasi"]
    paginf = 'User:PereBot/categories'
else:
    objectiu = [x for x in edificis.keys() if lloc.casefold() in [edificis[x].get("divLabel",{"value":"ZZZ"})["value"].casefold(), 
                                                                  edificis[x].get("barriLabel",{"value":"ZZZ"})["value"].casefold(), 
                                                                  edificis[x].get("distrLabel",{"value":"ZZZ"})["value"].casefold(), 
                                                                  edificis[x].get("munLabel",{"value":"ZZZ"})["value"].casefold()]]
    paginf = 'User:PereBot/categories/'+lloc
#print(objectiu)
if nofoto:
    paginf = paginf+"/sense P18"
print(paginf)
informe = "{{User:PereBot/categories/introducció}}\n\n"
div0 = ""
for qid in objectiu:
    #print(edificis[qid])
    #print(qid)
    #print(edificis[qid]["itemLabel"]["value"])
    #print(cat_edifici(edificis[qid]))
    #print(cat_monument(edificis[qid]))
    nomcat =  edificis[qid]["itemLabel"]["value"]
    nomcommons = nom_commons(edificis[qid])
    cedif = cat_edifici(edificis[qid])
    cmonum = cat_monument(edificis[qid])
    ctipus = cat_tipus(edificis[qid])
    if "divLabel" in edificis[qid]:
        div1 = edificis[qid]["divLabel"]["value"]
    else:
        div1 = ""
    if div1 != div0:
        div0=div1
        inf_cat="== "+div1+"==\n\n"
    else:
        inf_cat=""
    inf_cat = inf_cat + "=== "+nomcat+"===\n\n"
    inf_cat = inf_cat + "{{Q|"+qid+"}}\n\n"
    inf_cat = inf_cat + "Proposat: '''[[:Category:"+nomcommons+"]]'''\n\n"
    inf_cat = inf_cat + "Categories: [[:Category:"+cedif+"]]"
    if cmonum != False:
        inf_cat = inf_cat+" [[:Category:"+cmonum+"]]"
    if ctipus != False:
        inf_cat = inf_cat+" [[:Category:"+ctipus+"]]"
    inf_cat=inf_cat+"\n<pre><nowiki>{{Wikidata infobox}}\n{{ca|"+nomcat+"}}\n\n"
    inf_cat=inf_cat+"[[Category:"+cedif+"]]\n"
    if cmonum != False:
        inf_cat = inf_cat+"[[Category:"+cmonum+"]]\n"
    if ctipus != False:
        inf_cat = inf_cat+"[[Category:"+ctipus+"]]\n"
    inf_cat=inf_cat+"</nowiki></pre>\n\n"
    inf_cat=inf_cat+"* ["+link_creacat(nomcommons, nomcat, [cedif, cmonum, ctipus])+" Crea categoria]\n\n"
    quick = qid+'|Scommonswiki|"Category:'+nomcommons+'"||'+qid+'|P373|"'+nomcommons+'"||'
    #inf_cat=inf_cat+quick+'"\n\n'
    inf_cat = inf_cat + "* [https://quickstatements.toolforge.org/#/v1=" + urllib.parse.quote(quick)+" Afegeix categoria a Wikidata amb Quickstatements]\n\n"
    inf_cat = inf_cat + "* Cerca imatges [[Special:Search/haswbstatement:P180="+qid+"|amb Special:Search]] o "
    inf_cat = inf_cat + "[https://commons.wikimedia.org/w/index.php?search=depicts%3A"+qid+"&title=Special:MediaSearch&go=V%C3%A9s&type=image amb Special:MediaSearch]\n\n"
    #print(inf_cat)
    informe=informe+inf_cat
informe = informe + "Total elements: " + str(len(objectiu)) + "\n\n"
informe = informe +"\n--~~~~\n\n"
#print (informe)
site=pwb.Site('commons')
paginforme = pwb.Page(site, paginf)
paginforme.put(informe, "Robot preparant categories per carregar ("+ str(len(objectiu))+")")

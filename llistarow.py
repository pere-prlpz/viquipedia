#-*- coding: utf-8 -*-
#
# Script per actualitzar les llistes de topònims al format amb rowtemplate

import sys
import re
import pywikibot as pwb
from pywikibot import pagegenerators
import mwparserfromhell

def arreglaplantilla(plantilla, nocoord=False):
    consulta = plantilla.get("sparql").value
    #print (consulta)
    unitats = """        OPTIONAL {?item p:P2043/psv:P2043/wikibase:quantityUnit/wdt:P5061 ?allarg.
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
        OPTIONAL {?item p:P2053/psv:P2053/wikibase:quantityUnit/wdt:P5061 ?asuperfc.
                           FILTER(LANG(?asuperfc) = "ca").}
        OPTIONAL {?item wdt:P10241/wdt:P225 ?nomcient}
}
"""
    nomcient = """        OPTIONAL {?item wdt:P10241/wdt:P225 ?nomcient}
}
"""
    if ("OPTIONAL" in consulta):
        print("ja té les opcions")
        if ("wdt:P10241/wdt:P225" in consulta):
            print("també té el nom científic")
        else:
            consulta = re.sub("}.*$", nomcient, str(consulta.strip()))
            plantilla.add("sparql", consulta)
    else:
        consulta = re.sub("}.*$", unitats, str(consulta.strip()))
        plantilla.add("sparql", consulta)
        print("Afegides unitats")
    columnes = "label,item,p18,p131,p31,p366,p84,p170,p149,p135,p571,p177,p2505,p403,p10241,?nomcient,p5816,p1082,p2043,p2787,p2049,p2048,p2547,p2046,p2234,p2053,p138,p825,p547,p4511,p625,p2795,p6375,p669,p669/p670,p276,p706,p2044,p1435,p373,?allarg:Ullarg,?allum:Ullum,?aample:Uample,?aalt:Ualt,?aprof:Uprof,?aperim:Uperim,?asuperf:Usuperf,?avolum:Uvolum,?asuperfc:Usuperfc"
    if nocoord:
        columnes = columnes.replace("p625,","")
    plantilla.add("columns", columnes)
    plantilla.add("header_template", "Wikidata list/headerrow/topònim")
    plantilla.add("row_template","Wikidata list/topònim")
    plantilla.add("thumb", "128")
    return (plantilla)

def rowllista(llista):
    print(llista)
    text = llista.get()
    numfiles = text.count("Wikidata list/topònim")
    print(numfiles, "topònims")
    gran = (numfiles>800)
    if gran:
        print("Llistra gran. Prescindim de les coordenades.")
    treure = """   BIND (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "", "i") as ?itemId).
   BIND (CONCAT ("[","[","Fitxer:Arbcom ru editing.svg|12px|center|",  
              "Modifica les dades a Wikidata|", 
              "link", "=","d:",STR(?itemId), "]","]")  as ?llapis)
"""
    text = text.replace(treure, "")
    treure2 = """ BIND (REPLACE(STR(?item), "http://www.wikidata.org/entity/", "", "i") as ?itemId).
 BIND (CONCAT ("[","[","Fitxer:Arbcom ru editing.svg|12px|center|", 
              "Modifica les dades a Wikidata|", 
              "link", "=","d:",STR(?itemId), "]","]") as ?llapis)
"""
    text = text.replace(treure2, "")
    wikicode = mwparserfromhell.parse(text)
    #print(wikicode)
    templates = wikicode.filter_templates()
    for template in templates:
      if template.name.matches("wikidata list"):
        #print(template)
        template = arreglaplantilla(template, nocoord=gran)
        #print (template)
    textnou = str(wikicode)
    if text==textnou:
        print("cap canvi")
    else:
        llista.put(str(wikicode), summary="robot adapta la llista al format amb rowtemplate")

def rowllistes(nomorigen):
    if re.match("llistes", nomorigen.casefold()):
        cat = pwb.Category(site,'Category:'+nomorigen)
        print(cat)
        llistes = pagegenerators.CategorizedPageGenerator(cat, recurse=True)
    else:
        llistes = [pwb.Page(site, nomorigen)]
    for llista in llistes:
        rowllista(llista)


# el programa comença aquí
arguments = sys.argv[1:]
if len(arguments)>0:
    nomllista=" ".join(arguments)
else:
    print("Manca el nom de la llista de topònims. Agafem opció per defecte")
    nomllista="Usuari:PereBot/taller"
site=pwb.Site('ca')
print (nomllista)
rowllistes(nomllista) 

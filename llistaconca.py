#-*- coding: utf-8 -*-
#
# Script per actualitzar les llistes de topònims amb la superfície de la conca

import sys
import re
import pywikibot as pwb
from pywikibot import pagegenerators
import mwparserfromhell

def arreglaplantilla(plantilla):
    consulta = plantilla.get("sparql").value
    #print (consulta)
    vellconsulta = """FILTER(LANG(?avolum) = "ca").}
        OPTIONAL {?item wdt:P10241/wdt:P225 ?nomcient}"""
    vellconsulta2 = """FILTER(LANG(?avolum) = "ca").
              }

        OPTIONAL {?item wdt:P10241/wdt:P225 ?nomcient}"""
    nouconsulta = """FILTER(LANG(?avolum) = "ca").}
        OPTIONAL {?item p:P2053/psv:P2053/wikibase:quantityUnit/wdt:P5061 ?asuperfc.
                           FILTER(LANG(?asuperfc) = "ca").}
        OPTIONAL {?item wdt:P10241/wdt:P225 ?nomcient}"""
    if vellconsulta in consulta:
        print("trobat on modificar la consulta")
        consulta = str(consulta.strip()).replace(vellconsulta, nouconsulta)
        plantilla.add("sparql", consulta)
    elif vellconsulta2 in consulta:
        print("trobat on modificar la consulta")
        consulta = str(consulta.strip()).replace(vellconsulta2, nouconsulta)
        plantilla.add("sparql", consulta)
    elif nouconsulta in consulta:
        print("ja hi ha la consulta nova")
    else:
        print("No trobat on posar la consulta nova")
        return(plantilla)
    columnes = "label,item,p18,p131,p31,p366,p84,p170,p149,p135,p571,p177,p2505,p403,p10241,?nomcient,p5816,p1082,p2043,p2787,p2049,p2048,p2547,p2046,p2234,p2053,p138,p825,p547,p4511,p625,p2795,p6375,p669,p669/p670,p276,p706,p2044,p1435,p373,?allarg:Ullarg,?allum:Ullum,?aample:Uample,?aalt:Ualt,?aprof:Uprof,?aperim:Uperim,?asuperf:Usuperf,?avolum:Uvolum,?asuperfc:Usuperfc"
    plantilla.add("columns", columnes)
    return (plantilla)

def rowllista(llista):
    print(llista)
    text = llista.get()
    numfiles = text.count("Wikidata list/topònim")
    print(numfiles, "topònims")
    wikicode = mwparserfromhell.parse(text)
    #print(wikicode)
    templates = wikicode.filter_templates()
    for template in templates:
      if template.name.matches("wikidata list"):
        #print(template)
        template = arreglaplantilla(template)
        #print (template)
    textnou = str(wikicode)
    if text==textnou:
        print("cap canvi")
    else:
        llista.put(str(wikicode), summary="robot adapta la llista per mostrar la superfície de la conca")

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

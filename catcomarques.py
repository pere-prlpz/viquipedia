#-*- coding: utf-8 -*-
#
# Script per ajudar a crear categories per comarca a Commons (en construcció)

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


def catscomarca(comarca, catrel, catcoms, percom=False, prefsort=""):
    nom = catrel+" in "+comarca
    catcat0 = catrel+" in Catalonia"
    if percom:
        catcat0=catcat0+" by comarca"
    catcat = catcat0 +"|"+prefsort+comarca
    altrescats = [x+" in "+comarca for x in catcoms]
    descr = "* '''[[:Category:"+nom+"]]'''\n"
    descr = descr + "\n".join(["* [[:Category:"+x+"]]" for x in [catcat0]+altrescats])
    catwikitext = "\n".join(["[[Category:"+x+"]]" for x in [catcat]+altrescats])
    descr=descr.replace(" of in ", " of ")
    catwikitext = catwikitext.replace(" of in ", " in ")
    return(nom, descr, catwikitext)

def link_creacat(catpral, contingut=""):
    link = "https://commons.wikimedia.org/wiki/Category:"
    link = link + urllib.parse.quote(catpral)
    link = link + "?action=edit&section=new&nosummary=true&preload=User:PereBot/categories/plantilla_blanc&preloadparams%5b%5d="
    link = link + urllib.parse.quote_plus(contingut)
    return(link)

# el programa comença aquí
arguments = sys.argv[1:]  # per fer: arguments per percom i prefsort
rel = arguments[0]
if "-percom" in arguments:
    percom=True
    arguments.remove("-percom")
else:
    percom=False
if "-of" in arguments:
    pref="of"
    arguments.remove("-of")
else:
    pref=""
altres = arguments[1:]
comarques = ["Moianès", "Lluçanès", "Priorat", "Terra Alta", "Ribera d'Ebre", 
"Conca de Barberà", "Montsià", "Alt Camp", "Baix Ebre", "Baix Penedès", "Baix Camp", 
"Tarragonès", "Alt Penedès", "Garraf", "Anoia", "Baix Llobregat", "Barcelonès", 
"Bages", "Berguedà", "Vallès Oriental", "Vallès Occidental", "Osona", "Baixa Cerdanya", 
"Selva", "Baix Empordà", "Pla de l'Estany", "Gironès", "Solsonès", "Segarra", 
"Garrigues", "Urgell", "Pla d'Urgell", "Segrià", "Noguera", "Pallars Jussà", 
"Alt Urgell", "Pallars Sobirà", "Alta Ribagorça", "Maresme", "Garrotxa", 
"Ripollès", "Alt Empordà", "Val d'Aran"]
comarques.sort()
informe = "== [[:Category:" + rel + " in Catalonia]] ==\n\n".replace(" of in ", " in ")
for comarca in comarques:
    (nomcat, infcat, contcat) = catscomarca(comarca, rel, altres, percom, pref)
    informe = informe + infcat + "\n"
    informe = informe + link_creacat(nomcat, contcat) + "\n\n"
print (informe)
site=pwb.Site('commons')
paginforme = pwb.Page(site, "User:PereBot/categories per comarca")
sumari = "Robot preparant categories de "+rel
try:
    text0 = paginforme.get()+"\n\n"
except pwb.exceptions.NoPageError:
    text0 = ""
paginforme.put(text0+informe+"\n\n--~~~~\n", sumari)


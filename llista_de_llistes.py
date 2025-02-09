#-*- coding: utf-8 -*-
#
# Script per crear llistes de llistes de topònims de municipis del Rosselló i el Conflent

import pickle
import re

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

with open('C:/Users/Pere/Documents/perebot/comunes.pickle', 'rb') as f:
    comunes=pickle.load(f)
#print(comunes)
noms = [comunes[kcom]["itemLabel"]["value"] for kcom in comunes if ("comarca" in comunes[kcom].keys() and comunes[kcom]["comarcaLabel"]["value"]=="Conflent")]
print(noms)
print(len(noms))
noms.sort()
for nom in noms:
    print("# [[Llista de topònims "+de(nom, enllac=False)+"]]")
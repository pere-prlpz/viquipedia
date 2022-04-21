#-*- coding: utf-8 -*-

# trobar per què un article és en una categoria

import pywikibot as pwb
from pywikibot import pagegenerators
import re
import pickle
import sys

def miracat(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, vell=False, llegir=True, prof=20, 
            noseg=[], noinc=[], noincregex="", verbose="nou"):
    # vell: consulta el diccionari vell
    # llegir: llegeix el que no trobi als diccionaris
    # noseg: categories que llegeix però no continua més avall
    # noinc: categories que no llegeix
    # noincregex: categories que no llegeix (filtre regex de les que no)
    # verbose: sí, nou, tot
    if verbose=="sí":
        print(catnom, prof)
    noincreg = (len(noincregex)>0)
    if catnom in dicc:
        font = "dicc nou"
        art0 = dicc[catnom]["art0"]
        cat0 = dicc[catnom]["cat0"]
    elif vell and catnom in diccvell:
        font = "dicc vell"
        art0 = diccvell[catnom]["art0"]
        cat0 = diccvell[catnom]["cat0"]
    elif llegir==False:
        font = "no llegit"
        art0 = []
        cat0 = []    
    else:
        font = "llegit"
        cat = pwb.Category(site,catnom)
        articles = pagegenerators.CategorizedPageGenerator(cat, recurse=0)
        art0 = []
        for art in articles:
            art0.append(art.title())
        categories = pagegenerators.SubCategoriesPageGenerator(cat, recurse=0)
        cat0 = []
        for cat in categories:
            cat0.append(cat.title())
        dicc[catnom] = {"art0":art0, "cat0":cat0}
        diccvell[catnom] = {"art0":art0, "cat0":cat0}
    art1 = set(art0)
    cat1 = set(cat0)
    if prof<=0:
        if verbose == "sí":
            print("Arribat al límit de profunditat")
            print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
        return(art0, cat0, dicc, diccvell, art1, cat1)
    for cat in cat0:
        if cat in noinc:
            continue
        if noincreg and re.search(noincregex, cat):
            # print("No passa:",cat)
            continue
        # else:
            # print("Passa:",cat)
        if cat in noseg:
            profseguent = 0
        else:
            profseguent = prof-1
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, prof=profseguent, 
                                                      noseg=noseg, noinc=noinc, noincregex=noincregex)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    if verbose=="sí" or (verbose=="nou" and font=="llegit"):
        print(prof, "art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)
    
def inicialitzadicc():
    # carregar fitxer de categories
    try:
        diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
    except FileNotFoundError:
        print ("Fitxer de categories no trobat. Començant de nou.")
        diccatvell={}
    diccat = {}
    lencats = 0
    return(diccat, diccatvell, lencats)

def camicat(cat, catbuscar, artbuscar, dicc={}, diccvell={}, prof=20):
    profseguent = prof-1
    art0,cat0,dicc,diccvell,art1,cat1=miracat(cat, dicc=dicc, diccvell=diccvell, vell=True, llegir=False, prof=prof)
    if len(catbuscar & cat1)>0 or len(artbuscar & art1) > 0 and prof>=0:
        if len(catbuscar & set(cat0))>0 or len(artbuscar & set(art0)) > 0:
            cua = "DIRECTAMENT"
        else:
            cua=""
        print(prof, cat, "CÓNTÉ L'OBJECTIU", cua)
        for cati in cat0:
            camicat(cati, catbuscar, artbuscar, dicc=dicc, diccvell=diccvell, prof=profseguent)
    elif prof <0:
        print(prof, cat, "límit de profunditat")
    else:
        #print(prof, cat, "no conté l'objectiu")
        pass
    return
        
 
# -------------------
# carregar fitxer de categories
diccat, diccatvell, lencats = inicialitzadicc()
arguments = sys.argv[1:]
catsup = arguments[0]
catbuscar = {x for x in arguments[1:] if re.match("[Cc]ategoria:", x)}
artbuscar = {x for x in arguments[1:] if not re.match("[Cc]ategoria:", x)}
print ("Buscant perquè són a", catsup)
print ("les categories", catbuscar)
print ("i els articles", artbuscar)
camicat(catsup, catbuscar, artbuscar, dicc=diccat, diccvell=diccatvell, prof=20)
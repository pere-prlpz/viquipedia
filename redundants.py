#-*- coding: utf-8 -*-

# programa per treu categories redundants
import sys
import re
import pickle
import pywikibot as pwb
from pywikibot import pagegenerators

def miracat(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, vell=False, prof=20, verbose=False):
    if verbose:
        print(catnom, prof)
    if catnom in dicc:
        font = "dicc nou"
        art0 = dicc[catnom]["art0"]
        cat0 = dicc[catnom]["cat0"]
    elif vell and catnom in diccvell:
        font = "dicc vell"
        art0 = diccvell[catnom]["art0"]
        cat0 = diccvell[catnom]["cat0"]
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
        if verbose:
            print("Arribat al límit de profunditat")
            print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
        return(art0, cat0, dicc, diccvell, art1, cat1)
    for cat in cat0:
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, prof=prof-1, verbose=verbose)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    if verbose:
        print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)

def desadicc(diccatvell):
    fitxer = r"C:\Users\Pere\Documents\perebot\categories.pkl"
    pickle.dump(diccatvell, open(fitxer, "wb")) 
    print("Diccionari vell desat. Diccionari:",lencats,"Diccionari vell:", len(diccatvell))
    return

def posacats(cats=0, catsno=[], arts=[], site=pwb.Site('ca'), treu = True):
    # treu: treure les categories catsno encara que no hi posi les cats
    #print(cat)
    for art in arts:
        print(art)
        pag=pwb.Page(site, art)
        try:
            textvell=pag.get()
        except pwb.exceptions.IsRedirectPageError:
            print("Redirecció")
            continue
        except pwb.exceptions.NoPageError:
            print("La pàgina no existeix")
            continue
        text0 = textvell
        textnou = textvell # per evitar errors si realment no posa la categoria
        for cat in cats:
            if re.search("\[\["+cat+"(\|.*)?\]\]", textvell):
                print("La categoria ja hi és")
                continue
            if re.search("\]\]( *\n *)*$", textvell):
                #print("Categoria al final")
                textnou = re.sub("\]\]( *\n *)*$","]]\n[["+cat+"]]\n", textvell, count=1)
                textvell = textnou
            elif re.search("\[\[[Cc]ategor(ia|y) ?:", textvell):
                print ("Categoria al principi")
                textnou = re.sub("\[\[[Cc]ategor(ia|y) ?:","[["+cat+"]]\n[[Categoria:", textvell, count=1)
                textvell = textnou
            else:
                print ("No trobat on posar la categoria")
                continue
        if False and textnou != text0: # anul·lat (només per proves)
            pagprova = pwb.Page(site, "Usuari:PereBot/taller")
            sumari = "Robot copia [["+art+"]] tot fent proves"
            pagprova.put(textnou, sumari)
        sumtreu=""
        if textnou != text0 or treu:
            for catno in catsno:
                if len(cats)>0 and catno == cat:
                    print(catno, "redundant amb si mateixa")
                    continue
                if re.search("\[\["+catno+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+catno+"\]\]\n?", "", textnou)
                    #textnou=re.sub("\[\["+catno+"\|.*\]\]", "", textnou)
                    sumtreu=" i treu la [["+catno+"]] redundant"
                else:
                    print(catno, "no trobada")
            textcats = " ".join(["[["+cat+"]]" for cat in cats])
            if len(cats)>0:
                sumari = "Robot posa "+textcats+" a partir de Wikidata"+sumtreu
            else:
                sumari = "Robot treu la [["+catno+"]] redundant"
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
    return

def posaqcats(cats, catsno=[], arts=[], nqcat=r"C:\Users\Pere\Documents\perebot\qcat.txt"): # catsno no implementat
    cats = [re.sub("Categoria:","",cat) for cat in cats]
    catsno = [re.sub("Categoria:","",cat) for cat in catsno]
    tcats = "|".join(["+Category:"+cat for cat in cats])
    if len(catsno)>0:
        tcatsno = "|".join(["-Category:"+cat for cat in catsno])
        tcats = tcats+"|"+tcatsno
    comandes = "\n".join([art+"|"+tcats for art in arts])+"\n"
    with open(nqcat, "a", encoding='utf-8') as f:
        f.write(comandes)
        f.close()

# el programa comença aquí
# arguments que podrien anar com a arguments
titrel = "Categoria:Biografies per segle"
profcat = 0 # fins on buscar categories pre treure
profart = 1 # fins on buscar articles amb categories redundants
qcat = False # True escriure en fitxer, False editar directament
#
nqcat = r"C:\Users\Pere\Documents\perebot\qcat.txt"
# inicialitzar miracats
try:
    diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
except FileNotFoundError:
    print ("Fitxer de categories no trobat. Començant de nou.")
    diccatvell={}
icat=0
diccat={}
lencats = 0
#
art0, cat0, diccat, diccatvell, articles, cat1=miracat(titrel, dicc=diccat, diccvell=diccatvell, vell=False, prof=profcat)
print(cat1)
for catred in cat1: # cat1 és la categoria que comprovarem si és redundant 
    print(catred)
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(catred, dicc=diccat, diccvell=diccatvell, vell=False, prof=0)
    artsup = art0
    print(art0)
    print(cat0)
    for cat in cat0:
        print("Mirant", cat, "redundant amb", catred)
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=profart, verbose=True)
        artinf = articles
        artredundants = set(artsup).intersection(set(artinf))
        print("Redundants:", artredundants)
        if len(artredundants)>0:
            if qcat:
                posaqcats([], catsno = [catred], arts=artredundants, nqcat=nqcat)
            else:
                print("Editant per:", [], [catred], artredundants) 
                posacats([], catsno = [catred], arts=artredundants)
## PENDENT: Desar els diccionaris de categories        
    
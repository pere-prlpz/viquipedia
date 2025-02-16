#Crea pàgina d'articles sense referència en una categoria
#Formats previstos:
#python senserefcat.py categoria 
#on categoria és el nom de la categoria sesnse prefix (com ara Garraf o "Vilanova de Meià")
#PER IMPLEMENTAR: python senserefcat.py categoria -prof:p
#Si no s'hi posa categora la llegeix d'un fitxer (no torna a llegir la categoria però
#sí que llegeix la categoria d'articles sense referències; útil per actualitzar ràpid)
import pywikibot as pwb
from pywikibot import pagegenerators
import pickle
import sys

# el programa comença aquí
arguments = sys.argv[1:]  
if len(arguments)>0:
    catnom = "Categoria:"+" ".join(arguments)
    desa = True
else:
    catnom=""
    desa=False
print(catnom)
site=pwb.Site('ca')
if catnom != "":
    cat = pwb.Category(site,catnom)
    print(cat)
    profunditat = 8
    articles = pagegenerators.CategorizedPageGenerator(cat, recurse=profunditat)
    artcat = []
    for article in articles:
        artcat.append(article.title())
    print(len(artcat))
    if desa:
        dades = (catnom, profunditat, artcat)
        with open(r"categoria.pkl", "wb") as fitxer:
            pickle.dump(dades, fitxer)
            print("desat")
else:
    with open(r"categoria.pkl", "rb") as fitxer:
        (catnom, profunditat, artcat) = pickle.load(fitxer)
    print("carregat")
ncat = len(artcat)
catFR = pwb.Category(site,"Categoria:Articles sense referències")
articles = pagegenerators.CategorizedPageGenerator(catFR, recurse=profunditat)
faltaref = []
for article in articles:
    faltaref.append(article.title())
print(len(faltaref))
nnref = len(faltaref)
senseref = list(set(artcat) & set(faltaref))
senseref.sort()
print(senseref)
nsenseref = len(senseref)
informe = "\n".join(["# [["+x+"]]" for x in senseref])
print(informe)
informe_inici = "Pàgines de la [[:"+catnom+"]] (profunditat "+str(profunditat)+") amb {{tl|Falten referències}}.\n\n"
informe_inici = informe_inici+"* "+str(ncat)+" pàgines a la categoria.\n"
informe_inici = informe_inici+"* "+str(nnref)+" articles sense referències a la Viquipèdia.\n"
informe_inici = informe_inici+"* "+str(nsenseref)+" articles sense referències a la categoria i en aquesta llista.\n"
informe_final = "--~~~~"
informe = informe_inici + informe +"\n"+ informe_final
paginforme = pwb.Page(site, "Usuari:PereBot/articles sense referències")
sumari = "Robot actualitzant articles sense referències de la [[:"+catnom+"]] amb profunditat "+str(profunditat)+" ("+str(len(senseref))+" articles)"
paginforme.put(informe, sumari)



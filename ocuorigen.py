#-*- coding: utf-8 -*-

# posar categories per ocupació i origen

import pywikibot as pwb
from pywikibot import pagegenerators
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import pickle
import sys
import time
import urllib
import urllib.request
#import json
from urllib.parse import unquote

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_query(query):
    print("Carregant query")
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    #print(wd)
    return (wd)

def miracatinv(cat, dicc, prof=20, noinc=[]):
    lliures = {cat}
    super = {cat}
    while len(lliures)>0 and prof>0:
        lliures = {x for x in dicc if (not lliures.isdisjoint(set(dicc[x]["cat0"])) and x not in noinc)}
        #print("Directes:", lliures)
        lliures = lliures - super
        super = lliures | super
        #print("Tots:", super)
        #print("Lliures:", lliures)
    return(super) 

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
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, llegir=llegir, prof=profseguent, 
                                                      noseg=noseg, noinc=noinc, noincregex=noincregex, verbose=verbose)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    if verbose=="sí" or (verbose=="nou" and font=="llegit"):
        print(prof, "art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)
    
def miracatdesada(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, diccatgran={}, gran=True, vell=False, llegir=True, prof=20, 
            noseg=[], noinc=[], noincregex="", verbose="nou"):
    if catnom in diccatgran and gran==True:
        return (diccatgran[catnom]+(diccatgran,))
    else:
        art0, cat0, dicc, diccvell, art1, cat1 = miracat(catnom=catnom, dicc=dicc, diccvell=diccvell, vell=vell, llegir=llegir, prof=prof, 
                                                      noseg=noseg, noinc=noinc, noincregex=noincregex, verbose=verbose)
        diccatgran[catnom] = (art0, cat0, dicc, diccvell, art1, cat1)
        if verbose!="no":
            print(catnom, "desada")
        return (art0, cat0, dicc, diccvell, art1, cat1, diccatgran)

def catmaj(x):
    # Endreça el nom d'una categoria
    if ":" in x:
        nom=re.split(":", x)[1]
    else:
        nom=x
    nom=nom.strip()
    nom=re.sub("  "," ", nom)
    nom=nom[0].upper()+nom[1:]
    return ("Categoria:"+nom)

def minuscula(x):
    return (x[0].lower()+x[1:])

def imprimeix(text, file=r"C:\Users\Pere\Documents\perebot\informe_ocuorigen.txt"):
    with open(file, "a", encoding="utf-8") as f:
        f.write(text+"\n")
        f.close()
    return
    
def imprimeixlinies(text, file=r"C:\Users\Pere\Documents\perebot\informe_ocuorigen.txt", afegit="\n"):
    text = [text+afegit for text in text]
    with open(file, "a", encoding="utf-8") as f:
        f.writelines(text+["\n"])
        f.close()
    return
    
def desadicc(diccatvell, diccatnou=[1], lendic=0):
    if len(diccatnou)>lendic:
        fitxer = r"C:\Users\Pere\Documents\perebot\categories.pkl"
        pickle.dump(diccatvell, open(fitxer, "wb")) 
        lennou = len(diccatnou)
        print("Diccionari vell desat. Diccionari:",lennou,"Diccionari vell:", len(diccatvell))
        return (lennou)
    else:
        return(lendic)

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

def posacat(cat, catsno=[], arts=[], site=pwb.Site('ca'), extrasumari=""):
    #print(cat)
    if not(re.search("^[Cc]ategoria:", cat)):
        print("Això no sembla una categoria:",cat)
        return
    n = len(arts)
    i = 0
    for art in arts:
        i = i+1
        print(i, "/", n, art)
        pag=pwb.Page(site, art)
        try:
            textvell=pag.get()
        except pwb.exceptions.IsRedirectPageError:
            print("Redirecció:", pag)
            continue
        except pwb.NoPage:
            print("La pàgina no existeix:", pag)
            continue
        if re.search("\[\["+cat+"(\|.*)?\]\]", textvell):
            print("La categoria ja hi és")
            continue
        if re.search("\]\]( *\n *)*$", textvell):
            #print("Categoria al final")
            textnou = re.sub("\]\]( *\n *)*$","]]\n[["+cat+"]]\n", textvell, count=1)
        elif re.search("\[\[[Cc]ategor(ia|y) ?:", textvell):
            print ("Categoria al principi")
            textnou = re.sub("\[\[[Cc]ategor(ia|y) ?:","[["+cat+"]]\n[[Categoria:", textvell, count=1)
        else:
            print ("No trobat on posar la categoria. Categoria al final.")
            textnou = textvell + "\n[["+cat+"]]\n"
        if textnou != textvell and False: # anul·lat (només per proves)
            pagprova = pwb.Page(site, "Usuari:PereBot/taller")
            sumari = "Robot copia [["+art+"]] tot fent proves"
            pagprova.put(textnou, sumari)
        sumtreu=""
        if textnou != textvell:
            sumtreu = ""
            for catno in catsno:
                if catno == cat:
                    #print(catno, "redundant amb si mateixa")
                    continue
                if re.search("\[\["+re.escape(catno)+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+re.escape(catno)+"\]\]\n?", "", textnou)
                    sumtreu=sumtreu+" i treu la [["+catno+"]] redundant"
            sumari = "Robot posa la [["+cat+"]] "+extrasumari+sumtreu
            try:
                pag.put(textnou, sumari)
            except pwb.exceptions.LockedPageError:
                print ("Pàgina protegida")
                continue
    return

def posaqcats(cats, catsno=[], arts=[], nqcat=r"C:\Users\Pere\Documents\perebot\qcat.txt", treuper=True): 
    cats = [re.sub("Categoria:","",cat) for cat in cats]
    catsno = [re.sub("Categoria:","",cat) for cat in catsno]
    tcats = "|".join(["+Category:"+cat for cat in cats])
    if treuper:
        catsno = [x for x in catsno if not " per " in x]
    if len(catsno)>0:
        tcatsno = "|".join(["-Category:"+cat for cat in catsno])
        tcats = tcats+"|"+tcatsno
    comandes = "\n".join([art+"|"+tcats for art in arts])+"\n"
    with open(nqcat, "a", encoding='utf-8') as f:
        f.write(comandes)
        f.close()


# el programa comença aquí ----------------------------------------
ordena = True # ordenar categories per mida
ordena3 = True # ordenar tenint en compte categories pares
qcnet = False   # netejar el fitxer quickcategories
qcat = False   # fer servir quickcategories en comptes d'editar directament
nqcat = r"C:\Users\Pere\Documents\perebot\qcat.txt"
llistano = False
imprimeix("\n"+time.asctime(time.localtime(time.time())))
site=pwb.Site('ca')
actualitza = True
actualitzatot = False
arguments = sys.argv[1:]
if len(arguments)>0:
    if "-act" in arguments: # valor per defecte
        actualitza=True
        arguments.remove("-act")
    if "-noact" in arguments:
        actualitza=False
        arguments.remove("-noact")
    if "-acttot" in arguments:
        actualitza=True
        actualitzatot=True
        arguments.remove("-acttot")
    if "-llistano" in arguments: # fer llista de categories no cobertes
        llistano=True
        arguments.remove("-llistano")
    if "-qcat" in arguments:
        qcat=True
        arguments.remove("-qcat")
    if "-net" in arguments:
        qcnet=True
        arguments.remove("-net")
    if "-noordenis" in arguments:
        ordena=False
        arguments.remove("-noordenis")
if qcnet:
    with open(nqcat, "w", encoding='utf-8') as f:
        f.write("")
        f.close()

# llegir dades de Wikidata
ocupawd = get_query("""# Categories d'ocupacions
SELECT DISTINCT ?ocupacio ?ocupacioLabel ?cat ?categoria ?conte ?conteLabel
WHERE {
  ?ocupacio wdt:P31/wdt:P279* wd:Q28640.
  ?ocupacio wdt:P910 ?cat.
    ?categoria schema:about ?cat.
    ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
  OPTIONAL{?cat wdt:P4224 ?conte}
  SERVICE wikibase:label {bd:serviceParam wikibase:language "ca" . } 
}""")
#print(ocupawd)
docucat = {x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in ocupawd}
#print(docucat)
print("docucat",len(docucat))
dcatocu = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):\
x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/","")\
for x in ocupawd}
print("dcatocu",len(dcatocu))

idpwd = get_query("""# Categories d'identitats personals
SELECT DISTINCT ?ocupacio ?ocupacioLabel ?cat ?categoria ?conte ?conteLabel
WHERE {
  ?ocupacio wdt:P31/wdt:279* wd:Q844569.
  ?ocupacio wdt:P910 ?cat.
    ?categoria schema:about ?cat.
    ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
  OPTIONAL{?cat wdt:P4224 ?conte}
  SERVICE wikibase:label {bd:serviceParam wikibase:language "ca" . } 
}""")
#print(idpwd)
didpcat = {x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in idpwd}
#print(didpcat)
print("didpcat",len(didpcat))
dcatidp = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):\
x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/","")\
for x in idpwd}
print("dcatidp",len(dcatidp))
dcatocu.update(dcatidp)
print("dcatocu",len(dcatocu)) # afegeix identitats personals a les ocupacions

# Compte que sobreescriu les variables per identificació (si calen després, cal canviar-les-hi el nom)
idpwd = get_query("""# Categories d'ocupació (etiqueta)
SELECT DISTINCT ?ocupacio ?ocupacioLabel ?cat ?categoria ?conte ?conteLabel
WHERE {
  ?ocupacio wdt:P31/wdt:279* wd:Q12737077.
  ?ocupacio wdt:P910 ?cat.
    ?categoria schema:about ?cat.
    ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
  OPTIONAL{?cat wdt:P4224 ?conte}
  SERVICE wikibase:label {bd:serviceParam wikibase:language "ca" . } 
}""")
#print(idpwd)
didpcat = {x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in idpwd}
#print(didpcat)
print("didpcat",len(didpcat))
dcatidp = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):\
x["ocupacio"]["value"].replace("http://www.wikidata.org/entity/","")\
for x in idpwd}
print("dcatidp (ocupacions)",len(dcatidp))
dcatocu.update(dcatidp)
print("dcatocu",len(dcatocu)) # afegeix ocupacions (etiqueta) a les ocupacions

llocswd = get_query("""# categories persones per lloc
SELECT DISTINCT ?lloc ?cat ?categoria
WHERE {
    ?lloc wdt:P1464|wdt:P1792 ?cat.
    ?categoria schema:about ?cat.
    ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
dlloccat = {x["lloc"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in llocswd}
#print(dlloccat)
print("dlloccat", len(dlloccat))
dcatlloc = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):\
x["lloc"]["value"].replace("http://www.wikidata.org/entity/","")\
for x in llocswd}
#print(dcatlloc)
print("dcatlloc", len(dcatlloc))

cat2wd=get_query("""# categories de persones amb temes associats super P131
SELECT DISTINCT ?cat ?categoria ?associat WHERE {
  ?cat wdt:P31 wd:Q4167836.
  ?cat wdt:P4224 wd:Q5.
  ?cat wdt:P971 ?lloc.
  ?lloc wdt:P131 [].
  ?categoria schema:about ?cat.
  ?cat wdt:P971 ?associat.
  ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
dcatrel = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):[]\
for x in cat2wd}
#print(dcatrel)
for x in cat2wd:
    cat = urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
    tema = x["associat"]["value"].replace("http://www.wikidata.org/entity/","")
    dcatrel[cat].append(tema)
#print(dcatrel)
print("dcatrel", len(dcatrel))
dintercat = {}
for cat in dcatrel:
    relacions = dcatrel[cat]
    if "Q19660746" in relacions:
        relacions.remove("Q19660746")
    if len(relacions) != 2:
        continue
    qlloc = ""
    qocu = ""
    for tema in relacions:
        if tema in docucat and qocu=="":
            qocu = tema
        if tema in dlloccat and qlloc =="":
            qlloc = tema
    if qlloc != "" and qocu !="":
        dintercat[cat] = {"qocu":qocu, "qlloc":qlloc, "cocu":docucat[qocu], "clloc":dlloccat[qlloc]}
#print(dintercat, len(dintercat))
#for cat in dintercat: print(cat, dintercat[cat]["cocu"], dintercat[cat]["clloc"])
print("dintercat", len(dintercat))
sintercat = {(x, tuple(sorted((dintercat[x]["cocu"], dintercat[x]["clloc"])))) for x in dintercat}
#print(list(sintercat)[0:6])
print("sintercat:", len(sintercat))

# compte variables repetides
cat2wd=get_query("""# categories de persones amb temes associats amb estats
SELECT DISTINCT ?cat ?categoria ?associat WHERE {
  ?cat wdt:P31 wd:Q4167836.
  ?cat wdt:P4224 wd:Q5.
  ?cat wdt:P971 ?lloc.
  ?lloc wdt:P31 wd:Q3624078.
  ?categoria schema:about ?cat.
  ?cat wdt:P971 ?associat.
  ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
dcatrel = {urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "):[]\
for x in cat2wd}
#print(dcatrel)
for x in cat2wd:
    cat = urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
    tema = x["associat"]["value"].replace("http://www.wikidata.org/entity/","")
    dcatrel[cat].append(tema)
#print(dcatrel)
print("dcatrel", len(dcatrel))
dintercat = {}
for cat in dcatrel:
    relacions = dcatrel[cat]
    if "Q19660746" in relacions:
        relacions.remove("Q19660746")
    if len(relacions) != 2:
        continue
    qlloc = ""
    qocu = ""
    for tema in relacions:
        if tema in docucat and qocu=="":
            qocu = tema
        if tema in dlloccat and qlloc =="":
            qlloc = tema
    if qlloc != "" and qocu !="":
        dintercat[cat] = {"qocu":qocu, "qlloc":qlloc, "cocu":docucat[qocu], "clloc":dlloccat[qlloc]}
#print(dintercat, len(dintercat))
#for cat in dintercat: print(cat, dintercat[cat]["cocu"], dintercat[cat]["clloc"])
print("dintercat", len(dintercat))
sintercat2 = {(x, tuple(sorted((dintercat[x]["cocu"], dintercat[x]["clloc"])))) for x in dintercat}
#print(list(sintercat)[0:6])
print("sintercat2:", len(sintercat2))

cat1perswd = get_query("""# categories principals d'una persona
SELECT ?item ?cat ?categoria WHERE {
  ?item wdt:P31 wd:Q5.
  ?item wdt:P910 ?cat.
  ?categoria schema:about ?cat.
  ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
cat1perswdbib = get_query("""# categories principals de personatges bíblics humans
SELECT ?item ?cat ?categoria WHERE {
  ?item wdt:P31 wd:Q20643955.
  ?item wdt:P910 ?cat.
  ?categoria schema:about ?cat.
  ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
}""")
cat1pers = [urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
            for x in (cat1perswd+cat1perswdbib)]
#print(cat1pers)
print("cat1pers", len(cat1pers))

# carregar fitxer de categories
diccat, diccatvell, lencats = inicialitzadicc()
filtreno = "Categoria:((Virreis|Governadors( civils)?|Diputats.* pel districte|Capitans .*generals|(Arqueb|B)isbes|Abats|(Sants p|P)atriarques( llatins)?|Ducs|Comtes|Marquesos|Prínceps|Reis|Governants( .*)?|Jurats|Senyors|Ducs) d|(Palaus|Pel·lícules|Obres|Grups|Nissagues|Dinasties|Història|Sindicats|Estats|Topònims|[Gg]erra) )|per papa" #categories a no mirar
diccatgran={}

# busquem categories per nom
ntrobats = 0
nwd = 0
dcatinternom = {}
for catlloc in list(dcatlloc):
    gentilici = re.sub("^Categoria:", "", catlloc)
    gentilici = re.sub("^(Persones|Berguedans|Cerdans|Garriguencs|Penedesencs|Pallaresos|Selvatans|Urgellencs|Vallesans|Macedonis|Bascos) ",
                       "", gentilici)
    gentilici = gentilici[0].lower()+gentilici[1:]
    #print(gentilici)
    for catocu in list(dcatocu):
        proposta = catocu+" "+gentilici
        #print(proposta)
        if proposta in diccatvell:
            #print(proposta, "EXISTEIX LA CATEGORIA")
            ntrobats = ntrobats + 1
            #print(ntrobats, dcatlloc[catlloc], dcatocu[catocu])
            dcatinternom[proposta]=[catlloc, catocu]
print("dcatinternom:", len(dcatinternom), "categories trobades pel nom")
scatinternom = {(x, tuple(sorted((dcatinternom[x][0], dcatinternom[x][1])))) for x in dcatinternom}
print(list(scatinternom)[0:6])
print("scatinternom:", len(scatinternom))

# busquem a les categories per grup humà
art0, cat0, diccat, diccatvell, art1, cgrups=miracat("Categoria:Biografies per grup humà", dicc=diccat, diccvell=diccatvell, 
                                                      vell=True, prof=10, noseg=cat1pers)
lencats=desadicc(diccatvell, diccat, lencats)
tgrups = []
print("grups com a lloc")
for cat in cgrups:
    if " per " in cat:
        continue
    gentilici = re.sub("Categoria:", "", cat)
    for subcat in cgrups:
        if cat==subcat:
            continue
        if " per " in subcat:
            continue
        if re.search(gentilici, subcat) or re.search(gentilici.casefold(),subcat):
            queda=re.sub(gentilici,"",subcat).strip()
            queda=re.sub(gentilici.casefold(),"",queda)
            #queda=re.sub("  "," ", queda)
            #queda=re.sub(": ",":", queda)
            queda=catmaj(queda)
            print(subcat,"=", cat, "+", queda, queda in diccatvell)
            if queda in diccatvell:
                tgrups.append((subcat, tuple(sorted((cat, queda)))))
            elif re.match("Categoria:D",queda):
                queda=re.sub(gentilici,"Persones",subcat).strip()
                queda=re.sub(gentilici.casefold(),"Persones",queda).strip()
                queda=catmaj(queda)
                print(subcat,"=", cat, "+", queda, queda in diccatvell)
                if queda in diccatvell:
                    tgrups.append((subcat, tuple(sorted((cat, queda)))))
                
#print(tgrups)
print("tgrups:",len(tgrups))

# busquem categories per tros del nom
catsmirar = [("Flamencs (persones)", ("flamencs")), 
             ("Georgians dels Estats Units", ("de Geòrgia (Estats Units)", "de Geòrgia")), 
             ("Valencians de la ciutat de València", ("de València")), 
             ("Antics atenencs", ("de l'antiga Atenes", "atenencs de l'antiguitat")),
             ("Antics grecs de l'Àsia Menor", ("grecs de l'antiga Àsia Menor")),
             ("Nord-catalans", ("contemporanis", "contemporànies")),
             ("Catalans del sud contemporanis", ("contemporanis", "contemporànies", "catalans del sud")),
             ("Valencians contemporanis", ("contemporanis", "contemporànies")),
             ("Balears contemporanis", ("contemporanis", "contemporànies")),
             ("Rossellonesos contemporanis", ("contemporanis", "contemporànies")),
             ("Barcelonins contemporanis", ("contemporanis", "contemporànies")),
             ("Catalans històrics", ("històrics", "històriques")),
             ("Balears històrics", ("històrics", "històriques")),
             ("Valencians històrics", ("històrics", "històriques")),
             ("Rossellonesos històrics", ("històrics", "històriques")),
             ("Barcelonins històrics", ("històrics", "històriques")),
            ]
tgrups1 = []
for tcat in catsmirar:
    nom1 = minuscula(tcat[0])
    if type(tcat[1]) is tuple:
        noms = (nom1,) + tcat[1]
    else:
        noms = (nom1, tcat[1])
    print(noms)
    catsup = "Categoria:"+tcat[0]
    art0, cat0, diccat, diccatvell, art1, cat1=miracat(catsup, dicc=diccat, diccvell=diccatvell, vell=True, prof=10, noseg=cat1pers)
    for nomsup in noms:
        for subcat in cat1:
            if " per " in cat1:
                continue
            if re.search(nomsup, subcat):
                queda = re.sub(nomsup, "", subcat)
                queda = re.sub("  "," ", queda).strip()
                #print(nomsup, subcat, queda)
                if queda in diccatvell:
                    tgrups1.append((subcat, tuple(sorted((catsup, queda)))))
print("tgrups1:",len(tgrups1))
lencats=desadicc(diccatvell, diccat, lencats)

# categories amb el gentilici intercalat
catsbase = ["Categoria:Compositors per gènere", "Categoria:Compositors per estil", "Categoria:Compositors per segle", 
            "Categoria:Escriptors per llengua", "Categoria:Escriptors per gènere",
            "Categoria:Poetes per llengua", "Categoria:Poetes per segle", 
            "Categoria:Pintors per segle",
            "Categoria:Ciclistes per origen i palmarès‎", "Categoria:Pilots de motociclisme de velocitat per palmarès‎",
            "Categoria:Jugadors de pilota basca",
            "Categoria:Polítics espanyols per càrrec", "Categoria:Polítics bascos",]
diccgent = {}
for catlloc in list(dcatlloc):
    gentilici = re.sub("^Categoria:", "", catlloc)
    gentilici = re.sub("^(Persones|Vallesans|Penedesencs|Pallaresos|Cerdans|Selvatans|Urgellencs|Macedonis) ", "", gentilici)
    gentilici = gentilici[0].lower()+gentilici[1:]
    diccgent[catlloc]=gentilici
#print(diccgent)
print("diccgent:",len(diccgent))

tgrups2 = []
for catbase in catsbase:
    print(catbase)
    art0, cat0, diccat, diccatvell, art1, cat1=miracat(catbase, dicc=diccat, diccvell=diccatvell, vell=True, prof=14, 
                                                            noinc=cat1pers, noincregex=filtreno)
    cat1 = [cat for cat in cat1 if not re.search(" per ", cat)]
    for catlloc in diccgent:
        regentilici ="\\b"+diccgent[catlloc]+"\\b"
        for subcat in cat1:
            if re.search(regentilici, subcat):
                #print(regentilici," / ",subcat)
                queda=re.sub(regentilici,"",subcat).strip()
                queda=re.sub(regentilici.casefold(),"",queda)
                queda=re.sub("  "," ", queda)
                queda=re.sub(": ",":", queda)
                queda=catmaj(queda)
                #print(subcat, catlloc, queda, (queda in diccatvell))
                if queda in diccatvell:
                    print(subcat,"=", catlloc, "+", queda)
                    tgrups2.append((subcat, tuple(sorted((catlloc, queda)))))
#print(tgrups2)
print("tgrups2:",len(tgrups2))
lencats=desadicc(diccatvell, diccat, lencats)

# categories barrejant noms en totes les posicions
catsgrals = ["Categoria:Religiosos", "Categoria:Polonesos", 
             ("Categoria:Biografies per activitat",7),
             "Categoria:Biografies per causa de la mort",]
ctots = set()
for el in catsgrals:
    if isinstance(el, tuple):
        catinici = el[0]
        prof = el[1]
    else:
        catinici = el
        prof = 7
    print(catinici)
    art0, cat0, diccat, diccatvell, art1, ctotsi=miracat(catinici, dicc=diccat, diccvell=diccatvell, 
                                                         vell=True, llegir=False, prof=8)
    ctotsi.add(catinici)
    ctots = ctots | ctotsi
print("ctots:", len(ctots))
tgrupstot = []
for catsup in ctots:
    gentilici = re.sub("^Categoria:", "", catsup)
    gentilici = re.sub("^(Persones|Vallesans|Penedesencs|Pallaresos|Berguedans|Cerdans|Selvatans|Macedonis) ",
                       "", gentilici)
    gentilici = gentilici[0].lower()+gentilici[1:]
    #print(catsup,"/",gentilici)
    art0, cat0, diccat, diccatvell, art1, cats=miracat(catsup, dicc=diccat, diccvell=diccatvell, 
    
                                                 vell=True, llegir=False, prof=6)
    for subcat in cats:
        if re.search(gentilici, subcat):# or re.search(gentilici.casefold(),subcat):
            queda=re.sub(gentilici,"",subcat).strip()
            queda=re.sub(gentilici.casefold(),"",queda)
            #queda=re.sub("  "," ", queda)
            #queda=re.sub(": ",":", queda)
            queda=catmaj(queda)
            if queda in diccatvell:
                print(subcat,"=", catsup, "+", queda, queda in diccatvell)
                tgrupstot.append((subcat, tuple(sorted((catsup, queda)))))
        elif not catsup==subcat and re.match(catsup, subcat):
            queda = re.sub(catsup,"", subcat)
            #print(queda)
            if catmaj(queda) in diccatvell:
                queda=catmaj(queda)
                print(subcat,"=", catsup, "+", queda, queda in diccatvell)
                tgrupstot.append((subcat, tuple(sorted((catsup, queda)))))
            elif catmaj("Persones "+queda) in diccatvell:
                queda=catmaj("Persones "+queda)
                print(subcat,"=", catsup, "+", queda, queda in diccatvell)
                tgrupstot.append((subcat, tuple(sorted((catsup, queda)))))
print("tgrupstot:", len(tgrupstot))
lencats=desadicc(diccatvell, diccat, lencats)

# ajuntem
scats = sintercat | sintercat2 | scatinternom | set(tgrups) | set(tgrups1) | set(tgrups2) | set(tgrupstot)
print("scats:", len(scats))

# ordenem categories per nombre de subcategories
# i aprofitem per treure categories que no hi van
if ordena:
    print("Carregant categories per ordenar")
    dicmida = {}
    dicmida0 = {}
    n=len(scats)
    i=0
    for tcat in scats:
        cat = tcat[0]
        i=i+1
        # Primer filtre. Veure més avall el segon al bucle d'intersecar.
        if re.search(" per |guerra (mundial|civil)",cat.casefold()):
            print(i,"/",n, cat, "Descartada")
            continue
        if re.search("(emperadors( romans)?|rei(ne)?s|prínceps|governants|presidents|caps d'estat|(grans )?ducs|(primers )?ministres) d", cat.casefold()):
            print(i,"/",n, cat, "Descartada")
            continue
        if re.search("((arque)?bisbes|patriarques|governadors|alcaldes|comtes|ducs|marquesos|senyors|barons) d", cat.casefold()):
            print(i,"/",n, cat, "Descartada")
            continue
        if re.search("(alcaldes|governadors|emperadors) .* d", cat.casefold()):
            print(i,"/",n, cat, "Descartada")
            continue
        if re.search("professors al?s? ", cat.casefold()):
            print(i,"/",n, cat, "Descartada")
            continue
        if re.search(" olímpi(c|que)s ", cat.casefold()):
            print(i,"/",n, cat, "Descartada")
            continue
        if re.search("Categoria:(Sindicats|Estats|Obres|Pel·lícules)", cat):
            print(i,"/",n, cat, "Descartada (no biografies)")
            continue
        art0, cat0, diccat, diccatvell, art1, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, prof=10)
        mida = len(cat1)
        if ordena3:
            catA=tcat[1][0]
            catB=tcat[1][1]
            if catA in dicmida0:
                midaA = dicmida0[catA]
            else:
                art0, cat0, diccat, diccatvell, art1, cat1=miracat(catA, dicc=diccat, diccvell=diccatvell, vell=True, prof=10)
                midaA = len(cat1)
                dicmida0[catA] = midaA
            if catB in dicmida0:
                midaB = dicmida0[catB]
            else:
                art0, cat0, diccat, diccatvell, art1, cat1=miracat(catB, dicc=diccat, diccvell=diccatvell, vell=True, prof=10)
                midaB = len(cat1)
                dicmida0[catB] = midaB
            dicmida[tcat]=mida+midaA+midaB
            print(i,"/",n, cat, dicmida[tcat], mida, midaA, midaB)
        else: # NO PROVAT
            dicmida[tcat]=mida
            print(i,"/",n, cat, dicmida[tcat], mida)
        lencats=desadicc(diccatvell, diccat, lencats)
    print("Categories carregades per poder ordenar.")
    lencats=desadicc(diccatvell, diccat, lencats)
    print("Ordenant")
    catsllococu = sorted(dicmida, key=dicmida.get)
    print("catsllococu:", len(catsllococu)) #
    i = 0
    n = len(catsllococu)
    informecats = ["\nCategories a incloure:"]
    for cat in catsllococu:
        i=i+1
        #print(i, "/", n, cat,dicmida[cat])
        informecats.append("%d/%d %s %d" % (i, n, cat, dicmida[cat]))
    imprimeixlinies(informecats)
    #print(catsllococu)

if llistano:
    print ("Mirant catsi")
    catsi = {cat[0] for cat in catsllococu} | set(dcatlloc) 
    print("Buscant totes les categories")
    cat = "Categoria:Categories de biografies per paràmetre"
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, llegir=False,
                                                            prof=14, noinc=cat1pers, noincregex=filtreno) 
    print("Biografies:", len(cat1))
    print("Restant")
    catno = cat1 - catsi
    print("catno:", len(catno))
    lcatno = list(catno)
    lcatno.sort()
    imprimeixlinies(["Categories no mirades:"]+lcatno)
    
# Comencem a buscar i posar categories
n = len(catsllococu)
i = 0
for tcat in catsllococu:
    i = i+1
    cat = tcat[0]
    print (i,"/",n,tcat)
    if " per " in cat:
        print("Descartada", cat)
        continue
    if re.search("(emperadors( romans)?|rei(ne)?s|prínceps|governants|presidents|caps d'estat) d", cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("((grans )?ducs|marcgravis|marquesos|comtes|senyors|senescals) d", cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("((primers )?ministres|(arque)?bisbes|patriarques|governadors|kh?ans|sultans|emirs) d", cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("pilots d('|e )", cat.casefold()) and not re.search("pilots (d'automobilisme|de motociclisme)", cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("(reis|emperadors|virreis|bisbes|cabdills|kans) ", cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("governants", cat.casefold()):
        print("Descartada provisionalment per problemàtica",cat)
        continue
    if re.search("grups humans|guerra mundial", cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("olímpi(c|que)s", cat.casefold()):# and not re.search("catalans|valencians|balears",cat.casefold()):
        print("Descartada per ser ambigu que sigui una categoria per origen",cat)
        continue
    if re.search("diputats d.* a l'assemblea nacional", cat.casefold()) and not re.search("catalans|valencians|balears",cat.casefold()):
        print("Descartada",cat)
        continue
    if re.search("alcaldes franquistes|dictadors", cat.casefold()): # no tots els que han estat alcaldes i franquistes són alcaldes franquistes
        print("Descartada",cat)
        continue
    if re.search("espanyols|turcs|israelians", cat.casefold()) and not re.search("jueus israelians", cat.casefold()): #|bascos|francesos
        print("Descartada provisionalment",cat)
        continue
    catA=tcat[1][0]
    catB=tcat[1][1]
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, prof=14, noseg=cat1pers)
    lencats=desadicc(diccatvell, diccat, lencats)
    art0, cat0, diccat, diccatvell, articlesA, cat1A, diccatgran=miracatdesada(catA, dicc=diccat, diccvell=diccatvell, diccatgran=diccatgran,
                                                            vell=True, prof=14, noinc=cat1pers, noincregex=filtreno)
    lencats=desadicc(diccatvell, diccat, lencats)
    art0, cat0, diccat, diccatvell, articlesB, cat1B, diccatgran=miracatdesada(catB, dicc=diccat, diccvell=diccatvell, diccatgran=diccatgran,
                                                            vell=True, prof=14, noinc=cat1pers, noincregex=filtreno)
    lencats=desadicc(diccatvell, diccat, lencats)
    posar = (articlesA & articlesB) - articles
    print("Posar provisionalment:", posar, len(posar))
    if not (cat in (cat1A & cat1B)):
        missatge = cat+" no és a la intersecció entre "+catA+" ("+str(cat in cat1A)+") i "+catB+" ("+str(cat in cat1B)+")"
        print(missatge)
        imprimeix(missatge)
        existeix = True
        try:
            text0=pwb.Page(site, cat).get()
        except pwb.IsRedirectPage:
            print("Redirecció:", cat)
            existeix=False
        except pwb.NoPage:
            existeix=False
            print("La categoria no existeix:", cat)
        if existeix:
            missatge = cat + " SÍ que existeix"
        else:
            missatge = cat + " NO existeix. L'eliminem dels diccionaris."
            try:
                del diccatvell[cat]
            except KeyError:
                missatge = missatge + " Però dóna KeyError."
                print(missatge)
                imprimeix(missatge)
            continue
        print(missatge)
        imprimeix(missatge)
        if (actualitza and len(posar)>0) or actualitzatot:
            if cat not in cat1A:
                art0, cat0, diccat, diccatvell, articlesA, cat1A=miracat(catA, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, 
                                                                         noinc=cat1pers, noincregex=filtreno)
                lencats=desadicc(diccatvell, diccat, lencats)
            if cat not in cat1B:
                art0, cat0, diccat, diccatvell, articlesB, cat1B=miracat(catB, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, 
                                                                         noinc=cat1pers, noincregex=filtreno)
                lencats=desadicc(diccatvell, diccat, lencats)
            if not (cat in (cat1A & cat1B)):
                missatge = "Comprovat que "+cat+" NO ÉS a la intersecció entre "+catA+" ("+str(cat in cat1A)+") i "+catB+" ("+str(cat in cat1B)+")"
                print(missatge)
                imprimeix(missatge)
                continue
            else:
                missatge = "Comprovat que "+cat+" SÍ QUE ÉS a la intersecció entre "+catA+" ("+str(cat in cat1A)+") i "+catB+" ("+str(cat in cat1B)+")"
                print(missatge)
                imprimeix(missatge)           
        else:
            print("Deixem córrer la categoria")
            continue
    if len(posar)>0:
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, noseg=cat1pers)
        lencats=desadicc(diccatvell, diccat, lencats)
        if len(posar-articles)==0:
            print("Ja hi són tots")
            continue
        art0, cat0, diccat, diccatvell, articlesA, cat1=miracat(catA, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, 
                                                             noinc=cat1pers, noincregex=filtreno)
        lencats=desadicc(diccatvell, diccat, lencats)
        art0, cat0, diccat, diccatvell, articlesB, cat1=miracat(catB, dicc=diccat, diccvell=diccatvell, vell=False, prof=14, 
                                                             noinc=cat1pers, noincregex=filtreno)
        lencats=desadicc(diccatvell, diccat, lencats)
        posar = (articlesA & articlesB) - articles
        print("Posar definitivament:", posar, len(posar))
        redundants = miracatinv(cat, diccatvell, noinc=cat1pers)
        if re.search("esborranys", cat.casefold()):
            redundants = {x for x in redundants if re.search("esborranys", x.casefold())}
        print("Redundants:",redundants)
        sumari = "intersecant [["+catA+"]] i [["+catB+"]]"
        if qcat:
            posaqcats([cat], redundants, arts=posar, nqcat=nqcat)
        else:
            posacat(cat, catsno=redundants, arts=posar, extrasumari=sumari)
        diccat[cat]["art0"].extend(posar)
        diccatvell[cat]["art0"].extend(posar)    

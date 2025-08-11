#-*- coding: utf-8 -*-

# posa categories per origen a partir del lloc de naixement segons wikidata
# Paràmetres (incomplet):
# -1 (menys u, no menys L) Mira també les divisons administratives de cada lloc (amb P131)
#     però només mira un nivell, o sigui, les directament relacionades amb P131.
# -2 i més números fins a -5: mira el nombre de nivells especificat
# -noordenis: no ordena les categories abans de començar (alternativament, comença per les petites)
# -creacat: no implementat

import pywikibot as pwb
from pywikibot import pagegenerators
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import pickle
import sys
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

def get_no(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# categories de llocs problemàtics per P131
    SELECT DISTINCT ?lloc ?cat ?categoria
    WHERE {
        VALUES ?lloc {wd:Q29 wd:Q142 wd:Q15180 wd:Q28513 wd:Q16957 wd:Q33946 wd:Q12560 wd:Q12544}
        ?lloc wdt:P1464|wdt:P1792 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    # wd:Q83057  wd:Q35657
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    print(wd)
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\noorigen.pkl"
        pickle.dump(wd, open(fitxer, "wb")) 
    return (wd)

def carrega_no(disc=False):
    if disc:
        try:
            a=pickle.load(open(r"C:\Users\Pere\Documents\perebot\noorigen.pkl", "rb"))
        except FileNotFoundError:
            print ("Fitxer origens no mirar no trobat. Important de Wikidata.")
            a=get_no()
    else:
        a=get_no()
    return(a)

def get_catwd(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# categories persones per lloc
    SELECT DISTINCT ?lloc ?cat ?categoria
    WHERE {
        ?lloc wdt:P1464|wdt:P1792 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
      MINUS {?lloc wdt:P31 wd:Q50068795}
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\catorigen.pkl"
        pickle.dump(wd, open(fitxer, "wb")) 
    return (wd)

def carrega_catwd(desa=True, disc=False):
    if disc:
        print("llegint dades del disc")
        a=pickle.load(open(r"C:\Users\Pere\Documents\perebot\catorigen.pkl", "rb"))
    else:
        a=get_catwd(desa)
    return(a)

def get_nascutswd(qllocs, sub=0):
    print("Carregant articles de Wikidata")
    if sub==1:
        p131 = "wdt:P19/wdt:P131?"
    elif sub==2:
        p131 = "wdt:P19/wdt:P131?/wdt:P131?"
    elif sub==3:
        p131 = "wdt:P19/wdt:P131?/wdt:P131?/wdt:P131?"
    elif sub==4:
        p131 = "wdt:P19/wdt:P131?/wdt:P131?/wdt:P131?/wdt:P131?"
    elif sub==5:
        p131 = "wdt:P19/wdt:P131?/wdt:P131?/wdt:P131?/wdt:P131?/wdt:P131?"
    else:
        p131 = "wdt:P19|wdt:P27"
    query="""# articles de persones nascudes en uns llocs
    SELECT DISTINCT ?lloc ?persona ?article
    WHERE {
        VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
        ?persona wdt:P31 wd:Q5.
        ?persona """+p131+""" ?lloc.
        ?article schema:about ?persona.
        ?article schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def get_redundantswd(qllocs):
    print("Carregant categories redundants de Wikidata")
    query="""# categories redundants per origen
    SELECT DISTINCT ?lloc ?redundant ?llocLabel ?categoria
    WHERE {
      VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
      ?lloc wdt:P131+ ?redundant.
        ?redundant wdt:P1464|wdt:P1792 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ca" .
    }
    }"""
    #print(query)
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def artcat(catnom, site=pwb.Site('ca'), profunditat=8):
    # llista d'articles d'una categoria
    cat = pwb.Category(site,catnom)
    articles = pagegenerators.CategorizedPageGenerator(cat, recurse=profunditat)
    llistart = []
    for art in articles:
        llistart.append(art.title())
    return(llistart)

def miracat(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, vell=False, prof=20, noseg=[], noinc=[], verbose="nou"):
    # noseg: categories que llegeix però no continua més avall
    # noinc: categories que no llegeix
    # verbose: sí, nou, tot
    if verbose=="sí":
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
        if verbose == "sí":
            print("Arribat al límit de profunditat")
            print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
        return(art0, cat0, dicc, diccvell, art1, cat1)
    for cat in cat0:
        if cat in noinc:
            continue
        if cat in noseg:
            profseguent = 0
        else:
            profseguent = prof-1
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, prof=profseguent, noseg=noseg, noinc=noinc)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    if verbose=="sí" or (verbose=="nou" and font=="llegit"):
        print(prof, "art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)
    
def posacat(cat, catsno=[], arts=[], site=pwb.Site('ca')):
    #print(cat)
    if not(re.search("^[Cc]ategoria:", cat)):
        print("Això no sembla una categoria:",cat)
        return
    for art in arts:
        print(art)
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
            for catno in catsno:
                if catno == cat:
                    print(catno, "redundant amb si mateixa")
                    continue
                if re.search("\[\["+re.escape(catno)+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+re.escape(catno)+"\]\]\n?", "", textnou)
                    #textnou=re.sub("\[\["+catno+"\|.*\]\]", "", textnou)
                    sumtreu=" i treu la [["+catno+"]] redundant"
            sumari = "Robot posa la [["+cat+"]] a partir de Wikidata"+sumtreu
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
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


# el programa comença aquí
disc=False
discvp=False
desa=True
edita=True
editacat=True
creacat=False
sub = 4
nograns = True
ordena = True
arguments = sys.argv[1:]
if len(arguments)>0:
    if "-disc" in arguments:
        disc=True
        arguments.remove("-disc")
    if "-discvp" in arguments:
        discvp=True
        arguments.remove("-discvp")
    if "-discwp" in arguments:
        discvp=True
        arguments.remove("-discwp")
    if "-nodesis" in arguments:
        desa=False
        arguments.remove("-nodesis")
    if "-noeditis" in arguments:
        edita=False
        editacat=False
        arguments.remove("-noeditis")
    if "-creacat" in arguments:
        creacat=True
        edita=False
        arguments.remove("-creacat")
    if "-noordenis" in arguments:
        ordena=False
        arguments.remove("-noordenis")
    if "-0" in arguments:
        sub = 0
        nograns = False
        arguments.remove("-0")
    if "-1" in arguments:
        sub = 1
        nograns = True
        arguments.remove("-1")
    if "-2" in arguments:
        sub = 2
        nograns = True
        arguments.remove("-2")
    if "-3" in arguments:
        sub = 3
        nograns = True
        arguments.remove("-3")
    if "-4" in arguments:
        sub = 4
        nograns = True
        arguments.remove("-4")
    if "-5" in arguments:
        sub = 5
        nograns = True
        arguments.remove("-5")
    if "-max" in arguments:  # no implementat?
        imax=arguments.index("-max")
        if len(arguments)>imax:
            maxcats=int(arguments.pop(imax+1))
        arguments.remove("-max")
    else:
        maxcats=4
if nograns:
    #nomirar = carrega_no()
    #print(nomirar)
    #qno = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in nomirar]
    #qno = qno + ["Q15348","Q249461"] #Barcelonès i Àmbit Metropolità
    qno = ["Q29", "Q142", "Q15180", "Q28513", "Q16957", "Q33946", "Q12560", "Q12544", "Q15348",
           "Q249461","Q15580","Q12709","Q18678265","Q17005","Q801"]
else:
    nomirar = []
    qno=[]
print ("No mirar:", qno)
diccat, diccatvell, lencats = inicialitzadicc()
catwd = carrega_catwd(disc=disc)
#print("catwd:",catwd)
print ("Llocs grans a ignorar:", qno)
print(len(qno))
qllocs = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in catwd]
#print (qllocs)
print(len(qllocs))
qsi = list(set(qllocs)-set(qno))
#print(qsi)
print("Llocs a mirar:",len(qsi))
dcats = {x["lloc"]["value"].replace("http://www.wikidata.org/entity/",""):\
urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")\
for x in catwd}
#print(dcats)
print(len(dcats))
dcats = {x: dcats[x] for x in qsi}
#print("dcats:",dcats)
print(len(dcats))
ncats=len(dcats)
if ordena:
    print("Carregant categories per ordenar")
    dicmida = {}
    i = 0
    n = len(qsi)
    for qlloc in qsi:
        i = i+1
        print(i, "/", n, qlloc, dcats[qlloc])
        art0, cat0, diccat, diccatvell, art1, cat1=miracat(dcats[qlloc], dicc=diccat, diccvell=diccatvell, vell=True, prof=10)
        dicmida[qlloc]=len(cat1)
        lencats = desadicc(diccatvell, diccat, lencats)
    print("Categories carregades per poder ordenar.")
    desadicc(diccatvell, diccat, lencats)
    print("Ordenant")
    qsi = sorted(dicmida, key=dicmida.get)
    #print("qsi:", qsi, len(qsi)) #
    #for x in qsi: print(x, dcats[x]) #
n = len(qsi)
i=0
qgrups = []
if sub == 0:
    midagrup = 25
else:
    midagrup = 1
qgrups = [qsi[x:x+midagrup] for x in range(0,len(qsi), midagrup)]
#print(qgrups)
print(len(qgrups))
total=0
icat=0
for qgrup in qgrups:
    print(qgrup)
    try:
        nascutswd = get_nascutswd(qgrup, sub=sub) 
    except ValueError:
        print("ValueError (que pot ser json.decoder.JSONDecodeError) per", qgrup)
        print("Ho deixem córrer i continuem")
        continue
    except OSError:
        print("Error OSError (potser urllib.error.URLError) per", qgrup)
        print("Ho deixem córrer i continuem")
        continue
    except urllib.error.HTTPError:
        print("Error urllib.error.HTTPError per", qgrup)
        print("Ho deixem córrer i continuem")
        continue
    except http.client.IncompleteRead:
        print("Error http.client.IncompleteRead per", qgrup)
        print("Ho deixem córrer i continuem")
        continue
    #print(nascutswd)
    total = total+len(nascutswd)
    print(len(nascutswd))
    nascutsllocwd = {}
    for art in nascutswd:
        lloc = art["lloc"]["value"].replace("http://www.wikidata.org/entity/","")
        article = urllib.parse.unquote(art["article"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
        if lloc in nascutsllocwd:
            nascutsllocwd[lloc].append(article)
        else:
            nascutsllocwd[lloc]=[article]
    #print(nascutsllocwd)
    print (len(nascutsllocwd), len(qgrup))
    for qlloc in qgrup:
        icat=icat+1
        cat=dcats[qlloc]
        print(icat,"/", ncats, cat, qlloc)
        if not(qlloc in nascutsllocwd):
            print("No cal buscar")
            continue
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, prof=14)
        #print(articles)
        print(len(articles))
        posar=set(nascutsllocwd[qlloc])-set(articles)
        print("Posar (provisionalment):", posar, len(posar))
        if len(diccat)>lencats:
            lencats=len(diccat)
            desadicc(diccatvell)
        if len(posar)>0:
            art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=14)
            print(len(articles))
            posar=set(nascutsllocwd[qlloc])-set(articles)
            print("Posar (definitivament):", posar, len(posar))
            desadicc(diccatvell, diccat, lencats)
            if len(posar)>0:
                redundantswd = get_redundantswd([qlloc])
                #print(redundantswd)
                redundants = []
                for red in redundantswd:
                    #print(red)
                    redundants.append(urllib.parse.unquote(red["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," "))
                print(redundants)
                posacat(cat, redundants, arts=posar)
                diccat[cat]["art0"].extend(posar)
                diccatvell[cat]["art0"].extend(posar)
print(total)

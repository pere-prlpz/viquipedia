#-*- coding: utf-8 -*-
# Categoritza per lloc de la mort d'acord amb Wikidata
# Adaptat del programa equivalent per lloc de naixement, els noms de les variables poden ser poc adients.
# Arguments:
# -sub: inclou els morts als llocs sense categoria als llocs que els inclouen (P131)
# -tot: com sub i a més posa també categories per llocs grans (estats, comunitats autònomes, etc.).
# -noestats: com tot però sense estats sobirans ni continents
# Si s'ha d'actualitzar molt pot ser recomanable fer primer una passada amb -sub, 
# després una passada amb -noestats i després una passada amb -tot, i d'aquesta manera
# evitar editar gaires vegades el mateix article.
# Si hi ha poc a actualitzar, pot ser més practic fer -tot directament.

import pywikibot as pwb
from pywikibot import pagegenerators
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import pickle
import sys
import urllib
from urllib.parse import unquote

def get_results(endpoint_url, query):
    user_agent = "PereBot/1.0 (ca:User:Pere_prlpz; prlpzb@gmail.com) Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert()
    except ValueError:
        print("Value error")
        print("Retornem diccionari buit")
        return {"results":{"bindings":{}}}

def get_no(nomesestats=False, desa=True):
    print("Carregant articles i categories de Wikidata")
    if nomesestats:
        altres=""
    else:
        altres="wd:Q10742 wd:Q35657 wd:Q15304003 wd:Q83057 wd:Q3336843 wd:Q3024240"
    query="""# categories de nascuts o relacionats amb estats, comunitats, etc.
    SELECT DISTINCT ?lloc ?cat ?categoria
    WHERE {
        VALUES ?grans {wd:Q5107 wd:Q3624078 """+altres+"""}
        ?lloc wdt:P31 ?grans.
        ?lloc wdt:P1465 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\noorigen.pkl"
        pickle.dump(wd, open(fitxer, "wb")) 
    return (wd)

# carrega_no no emprat perquè no fem servir el disc
def carrega_no(disc=False):
    try:
        a=pickle.load(open(r"C:\Users\Pere\Documents\perebot\noorigen.pkl", "rb"))
    except FileNotFoundError:
        print ("Fitxer origens no mirar no trobat. Important de Wikidata.")
        a=get_no()
    return(a)

def get_catwd(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# categories persones per lloc de la mort
    SELECT DISTINCT ?lloc ?cat ?categoria
    WHERE {
        ?lloc wdt:P1465 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
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

def get_mortswd(qllocs):
    print("Carregant articles de Wikidata")
    query="""# articles de persones mortes en un lloc
    SELECT DISTINCT ?lloc ?persona ?article
    WHERE {
        VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
        ?persona wdt:P31 wd:Q5.
        ?persona wdt:P20 ?lloc.
        ?article schema:about ?persona.
        ?article schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    wd = results["results"]["bindings"]
    return (wd)

def get_mortssubwd(qllocs):
    print("Carregant articles de Wikidata")
    query="""# articles de persones mortes en un lloc i les seves divisions
    SELECT DISTINCT ?lloc ?persona ?article
    WHERE {
        VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
        ?persona wdt:P31 wd:Q5.
        ?persona wdt:P20 ?llocConcret.
        ?llocConcret wdt:P131* ?lloc.
        ?article schema:about ?persona.
        ?article schema:isPartOf <https://ca.wikipedia.org/>.
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    try:
        results = get_results(endpoint_url, query)
        wd = results["results"]["bindings"]
    except ValueError:
        print("ValueError detectat; tornem llista buida")
        wd = []
    return (wd)

def get_redundantswd(qllocs):
    print("Carregant categories redundants de Wikidata")
    query="""# categories redundants per mort
    SELECT DISTINCT ?lloc ?redundant ?llocLabel ?categoria
    WHERE {
      VALUES ?lloc {"""+" ".join(["wd:"+el for el in qllocs])+"""}
      ?lloc wdt:P131+ ?redundant.
        ?redundant wdt:P1465 ?cat.
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

def miracat(catnom, site=pwb.Site('ca'), dicc={}, diccvell={}, vell=False, prof=20):
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
        print("Arribat al límit de profunditat")
        print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
        return(art0, cat0, dicc, diccvell, art1, cat1)
    for cat in cat0:
        art10,cat10,dicc,diccvell,art11,cat11=miracat(cat, dicc=dicc, diccvell=diccvell, vell=vell, prof=prof-1)
        art1 = art1.union(art11)
        cat1 = cat1.union(cat11)
    print("art0:", len(art0), "cat0:", len(cat0), "dicc:", len(dicc), "art1:", len(art1), "cat1", len(cat1), font, catnom)
    return(art0, cat0, dicc, diccvell, art1, cat1)

def desadicc(diccatvell):
    fitxer = r"C:\Users\Pere\Documents\perebot\categories.pkl"
    pickle.dump(diccatvell, open(fitxer, "wb")) 
    print("Diccionari vell desat. Diccionari:",lencats,"Diccionari vell:", len(diccatvell))
    return

def posacat(cat, catsno=[], arts=[], site=pwb.Site('ca')):
    #print(cat)
    for art in arts:
        print(art)
        pag=pwb.Page(site, art)
        try:
            textvell=pag.get()
        except pwb.IsRedirectPage:
            print("Redirecció")
            continue
        except pwb.NoPage:
            print("La pàgina no existeix")
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
            print ("No trobat on posar la categoria")
            continue
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
                if re.search("\[\["+catno+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+catno+"\]\]\n?", "", textnou)
                    #textnou=re.sub("\[\["+catno+"\|.*\]\]", "", textnou)
                    sumtreu=" i treu la [["+catno+"]] redundant"
            sumari = "Robot posa la [["+cat+"]] a partir de Wikidata"+sumtreu
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
    return


# el programa comença aquí
sub=False
tot=False
noestats=False
grans=False
disc=False
discvp=False
desa=True
edita=True
editacat=True
creacat=False
arguments = sys.argv[1:]
if len(arguments)>0:
    if "-sub" in arguments:
        sub=True
        tot=False
        arguments.remove("-sub")
    if "-tot" in arguments:
        sub=True
        tot=True
        arguments.remove("-tot")
    if "-noestats" in arguments:
        sub=True
        noestats=True
        arguments.remove("-noestats")
    if "-grans" in arguments:
        sub=True
        grans=True
        arguments.remove("-grans")
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
    if "-max" in arguments:
        imax=arguments.index("-max")
        if len(arguments)>imax:
            maxcats=int(arguments.pop(imax+1))
        arguments.remove("-max")
    else:
        maxcats=4
try:
    diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
except FileNotFoundError:
    print ("Fitxer de categories no trobat. Començant de nou.")
    diccatvell={}
catwd = carrega_catwd(disc=disc)
#print(catwd)
if grans:
    simirar = get_no(desa=False, nomesestats=False)
    qsimirar = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in simirar]
    qno = []
elif not tot: #ignorar els grans
    nomirar = get_no(desa=False, nomesestats=noestats)
    #print (nomirar)
    qno = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in nomirar]
else:
    qno = []
print ("Llocs grans a ignorar:", qno)
print(len(qno))
if not grans:
    qllocs = [x["lloc"]["value"].replace("http://www.wikidata.org/entity/","") for x in catwd]
    #print (qllocs)
else:
    qllocs = qsimirar
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
#print(dcats)
print(len(dcats))
ncats=len(dcats)
if sub:
    midagrup=1
else:
    midagrup = 25
qgrups = [qsi[x:x+midagrup] for x in range(0,len(qsi), midagrup)]
#print(qgrups)
print(len(qgrups))
total=0
icat=0
diccat={}
lencats = 0
for qgrup in qgrups:
    print(qgrup)
    try:
        if sub:
            mortswd = get_mortssubwd(qgrup) 
        else:
            mortswd = get_mortswd(qgrup)
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
    #print(mortswd)
    total = total+len(mortswd)
    print(len(mortswd))
    if len(mortswd)==0:
        print("Cap mort en aquest grup")
        continue
    nascutsllocwd = {}
    for art in mortswd:
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
        if not(qlloc in nascutsllocwd):# and not(sub):
            print("No cal buscar")
            continue
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, prof=14)
        #print(articles)
        print(len(articles))
        posar=set(nascutsllocwd[qlloc])-set(articles)
        print("Posar (provisionalment):", posar, len(posar))
        if len(posar)>0:
            art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=14)
            print(len(articles))
            posar=set(nascutsllocwd[qlloc])-set(articles)
            print("Posar (definitivament):", posar, len(posar))
            if len(diccat)>lencats:
                lencats=len(diccat)
                desadicc(diccatvell)
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

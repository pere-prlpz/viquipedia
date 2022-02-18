#-*- coding: utf-8 -*-

# Programa per posar les categories d'estudiants per centre educatiu
# per crear categories d'estudiants per universitat (fa una cosa o l'altra).
# Arguments:
# -noeditis No edita. Només dóna informació de les categories que falten.
# -disc No fa una query sinó que agafa els resultats del disc
# -discvp No llegeix la viquipèdia sinó el disc (per decidir què ha d'editar)
# -creacat Crea categories en comptes de categoritzar articles
# -max Nombre de categories que crea com a màxim
# Exemple:
# Per donar informació:
# python universitats.py -noeditis
# Per categoritzar articles:
# python universitats.py
# Per crear 10 categories (excloses les que no tinguin P31 a Wikidata).
# A més de crear les categories, dona instruccions per enllaçar-les
# amb quickstatements (no ho fa el bot sol):
# python universitats.py -creacat -max 10

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
    return sparql.query().convert()

def get_wd(desa=True):
    print("Carregant articles i categories de Wikidata")
    query="""# articles i categories d'estudiants i universitats
    SELECT DISTINCT ?persona ?uni ?article ?cat ?categoria
    WHERE {
      ?persona wdt:P69 ?uni.
      ?article schema:about ?persona.
      ?article schema:isPartOf <https://ca.wikipedia.org/>.
      OPTIONAL {
        ?uni wdt:P3876 ?cat.
        ?categoria schema:about ?cat.
        ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
      }
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    uniwd = results["results"]["bindings"]
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\estunibrut.pkl"
        pickle.dump(uniwd, open(fitxer, "wb")) 
    return (uniwd)

def carrega_wd(desa=True, disc=False):
    if disc:
        print("llegint dades del disc")
        unibrut=pickle.load(open(r"C:\Users\Pere\Documents\perebot\estunibrut.pkl", "rb"))
    else:
        unibrut=get_wd(desa)
    return(unibrut)

def classifica(res, desa=True):
    print ("Agrupant articles per universitat")
    dicsi={}
    dicno={}
    for registre in res:
        article = registre["article"]["value"].replace("https://ca.wikipedia.org/wiki/", "")
        article = urllib.parse.unquote(article).replace("_"," ")
        if "categoria" in registre.keys():
            cat = registre["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/", "")
            cat = urllib.parse.unquote(cat).replace("_"," ")
            if cat not in dicsi.keys():
                print(cat)
                dicsi[cat]=[]
            dicsi[cat].append(article)
        else:
            uni = registre["uni"]["value"]
            if uni in dicno.keys():
                dicno[uni] = dicno[uni]+1
            else:
                dicno[uni] = 1
    if desa:
        fitxer = r"C:\Users\Pere\Documents\perebot\estuni.pkl"
        pickle.dump((dicsi,dicno), open(fitxer, "wb")) 
    return(dicsi, dicno)

def artcat(catnom, site=pwb.Site('ca')):
    # llista d'articles d'una categoria
    cat = pwb.Category(site,catnom)
    articles = pagegenerators.CategorizedPageGenerator(cat, recurse=5)
    llistart = []
    for art in articles:
        llistart.append(art.title())
    return(llistart)

def artcats(catnoms, desa=True, disc= False, site=pwb.Site('ca')):
    # diccionari amb llistes d'articles d'una llista de categories
    if disc:
        print("llegint categories del disc")
        dicc=pickle.load(open(r"C:\Users\Pere\Documents\perebot\estcats.pkl", "rb"))
    else:   
        print ("llegint categories")
        dicc = {}
        for cat in catnoms:
            print(cat)
            dicc[cat]=artcat(cat)
        if desa:
            fitxer = r"C:\Users\Pere\Documents\perebot\estcats.pkl"
            pickle.dump(dicc, open(fitxer, "wb")) 
    return(dicc)

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

def posacat(cat, arts, site=pwb.Site('ca')):
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
        if re.search("\[\["+cat+"\]\]", textvell):
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
        if textnou != textvell:
            sumari = "Robot posa la [["+cat+"]] a partir de Wikidata"
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
    return

def creacategories(quni, edita=True, site=pwb.Site('ca')):
    #print(quni)
    query="""# articles d'estudiants de centres educatius sense categoria per centre educatiu
    SELECT DISTINCT ?uni ?uniLabel ?cat ?catLabel ?article
    WHERE {
      VALUES ?uni {"""+" ".join(["wd:"+el for el in quni])+"""}
      ?uni wdt:P3876 ?cat.
      ?uni wdt:P31 [].
      OPTIONAL {
        ?article schema:about ?uni.
        ?article schema:isPartOf <https://ca.wikipedia.org/>.
      }     
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ca,en,es" . } 
    }"""
    endpoint_url = "https://query.wikidata.org/sparql"
    results = get_results(endpoint_url, query)
    instruccions=""
    for registre in results["results"]["bindings"]:
        article=""
        nomcat=""
        if "article" in registre.keys():
            nom = registre["article"]["value"].replace("https://ca.wikipedia.org/wiki/", "")
            nom = urllib.parse.unquote(nom).replace("_"," ")
            article=nom
            print("Nom a partir d'article:", nom)
        else:
            nom = registre["uniLabel"]["value"]
            print("Nom a partir de label:", nom)
        if re.match("^(Universitat|Facultat|Reial Acadèmia|Royal Academy|Institució)",nom):
            nomcat="Alumnes de la "+nom
        elif re.match("^(Hochschule|Sc[uh]ola|Institución?|KU|Pontifícia|HEC|Mesquita|Vrije Universiteit) ",nom):
            nomcat="Alumnes de la "+nom
        elif re.match("^(Reial (Escola|Acadèmia|Universitat)) ",nom):
            nomcat="Alumnes de la "+nom
        elif re.match("^(Queen's|Presidency) (University)",nom):
            nomcat="Alumnes de la "+nom
        elif re.match("^(Escola|Institut|ETH|Acadèmia|Accademia|École) ", nom):
            nomcat="Alumnes de l'"+nom
        elif re.match("^(Reial )?(Conservat(ori|oire)|L[iy]cé?eu?|Col·legi|Coll[èe]ge) ", nom):
            nomcat="Alumnes del "+nom
        elif re.match("^(Seminari|Cos) ", nom):
            nomcat="Alumnes del "+nom
        elif re.match("^(Centre|Prytanée|Cours|Pontifici|Colegio|Politècnic|Programa) ", nom):
            nomcat="Alumnes del "+nom
        elif re.match("^[AEIOUÈÉaeiou]", nom):
            nomcat="Alumnes de l'"+nom
        elif re.match("^(The|Det) ", nom):
            nomcat="Alumnes de "+nom
        elif re.match(".*(Hall|Studio|Institute|Hospital)$", nom):
            nomcat="Alumnes del "+nom
        elif re.match(".*(School|Academy|Union)$", nom):
            nomcat="Alumnes de la "+nom
        elif re.match(".*(College|Institut|Conservator[iy]|Studio|Center|Gymnasium)", nom):
            nomcat="Alumnes del "+nom
        elif re.match(".*(School|[Aa][ck]ademie|Academy|[Ss]chule)", nom):
            nomcat="Alumnes de la "+nom
        elif nom  in ["Bauhaus", "Peterhouse", "Konstfack"]:
            nomcat="Alumnes de la "+nom
        elif nom  in ["Mozarteum", "Johanneum"]:
            nomcat="Alumnes del "+nom
        elif nom  in ["Goldsmiths", "Hogwarts"]:
            nomcat="Alumnes de "+nom
        else:
            print("NO PUC CONFEGIR EL NOM DE LA CATEGORIA:", nom)
            continue
        print(nomcat)
        if article != "":
            nomel = nomcat.replace("Alumnes de l'","l'")
            nomel = nomel.replace("Alumnes de la","la")
            nomel = nomel.replace("Alumnes de ","")
            nomel = nomel.replace("Alumnes d","")
            infocat="{{infocat|"+nom+"|"+nomel+"}}\n"
        else:
            infocat=""
        ordena = re.sub("^Universitat","", nom)
        ordena = re.sub("^ ?(de |del |dels |d')","", ordena)
        ordena = re.sub("^ ?(el |la |l')","", ordena)
        ordena = re.sub("^ ","", ordena) 
        ordena = ordena.replace("É","E")
        text = infocat + "[[Categoria:Alumnes per centre educatiu|"+ordena+"]]\n"
        qcat = registre["cat"]["value"].replace("http://www.wikidata.org/entity/","")
        instruccio = qcat + '|Scawiki|"Categoria:'+nomcat+'"||'
        print(text)
        print(instruccio)
        if edita:
            pag=pwb.Page(site, "Categoria:"+nomcat)
            if pag.exists():
                print("Ja existeix la categoria", pag)
            else:
                pag.put(text, "Robot crea categoria a partir de Wikidata")
        instruccions = instruccions + instruccio
    print("Instruccions pel quickstatements:")
    print(instruccions)
    return

# el programa comença aquí
disc=False
discvp=False
desa=True
edita=True
editacat=True
creacat=False
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
    if "-max" in arguments:
        imax=arguments.index("-max")
        if len(arguments)>imax:
            maxcats=int(arguments.pop(imax+1))
        arguments.remove("-max")
    else:
        maxcats=4
estuniwdbrut = carrega_wd(desa=desa, disc=disc)
unisi, unino = classifica(estuniwdbrut, desa=True)
#print(unisi[list(unisi)[1]])
print ("Informació: categories per crear")
tunino = []
qunino = []
for uni in unino.keys():
    if unino[uni]>=5:
        print(uni, unino[uni])
        tunino.append((unino[uni],uni.replace("http://www.wikidata.org/entity/Q","")))
tunino = sorted(tunino, reverse=True)
#print(tunino)
textunino = "Centres educatius que apareixen a {{P|69}} de persones amb article "
textunino = textunino + "però sense categoria a la Viquipèdia, i nombre "
textunino = textunino + "d'articles que hi anirien si existís.\n\n"
textunino = textunino + "No tots són categories a crear.\n\n"
totalunino = 0
for tuni in tunino:
    textunino = textunino + "# {{Q|"+tuni[1]+"}}:"+str(tuni[0])+"\n"
    #print("* {{Q|"+tuni[1]+"}}", tuni[0]) 
    qunino.append("Q"+tuni[1])
    totalunino = totalunino+tuni[0]
print ("Total", totalunino)
textunino = "\n"+textunino + "Total: "+str(totalunino)+"\n\n"
if edita or creacat:
    pag = pwb.Page(pwb.Site('ca'), "Usuari:PereBot/centres educatius")
    pag.put(textunino, "Robot actualitza centres educatius sense categoria")
if creacat:
    creacategories(qunino[1:(min(maxcats, len(qunino)))], editacat)
    exit(0)
# A partir d'aquí només per omplir categories
try:
    diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
except FileNotFoundError:
    print ("Fitxer de categories no trobat. Començant de nou.")
    diccatvell={}
diccat={}
lencats = 0
#uniwp = artcats(list(unisi), disc=discvp, desa=True)
#print(uniwp[list(uniwp)[1]])
total = 0
tots= set([])
icat = 0
ncats = len(unisi)
for cat in unisi:
    print(icat,"/", ncats, cat)
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=True, prof=5)
    #print(articles)
    print(len(articles))
    posar = set(unisi[cat])-set(articles)
    print("Posar (provisionalment):", posar, len(posar))
    if len(diccat)>lencats:
        lencats=len(diccat)
        desadicc(diccatvell)
    if len(posar)>0:
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=5)
        #print(articles)
        print(len(articles))
        posar = set(unisi[cat])-set(articles)
        print("Posar (definitivament):", posar, len(posar))
        if len(diccat)>lencats:
            lencats=len(diccat)
            desadicc(diccatvell)
        total=total+len(posar)
        #print(posar)
        tots=tots|posar
        if edita:
            posacat(cat, posar)
            diccat[cat]["art0"].extend(posar)
            diccatvell[cat]["art0"].extend(posar)        
print("Total:",total)
print("Diferents:", len(tots))

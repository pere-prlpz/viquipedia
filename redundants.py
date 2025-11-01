#-*- coding: utf-8 -*-

# programa per treu categories redundants
import sys
import re
import pickle
from SPARQLWrapper import SPARQLWrapper, JSON
import pywikibot as pwb
from pywikibot import pagegenerators
import urllib
import urllib.request
from urllib.parse import unquote

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
            print("No passa:",cat)
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

def desadicc(diccatvell, diccatnou=[1], lendic=0):
    if len(diccatnou)>lendic:
        fitxer = r"C:\Users\Pere\Documents\perebot\categories.pkl"
        pickle.dump(diccatvell, open(fitxer, "wb")) 
        lennou = len(diccatnou)
        print("Diccionari vell desat. Diccionari:",lennou,"Diccionari vell:", len(diccatvell))
        return (lennou)
    else:
        return(lendic)


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
    comandes = comandes.replace("||","|")  # pegat. No hi hauria d'haver cap || per començar.
    with open(nqcat, "a", encoding='utf-8') as f:
        f.write(comandes)
        f.close()

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


def catprals():
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
    cat1orgintergov = get_query("""# categories principals d'una organització intergovernamental
    SELECT ?item ?cat ?categoria WHERE {
      ?item wdt:P31 wd:Q245065.
      ?item wdt:P910 ?cat.
      ?categoria schema:about ?cat.
      ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }""")
    cat1org = get_query("""# categories principals d'una organització 
    SELECT ?item ?cat ?categoria WHERE {
      ?item wdt:P31 wd:Q43229.
      ?item wdt:P910 ?cat.
      ?categoria schema:about ?cat.
      ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }""")
    cat1grupmus = get_query("""# categories principals d'un grup de música
    SELECT ?item ?cat ?categoria WHERE {
      ?item wdt:P31 wd:Q215380.
      ?item wdt:P910 ?cat.
      ?categoria schema:about ?cat.
      ?categoria schema:isPartOf <https://ca.wikipedia.org/>.
    }""")
    cat1pers = [urllib.parse.unquote(x["categoria"]["value"].replace("https://ca.wikipedia.org/wiki/","")).replace("_"," ")
                for x in (cat1perswd+cat1perswdbib+cat1orgintergov+cat1org+cat1grupmus)]
    #print(cat1pers)
    print("cat1pers", len(cat1pers))
    return (cat1pers)




# el programa comença aquí
# arguments que podrien anar com a arguments
arguments = sys.argv[1:]
actualitza = False
if len(arguments)>0:
    if "-act" in arguments:
        actualitza=True
        arguments.remove("-act")
if len(arguments)>0:
    titrel="Categoria:"+(" ".join(arguments))  
else:
    print("Manca el nom de la llista de monuments. Agafem opció per defecte")
    titrel = "Categoria:Científics socials"
profcat = 3 # fins on buscar categories pre treure
profart = 4 # fins on buscar articles amb categories redundants
qcat = True # True escriure en fitxer, False editar directament
#
nqcat = r"C:\Users\Pere\Documents\perebot\qcatredundants.txt"
catprals = catprals()
# inicialitzar miracats
diccat, diccatvell, lencats = inicialitzadicc()

noincregex="Esborrany"
nomirarregex=" per "
#
art0, cat0, diccat, diccatvell, articles, cat1=miracat(titrel, dicc=diccat, diccvell=diccatvell, vell=False, prof=profcat, noincregex=noincregex, noinc=catprals)
print(cat1, len(cat1))
cat1.add(titrel)
if (len(noincregex)>0):
    cat1 = [x for x in cat1 if not re.search(noincregex,x) and not x in catprals]
print(cat1, len(cat1))
for catred in cat1: # cat1 és la categoria que comprovarem si és redundant 
    print(catred)
    if re.search(noincregex,catred) or re.search(nomirarregex, catred) :
        print("No mirem", catred)
        continue
    art0, cat0, diccat, diccatvell, articles, cat1=miracat(catred, dicc=diccat, diccvell=diccatvell, vell=False, prof=0, noincregex=noincregex, noinc=catprals)
    artsup = art0
    #print(art0)
    print(cat0)
    for cat in cat0:
        print("Mirant", cat, "redundant amb", catred)
        if re.search(noincregex,cat) or  cat in catprals:
            print("No mirem", cat)
            continue
        art0, cat0, diccat, diccatvell, articles, cat1=miracat(cat, dicc=diccat, diccvell=diccatvell, vell=False, prof=profart, verbose=True, noincregex=noincregex, noinc=catprals)
        artinf = articles
        artredundants = set(artsup).intersection(set(artinf))
        print("Redundants:", artredundants)
        if len(artredundants)>0:
            if qcat:
                posaqcats([], catsno = [catred], arts=artredundants, nqcat=nqcat)
            else:
                print("Editant per:", [], [catred], artredundants) 
                posacats([], catsno = [catred], arts=artredundants)
        if actualitza:
            lencats=desadicc(diccatvell, diccat, lencats)
if actualitza:
    lencats=desadicc(diccatvell, diccat, lencats)

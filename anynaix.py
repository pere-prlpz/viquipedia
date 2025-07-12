#-*- coding: utf-8 -*-

# programa per posar categories per any de naixement
import sys
import requests
import json
import re
import pickle
import pywikibot as pwb
from pywikibot import pagegenerators

def llegeix_petscan(url):
    print ("llegint petscan")
    petscan = requests.get(url).json()
    table = petscan['*'][0]['a']['*']
    #print(table[0:2])
    print ("llegit petscan. recuperant títols")
    articles = [(x["title"],x["metadata"]["wikidata"]) for x in table]
    return (articles)

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

def posacats(cats, catsno=[], arts=[], site=pwb.Site('ca')):
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
        if textnou != text0 and False: # anul·lat (només per proves)
            pagprova = pwb.Page(site, "Usuari:PereBot/taller")
            sumari = "Robot copia [["+art+"]] tot fent proves"
            pagprova.put(textnou, sumari)
        sumtreu=""
        if textnou != text0:
            for catno in catsno:
                if catno == cat:
                    print(catno, "redundant amb si mateixa")
                    continue
                if re.search("\[\["+catno+"(\|.*)?\]\]", textnou):
                    print("Traient", catno)
                    textnou=re.sub("\[\["+catno+"\]\]\n?", "", textnou)
                    #textnou=re.sub("\[\["+catno+"\|.*\]\]", "", textnou)
                    sumtreu=" i treu la [["+catno+"]] redundant"
            textcats = " ".join(["[["+cat+"]]" for cat in cats])
            sumari = "Robot posa "+textcats+" a partir de Wikidata"+sumtreu
            try:
                pag.put(textnou, sumari)
            except pwb.LockedPage:
                print ("Pàgina protegida")
                continue
    return

def posaqcats(cats, catsno=[], arts=[], nqcat=r"C:\Users\Pere\Documents\perebot\qcat.txt"): # catsno no implementat
    cats = [re.sub("Categoria:","",cat) for cat in cats]
    tcats = "|".join(["+Category:"+cat for cat in cats])
    comandes = "\n".join([art+"|"+tcats for art in arts])+"\n"
    with open(nqcat, "a", encoding='utf-8') as f:
        f.write(comandes)
        f.close()

def infmanquen(dicc):
    inf = "=== Anys sense categoria===\n\n"
    for nany in sorted(dicc.keys()):
        inf = inf + "==== "+str(nany)+" ====\n\n"
        inf = inf + "\n".join(["# [["+x+"]]" for x in dicc[nany]])
        inf = inf + "\n\n"
    return (inf)

def desainf(continguts, paginftit="naixements", acabat=False):
    paginf = pwb.Page(pwb.Site('ca'), "Usuari:PereBot/"+paginftit)
    text = "\n\n".join(continguts)
    if acabat:
        text=text+"\n\nFeina acabada."
    else:
        text=text+"\n\nFeina en curs."
    text=text+"\n\n--~~~~"
    paginf.put(text, "Resum d'articles amb dates de naixement problemàtiques")

def claimsadata(claims):
    try:
        dates = [x.getTarget() for x in claims]
        anys = [x.year for x in dates]
        precisio = [x.precision for x in dates]
        qualificadors = [set(x.qualifiers.keys()) for x in claims]
        qualificadors = set().union(*qualificadors)
        return(anys, precisio, qualificadors)
    except AttributeError:
        return([], [], set())

# el programa comença aquí
arguments = sys.argv[1:] 
qcat = False   # fer servir quickcategories en comptes d'editar directament
if "-qcat" in arguments:
    qcat=True
    arguments.remove("-qcat")
qcnet = False   # netejar el fitxer quickcategories
if "-net" in arguments:
    qcnet=True
    arguments.remove("-net")
nqcat = r"C:\Users\Pere\Documents\perebot\qcat.txt"
if qcnet:
    with open(nqcat, "w", encoding='utf-8') as f:
        f.write("")
        f.close()
site=pwb.Site('ca')
repo = site.data_repository()
url = "https://petscan.wmcloud.org/?ores_prediction=any&manual_list=&namespace_conversion=keep&labels_any=&after=&common_wiki_other=&cb_labels_yes_l=1&output_limit=&source_combination=&active_tab=tab_wikidata&search_max_results=500&wikidata_prop_item_use=P569%2CQ5&templates_any=&langs_labels_no=&min_sitelink_count=&wpiu=all&max_age=&ores_prob_to=&search_query=&language=ca&negcats=Biografies+per+data+de+naixement&project=wikipedia&depth=12&labels_no=&sortorder=ascending&referrer_url=&outlinks_yes=&interface_language=en&search_filter=&edits%5Bflagged%5D=both&sortby=none&cb_labels_no_l=1&wikidata_source_sites=&edits%5Bbots%5D=both&ores_type=any&before=&common_wiki=auto&since_rev0=&ns%5B0%5D=1&pagepile=&categories=Biografies&larger=&format=json&langs_labels_any=&doit="
artsnaix = llegeix_petscan(url)
url = "https://petscan.wmcloud.org/?links_to_no=&max_sitelink_count=&cb_labels_yes_l=1&edits%5Bflagged%5D=both&labels_no=&output_compatability=catscan&subpage_filter=either&langs_labels_no=&since_rev0=&wikidata_label_language=&page_image=any&larger=&cb_labels_any_l=1&show_disambiguation_pages=both&langs_labels_any=&manual_list=&templates_no=&negcats=Biografies+per+data+de+defunci%C3%B3&search_max_results=500&wikidata_prop_item_use=P570%2CQ5&sortby=none&search_query=&ns%5B0%5D=1&sortorder=ascending&active_tab=tab_wikidata&cb_labels_no_l=1&rxp_filter=&sitelinks_no=&wikidata_item=no&project=wikipedia&categories=Biografies&links_to_any=&labels_any=&show_redirects=both&min_sitelink_count=&wpiu=all&language=ca&namespace_conversion=keep&ores_prediction=any&interface_language=en&depth=12&format=json&minlinks=&doit="
artsmort = llegeix_petscan(url)
artwds = set(artsnaix+artsmort)
print(len(artsnaix), len(artsmort), len(artwds))
#print(artwds[0:min(10,len(artwds))])
# el programa comença aquí
try:
    diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
except FileNotFoundError:
    print ("Fitxer de categories no trobat. Començant de nou.")
    diccatvell={}
icat=0
diccat={}
lencats = 0
infantics="=== Sense categoria ===\n\n"
infqualifs="=== Amb qualificadors ===\n\n"
infmultiples="=== Amb múltiples valors ===\n\n"
diccmanquen = {}
infanticsm="=== Sense categoria ===\n\n"
infqualifsm="=== Amb qualificadors ===\n\n"
infmultiplesm="=== Amb múltiples valors ===\n\n"
diccmanquenm = {}
ierrdesat = 0
iart = 0
narts = len(artwds)
for artwd in artwds:
    iart=iart+1
    print(iart,"/",narts)
    posar = []
    titol = artwd[0]
    qid = artwd[1]
    print(titol, qid)
    item = pwb.ItemPage(repo, qid)
    #print(item)
    try:
        item.get()
    except pwb.exceptions.MaxlagTimeoutError:
        print("Error maxlag")
        continue
    if item.claims:
        titnet=titol.replace("_"," ")
        # anys neixement
        if artwd in artsnaix and 'P569' in item.claims:
            print("preparem naixement")
            anys, precisions, qualificadors = claimsadata(item.claims['P569'])
            print(anys, precisions, qualificadors)
            if len(set(anys))>1:
                print("dates diferents", anys) 
                infmultiples = infmultiples + "# [["+titol+"]] "+str(anys)+"\n"
                ierrdesat = ierrdesat+1
            elif len(set(anys))==0:
                print("sense data o valor desconegut")
            elif min(precisions) < 9:
                print("Data imprecisa", precisions)
            elif len(qualificadors-{"P31","P7452"})>0:
                print("Té qualificadors")
                print(qualificadors)
                infqualifs = infqualifs + "# [["+titol+"]] "+str(qualificadors)+"\n"
                ierrdesat = ierrdesat+1
            elif anys[0] < 1300 and anys[0] not in [ 1283, 1273, 1259, 1215]:
                nany = anys[0]
                print("Massa antic per tenir categoria", ierrdesat)
                if nany in diccmanquen:
                    diccmanquen[nany].append(titnet)
                else:
                    diccmanquen[nany] = [titnet]
                ierrdesat = ierrdesat+1
            else:
                nany = anys[0]
                print(nany)
                titcat = "Categoria:Naixements del "+str(nany)
                print(titcat)
                art0, cat0, diccat, diccatvell, articles, cat1=miracat(titcat, dicc=diccat, diccvell=diccatvell, vell=True, prof=3)
                #print(art0)
                #print(articles)
                if titnet in articles:
                    print("Ja hi és")
                    continue
                else:
                    print("Provisionalment, no hi és")
                    art0, cat0, diccat, diccatvell, articles, cat1=miracat(titcat, dicc=diccat, diccvell=diccatvell, vell=False, prof=3)
                    if titnet in articles:
                        print("Però reament sí que hi és")
                        continue
                    else:
                        print("posar", titnet, "a", titcat)
                        posar.append(titcat)
        # anys defunció
        if artwd in artsmort and 'P570' in item.claims:
            print("preparem defunció")
            anys, precisions, qualificadors = claimsadata(item.claims['P570'])
            print(anys, precisions, qualificadors)
            if len(set(anys))>1:
                print("dates diferents", anys, ierrdesat) 
                infmultiplesm = infmultiples + "# [["+titol+"]] "+str(anys)+"\n"
                ierrdesat = ierrdesat+1
            elif len(set(anys))==0:
                print("sense data o valor desconegut")
            elif min(precisions) < 9:
                print("Data imprecisa", precisions)
            elif len(qualificadors-{"P31","P7452"})>0:
                print("Té qualificadors")
                print(qualificadors)
                infqualifsm = infqualifs + "# [["+titol+"]] "+str(qualificadors)+"\n"
                ierrdesat = ierrdesat+1
            elif anys[0] < 1345:
                nany = anys[0]
                print("Massa antic per tenir categoria", ierrdesat)
                if nany in diccmanquenm:
                    diccmanquenm[nany].append(titnet)
                else:
                    diccmanquenm[nany] = [titnet]
                ierrdesat = ierrdesat+1
            else:
                nany = anys[0]
                print(nany)
                titcat = "Categoria:Morts el "+str(nany)
                print(titcat)
                art0, cat0, diccat, diccatvell, articles, cat1=miracat(titcat, dicc=diccat, diccvell=diccatvell, vell=True, prof=3)
                #print(art0)
                #print(articles)
                if titnet in articles:
                    print("Ja hi és")
                    continue
                else:
                    print("Provisionalment, no hi és")
                    art0, cat0, diccat, diccatvell, articles, cat1=miracat(titcat, dicc=diccat, diccvell=diccatvell, vell=False, prof=3)
                    if titnet in articles:
                        print("Però reament sí que hi és")
                        continue
                    else:
                        print("posar", titnet, "a", titcat)
                        posar.append(titcat)
    if len(posar)>0:
        if qcat:
            posaqcats(posar,  arts=[titnet], nqcat=nqcat)
        else:
            posacats(posar, arts=[titnet])
    if ierrdesat>40:
        print("Desem informe d'errors")
        desainf(["== Naixements ==\n\n",infmanquen(diccmanquen), infqualifs, infmultiples,"== Defuncions ==\n\n",infmanquen(diccmanquenm), infqualifsm, infmultiplesm], acabat=False)
        ierrdesat=0
    if len(diccat)>lencats:
        lencats=len(diccat)
        desadicc(diccatvell)
desainf(["== Naixements ==\n\n",infmanquen(diccmanquen), infqualifs, infmultiples,"== Defuncions ==\n\n",infmanquen(diccmanquenm), infqualifsm, infmultiplesm], acabat=True)



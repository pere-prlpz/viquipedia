#-*- coding: utf-8 -*-

# programa per posar la plantilla bases de dades taxonòmiques
import requests
import json
import pywikibot as pwb
import re

def llegeix_petscan(url):
    print ("llegint petscan")
    petscan = requests.get(url).json()
    table = petscan['*'][0]['a']['*']
    print ("llegit petscan. recuperant títols")
    articles = [x["title"] for x in table]
    return (articles)

def plant(tit, site=pwb.Site('ca')):
    return pwb.Page(site,u"Plantilla:{}".format(tit))

# Funció que insereix la plantilla Autoritat (o un altre text) en una pàgina.
# Mira de posar-la davant de la plantilla Esborrarny o les categories.
# Els arguments són la pàgina i el text a afegir (habitualment la plantilla amb
# el seus paràmetres).
# Retorna el text amb la plantilla (o sense, si no ha trobat on posar-la).
# És una adaptació de la del programa ccat monuments (l'argument és l'objecte pàgina i no el text).
#
def insertaut(page,afegit="{{Autoritat}}"):
    if page.isRedirectPage():
        page=page.getRedirectTarget()
    text=page.get()
    if re.search(u"\{\{ ?[Bb]ases de dades taxonòmiques",text):
        if afegit=="{{Bases de dades taxonòmiques}}":
            print ("BDT ja hi és")
        else:
            text=re.sub(u"\{\{ ?[Bb]ases de dades taxonòmiques",afegit+u"\n{{Bases de dades taxonòmiques",text)
            print (afegit,u"afegit davant de la plantilla Bases de dades taxonòmiques")
    if re.search(u"\{\{ ?[Aa]utoritat",text):
        if afegit=="{{Autortat}}":
            print ("Autortat ja hi és")
        else:
            text=re.sub(u"\{\{ ?[Aa]utoritat",afegit+u"\n{{Autoritat",text)
            print (afegit,u"afegit davant de la plantilla Autoritat")
#    elif re.search(u"\{\{[Ee]sborrany",text):
#        text=re.sub(u"\{\{[Ee]sborrany",afegit+u"\n{{Esborrany",text,count=1)
#        print (afegit,u"afegit davant de la plantilla esborrany")
#    elif re.search(u"\{\{1000 Biografies",text):
#        text=re.sub(u"\{\{1000 Biografies",afegit+u"\n{{1000 Biografies",text,count=1)
#        print (afegit,u"afegit davant de la plantilla 1000 Biografies")
#    elif re.search(u"\{\{[Ee]nllaç AD",text):
#        text=re.sub(u"\{\{[Ee]nllaç AD",afegit+u"\n{{Enllaç AD",text,count=1)
#        print (afegit,u"afegit davant de la plantilla Enllaç AD")
#    elif re.search(u"\{\{[Ee]nllaç AB",text):
#        text=re.sub(u"\{\{[Ee]nllaç AB",afegit+u"\n{{Enllaç AB",text,count=1)
#        print (afegit,u"afegit davant de la plantilla Enllaç AB")
    elif re.search(u"\{\{(ORDENA|DEFAULTSORT)",text):
        text=re.sub(u"\{\{(ORDENA|DEFAULTSORT)",afegit+u"\n\n{{ORDENA",text,count=1)
        print (afegit,u"afegit davant de l'ORDENA")
    elif re.search(u"\[\[ ?[Cc]ategoria ?:",text):
        text=re.sub(u"\[\[ ?[Cc]ategoria ?:",afegit+u"\n\n[[Categoria:",text,count=1)
        print (afegit,u"afegit davant de les categories")
    else:
        print (u"No he trobat on afegir el text a [["+page.title()+u"]]")
    return text

# Endreça una mica les plantilles.
# PER FER: FER QUE POSI BÉ LES PLANTILLES QUE HAGIN QUEDAT ABANS D'ENLLAÇOS EXTERNS
def poleix(text):
    for i in range(1,10):
        text=text.replace("\n\n\n{{Autoritat}}",u"\n\n{{Autoritat}}")
        text=text.replace("{{Bases de dades taxonòmiques}}\n{{Autoritat}}","{{Autoritat}}\n{{Bases de dades taxonòmiques}}")
        text=text.replace("\n\n\n{{Bases de dades taxonòmiques}}","\n\n{{Bases de dades taxonòmiques}}")
        text=text.replace("\n\n{{Commonscat",u"\n{{Commonscat")
        text=text.replace("\n\n{{Projectes germans",u"\n{{Projectes germans")
        text=re.sub("(\{\{ORDENA\:.*\}\}|\{\{Enllaç A[BD]\|.*\}\})\n*(\{\{Bases de dades taxonòmiques\}\}|\{\{Autoritat\}\})",r"\2\n\1",text)
        text=re.sub("(\{\{[Cc]al coor\}\}|\{\{[Cc]al coor\|.*?\}\})\n*(\{\{Bases de dades taxonòmiques\}\}|\{\{Autoritat\}\})",r"\2\n\1",text)
        text=re.sub("(\[\[ ?[Cc]ategoria ?\:.*\|?.*?\]\])\n*(\{\{Bases de dades taxonòmiques\}\}|\{\{Autoritat\}\})",r"\2\n\1",text)
        text=text.replace(u"\n\n\n{{ORDENA",u"\n\n{{ORDENA")
    text=text.replace(u"{{Autoritat}}\n{{ORDENA",u"{{Autoritat}}\n\n{{ORDENA")
    text=text.replace(u"{{Autoritat}}\n[[Categoria:",u"{{Autoritat}}\n\n[[Categoria:")
    text=text.replace(u"{{Bases de dades taxonòmiques}}\n{{ORDENA",u"{{Bases de dades taxonòmiques}}\n\n{{ORDENA")
    text=text.replace(u"{{Bases de dades taxonòmiques}}\n[[Categoria:",u"{{Bases de dades taxonòmiques}}\n\n[[Categoria:")
    text=re.sub(u"\{\{ ?citar web ?\|",u"{{ref-web|",text)
    return text

def posaplantilles(titol, site=pwb.Site('ca')):
    pag=pwb.Page(site,titol)
    print(pag)
    if pag.namespace()==10:
        print (u"Plantilla. No editar.")
        return()
    try:
        textvell=pag.get()
    except pwb.exceptions.IsRedirectPageError:
        print ("Pàgina redirigida")
        return()
    plantilles=pag.templates()
    sumari=u""
    germans=False
    # Comença la part de posar plantilla BDT
    if pag.namespace()!=14 and ((not plant(u'Bases de dades taxonòmiques') in plantilles) and (not plant(u"Registre d'autoritats") in plantilles) and (not plant(u"Authority control") in plantilles)):
        textnou=insertaut(pag,"{{Bases de dades taxonòmiques}}")
        sumari = "Robot posa la plantilla Bases de dades taxonòmiques"
    else:
        #print u"O ja hi ha la plantilla BDT o no hi ha cap BDT a Wikidata"
        textnou=textvell
      # Tot incorporat. Poleix i desa.
    if textnou!=textvell:
        textnou=poleix(textnou)
        if sumari=="":
            sumari="Robot endreça plantilles"
        try:
            pag.put(textnou,sumari)
        except urllib2.HTTPError:
            print ("Error HTTP en desar (no deu funcionar el web)")
        except pwb.LockedPage:
            print ("Pàgina protegida")
    return()

#el programa comença aquí
# versió categoria principal i taxocaixa (compte:falta actualitzar propietats)
depth = 20 # depth baix per proves
url1 = "https://petscan.wmflabs.org/?show_redirects=no&pagepile=&outlinks_any=&smaller=&wikidata_prop_item_use=P1348%2CP4024%2CP7905%2CP2036%2CP3594%2CP2026%2CP5036%2CP3606%2CP838%2CP6070%2CP687%2CP1939%2CP3444%2CP830%2CP1895%2CP938%2CP5179%2CP1747%2CP846%2CP6433%2CP1421%2CP3099%2CP1076%2CP1391%2CP3151%2CP961%2CP815%2CP627%2CP959%2CP962%2CP685%2CP6754%2CP842%2CP1070%2CP1772%2CP2040%2CP7066%2CP960%2CP4728%2CP1772%2CP1745%2CP4664%2CP850%2CP3288%2CP2426%2CP1746&output_compatability=catscan&labels_yes=&cb_labels_no_l=1&show_soft_redirects=both&sortorder=ascending&templates_any=Infotaula+%C3%A9sser+viu%0D%0AIEV&categories=Principal&cb_labels_any_l=1&language=ca&edits%5Bbots%5D=both&rxp_filter=&interface_language=en&labels_no=&psid=26784760&edits%5Banons%5D=both&common_wiki=auto&sitelinks_no=&subpage_filter=either&active_tab=tab_templates_n_links&max_age=&links_to_all=&source_combination=&namespace_conversion=keep&depth="
url2 = "&templates_no=Bases+de+dades+taxon%C3%B2miques%0D%0ABDT&wikidata_label_language=&search_filter=&ores_prediction=any&sortby=none&ns%5B0%5D=1&langs_labels_any=&manual_list=&min_sitelink_count=&project=wikipedia&before=&larger=&wikidata_source_sites=&cb_labels_yes_l=1&search_max_results=500&doit=&format=json"
# versió arbre de la vida
depth = 35 # depth baix per proves
url1 = "https://petscan.wmflabs.org/?show_redirects=no&search_query=&ns%5B0%5D=1&active_tab=tab_wikidata&edits%5Bbots%5D=both&edits%5Bflagged%5D=both&depth="
url2 = "&categories=Arbre%20de%20la%20vida&cb_labels_no_l=1&wikidata_prop_item_use=P7715,P9157,P5037,P6098,P10585,P1348,P4024,P7905,P2036,P3594,P2026,P5036,P3606,P838,P6070,P687,P1939,P3444,P830,P1895,P938,P5179,P1747,P846,P6433,P1421,P3099,P1076,P1391,P3151,P961,P815,P627,P959,P962,P685,P6754,P842,P1070,P1772,P2040,P7066,P960,P4728,P1772,P1745,P4664,P850,P3288,P2426,P1746,P12560&edits%5Banons%5D=both&search_max_results=500&project=wikipedia&templates_no=Bases%20de%20dades%20taxon%C3%B2miques&interface_language=en&language=ca&cb_labels_any_l=1&cb_labels_yes_l=1&negcats=&format=json&langs_labels_any=&doit="
url=url1+str(depth)+url2
titols = llegeix_petscan(url)
print(titols[0:min(10,len(titols))])
#print(titols[-10:-1])
print(len(titols))
total=len(titols)
compta=0
for art in titols:
    compta=compta+1
    print(compta,"/",total)
    posaplantilles(art)
print("ja està")

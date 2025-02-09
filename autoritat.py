#-*- coding: utf-8 -*-

# programa per posar la plantilla autoritat
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
        text=re.sub(u"\{\{ ?[Bb]ases de dades taxonòmiques",afegit+u"\n{{Bases de dades taxonòmiques",text)
        print (afegit,u"afegit davant de la plantilla Bases de dades taxonòmiques")
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
        text=text.replace("\}\}\n\n{{Autoritat}}",u"\}\}\n{{Autoritat}}")
        text=text.replace("\n\n\n{{Autoritat}}",u"\n\n{{Autoritat}}")
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
    # Comença la part de posar plantilla Autoritat
    if pag.namespace()!=14 and ((not plant(u'Autoritat') in plantilles) and (not plant(u"Registre d'autoritats") in plantilles) and (not plant(u"Authority control") in plantilles)):
        textnou=insertaut(pag,"{{Autoritat}}")
        sumari = "Robot posa la plantilla autoritat"
    else:
        #print u"O ja hi ha la plantilla Autoritat o no hi ha cap autoritat a Wikidata"
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
depth = 30 # depth baix per proves
url1 = "https://petscan.wmflabs.org/?links_to_all=&project=wikipedia&templates_no=Autoritat&edits%5Banons%5D=both&cb_labels_no_l=1&edits%5Bbots%5D=both&search_max_results=500&ns%5B0%5D=1&cb_labels_yes_l=1&categories=Principal&interface_language=en&larger=70&active_tab=tab_pageprops&language=ca&depth="
url2 = "&cb_labels_any_l=1&edits%5Bflagged%5D=both&wikidata_prop_item_use=P1296,P5513,P6412,P902,P886,P7872,P7357,P2498,P12385&format=json&langs_labels_any=&doit="
# Europeana ,P7704 no inclòs perquè hi ha registres buits
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

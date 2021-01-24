#-*- coding: utf-8 -*-


# programa per posar la plantilla autoritat
import requests
import json
import pywikibot as pwb
import re
import urllib

def llegeix_petscan(url):
    print ("llegint petscan")
    petscan = requests.get(url).json()
    table = petscan['*'][0]['a']['*']
    print ("llegit petscan. recuperant títols")
    articles = [x["title"] for x in table]
    return (articles)

def plant(tit, site=pwb.Site('ca')):
    return pwb.Page(site,u"Plantilla:{}".format(tit))

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

def treu_cal_coor(titol, site=pwb.Site('ca')):
    pag=pwb.Page(site,titol)
    print(pag)
    if pag.namespace()==10:
        print (u"Plantilla. No editar.")
        return()
    try:
        textvell=pag.get()
    except pwb.IsRedirectPage:
        print ("Pàgina redirigida")
        return()
    plantilles=pag.templates()
    sumari=u""
    if (plant("indret") in plantilles or plant("infotaula geografia política") in plantilles or 
        plant("infotaula edifici") in plantilles):
        #print("Té infotaula")
        if (plant("cal coor") in plantilles or plant("cal coor cat") in plantilles 
            or plant("cal coor cat nord") in plantilles 
            or plant("cal coor val") in plantilles or plant("cal coor franja") in plantilles
            or plant("cal coor bal") in plantilles or plant("cal coor esp") in plantilles 
            or plant("cal coor País Basc") in plantilles
            or plant("cal coor Irlanda") in plantilles or plant("cal coor França") in plantilles
            or plant("cal coor Àsia") in plantilles or plant("cal coor Grècia") in plantilles
            or plant("cal coor Egipte") in plantilles or plant("cal coor Àfrica") in plantilles):
            text=pag.get()
            textnou=re.sub(u"\{\{ ?[Cc]al coord?( (cat( nord)?|val|bal|franja|esp|França|Irlanda|Egipte|À(fric|si)a|Grècia|País Basc))?(\|type=(mountain|river|waterbody|city|landmark|country|adm(1st|2nd)|forest|event|isle|pass|canal))?(\|region=..)?\}\}\n?","",text)
            if textnou != text:
                sumari="robot treu plantilla cal coor redundant amb la infotaula"
                textnou=poleix(textnou)
                try:
                    pag.put(textnou,sumari)
                except urllib.HTTPError:
                    print ("Error HTTP en desar (no deu funcionar el web)")
                except pwb.LockedPage:
                    print ("Pàgina protegida")
            else:
                print("Sense canvis")
        else:
            print("No trobada la plantilla cal coor")
    else:
        print("No trobada la infotaula")
    return()

urls=[]
urls.append("https://petscan.wmflabs.org/?psid=18280562&format=json") #indret
urls.append("https://petscan.wmflabs.org/?psid=18280565&format=json") #infotaula geografia política
urls.append("https://petscan.wmflabs.org/?psid=18280568&format=json") #infotaula edifici
print (urls)
for url in urls:
    titols = llegeix_petscan(url)
    print(titols[0:min(10,len(titols))])
    #print(titols[-10:-1])
    print(len(titols))
    total=len(titols)
    compta=0
    for art in titols:
        compta=compta+1
        print(compta,"/",total)
        treu_cal_coor(art)
    print("ja està")


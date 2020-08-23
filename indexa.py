# -*- coding: utf-8 -*-
# Robot indexa categories.
# Fa servir dos paràmetres:
# - Nom de la categoria
# - Part del títol dels articles que s'ha de treure:
#    - no hi inclogueu "de", "del" i variants, que ja ho fa el programa tot sol
#    - pot ser una expressió regular
#    - Si no s'indica aquest paràmetre, fa servir el títol de la categoria
# Exemples:
# python indexa.py "Avingudes d'Alacant" "Avinguda"
# python indexa.py "Arxius municipals del País Valencià" "(Arxiu Municipal|Arxiu Històric Municipal)"
# python indexa.py "Eleccions del 2016" "(Eleccions ?(parlamentàries|generals|legislatives|regionals|provincials|presidencials|cantonals|federals)?( al)?)"
# python indexa.py "Pollimyrus"
# Si algun dels dos paràmetres té una sola paraula (sense espais) no calen les cometes:
# python indexa.py "Fonts de Teià" Font

import re
import sys
import pywikibot as pwb
from pywikibot import pagegenerators

def noaccents(text):
    c0="àáèéìíòóùúÀÈÌÒÙÁÉÍÓÚçÇñÑ"
    c1="aaeeiioouuAEIOUAEIOUcCnN"
    tx = text
    for i in range(len(c0)):
        tx=re.sub(c0[i], c1[i], tx)
    return (tx) 

# el programa comença aquí
site=pwb.Site('ca')
#tcat=u"Places del Baix Llobregat" #Poseu aquí la categoria a indexar
#tcats=u"Plaça" #Poseu aquí la part del títol que no forma part de l'índex (no hi inclogueu "de", "del" i variants, que ja ho fa el programa tot sol).
arguments = sys.argv[1:]
tcat = arguments[0]
if len(arguments) > 1:
    tcats = arguments[1]
else:
    tcats = tcat[:]
inicial=tcat[0]
retcat=u"["+inicial.upper()+inicial.lower()+"]"+tcat[1:]
cat = pwb.Category(site,'Category:'+tcat)
pags = pagegenerators.CategorizedPageGenerator(cat, recurse=False)
for pag in pags:
    print (pag)
    try:
        textvell=pag.get()
    except pwb.IsRedirectPage:
        print("Redirecció")
        continue
    tit=pag.title()
    ord = re.search("\{\{ORDENA:(.+?)\}\}", textvell)
    if ord:
        ordena = ord.group(1)
        print("ORDENA:", ordena)
    else:
        ordena = tit
    index=tit
    #index=re.sub("^("+tcats+") (del |de la |de l'|dels |de les )","",index)
    #index=re.sub("^("+tcats+") (de |d')","",index)
    index=re.sub("^("+tcats+") ","",index)
    index=re.sub("^(del |de la |de l'|dels |de les |d'en |de na |al |a la |als |a les |a l')","", index)
    index=re.sub("^(de |d'|a )","", index)    
    index=re.sub("^(el |la |l'|els |les )","", index)
    index0=index[:]
    index=re.sub("[·\-\)\(«»,\.\:]","",index)
    index=noaccents(index).title().strip()
    print (index)
    if index != tit and index0 != tit and index != ordena and index0 != ordena and not ordena.startswith(index) and len(index)>0:
        #index=index[0].upper()+index[1:]
        print (index)
        noutext=re.sub("\[\[ ?[Cc]ategoria: ?"+retcat+u" ?\]\]", "[[Categoria:"+tcat+u"|"+index+u"]]",textvell)
        #print ("\[\[ ?[Cc]ategoria: ?"+retcat+u" ?\]\]")
        print ("[[Categoria:"+tcat+u"|"+index+u"]]")
        if noutext != textvell:
            pag.put(noutext,u"Robot indexant l'article a la [[Categoria:"+tcat+u"]] amb l'índex '"+index+u"'")

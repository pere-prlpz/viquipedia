# -*- coding: utf-8 -*-
# Robot indexa categories.
# Fa servir dos paràmetres:
# - Nom de la categoria
# - Part del títol dels articles que s'ha de treure:
#    - no hi inclogueu "de", "del" i variants, que ja ho fa el programa tot sol
#    - pot ser una expressió regular (entre parèntesi)
# Exemples:
# python indexa.py "Avingudes d'Alacant" "Avinguda"
# python indexa.py "Arxius municipals del País Valencià" "(Arxiu Municipal|Arxiu Històric Municipal)"

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
tcats = arguments[1]
inicial=tcat[0]
retcat=u"["+inicial.upper()+inicial.lower()+"]"+tcat[1:]
cat = pwb.Category(site,'Category:'+tcat)
pags = pagegenerators.CategorizedPageGenerator(cat, recurse=False)
for pag in pags:
    print (pag)
    textvell=pag.get()
    tit=pag.title()
    index=tit
    index=re.sub("^("+tcat+"|"+tcats+u") (del |de la |de l'|dels |de les )","",index)
    index=re.sub("^("+tcat+"|"+tcats+u") (de |d')","",index)
    index=re.sub("^("+tcat+"|"+tcats+u") ","",index)
    index0=index[:]
    index=re.sub("[·-]","",index)
    index=noaccents(index).title()
    print (index)
    if index != tit and index0 != tit and len(index)>0:
        #index=index[0].upper()+index[1:]
        print (index)
        noutext=re.sub("\[\[ ?[Cc]ategoria: ?"+retcat+u" ?\]\]", "[[Categoria:"+tcat+u"|"+index+u"]]",textvell)
        #print ("\[\[ ?[Cc]ategoria: ?"+retcat+u" ?\]\]")
        print ("[[Categoria:"+tcat+u"|"+index+u"]]")
        if noutext != textvell:
            pag.put(noutext,u"Robot indexant l'article a la [[Categoria:"+tcat+u"]] amb l'índex '"+index+u"'")

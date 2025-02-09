# -*- coding: utf-8 -*-
# Arregla enllaços ambigus
# sintaxi:
# python desambigua.py tpagdes patro1 tnou1 patro2 tnou2 ... patrocap
# tpagdes: títol de la pàgina de desambiguació (amb la inicial en minúscula)
# patro1, patro2... patrons regexp per cada significat
# tnou1, tnou2... articles de destí de cada significat
# patrocap: patró regex per no fer cap canvi
# Exemple:
# python desambigua.py "creuer" "cuirassat|enfonsat|guerra|capità|blindatge|destructor|torpede|munici(ó|ons)|artilleria|calibre" "creuer (vaixell de guerra)" "església|capell(a|es)| altar|absis|romànic|gòtic" "creuer (arquitectura)" "vacances|de plaer"

import sys
import pywikibot
import re #,urllib.request, json,time
from pywikibot import pagegenerators

# El programa comença aquí.
arguments = sys.argv[1:]
tpagdes=arguments[0] # pàgina de desambiguació (canviar)
arguments = arguments[1:]
qqtext = " #QQ24"  # "" fora de la quinzena de la qualitat
site=pywikibot.Site('ca')
pagdes=pywikibot.Page(site,tpagdes)
for page in pagdes.backlinks():
    art=page
    print (page)
    # primer mira de filtrar els casos en que els enllaços ambigus són correctes
    if art.namespace() != 0:
        print (u"No espai principal")
        continue
    plants=[x.title(with_ns=False) for x in art.templates()]
    if art.isRedirectPage():
        continue
    elif u'Confusió' in plants or u'Confondre' in plants or u'Distingir' in plants:
        print (u'Confusió')
        continue
    elif u'Polisèmia' in plants or u'Nota disambigua' in plants or u'Other uses' in plants or u'Altres usos' in plants:
        print (u'Polisèmia')
        continue
    elif u'Redirecció' in plants or u'Redirect' in plants:
        print (u'Redirecció')
        continue
    elif u'Vegeu' in plants or u'Polisèmia descripció' in plants or u'Homonímia' in plants:
        print (u'Vegeu')
        continue
    elif u'Vegeu (des)' in plants or u'Vegeu (desambiguació)' in plants:
        print (u'Vegeu (des)')
        #print (plants)
        continue
    elif u'Vegeu lliure' in plants:# or u'Hatnote' in plants:
        print (u'Vegeu (des)')
        #print (plants)
        continue
    elif u'Desambigua' in plants or u'Desambiguació' in plants or u'Disambig' in plants or u'DesambiCurta' in plants or u'Acrònim' in plants or u'Onomàstica' in plants or u'Biografies' in plants:
        print (u'pàgina de desambiguació')
        continue
    elif u'Vegeu3' in plants or u'Otheruses4' in plants:
        print (u'Vegeu3 però seguim')
        #continue
    # tria si és un dels dos casos
    text0=page.get()
    text=text0
    canvis=0
    tvellm=tpagdes[0].upper()+tpagdes[1:]
    for i in range(0, int(len(arguments)/2)):
        if re.search(arguments[2*i],text):            # primer filtre (canviar)
            tnou=arguments[2*i+1]
            text=text.replace(u"[["+tpagdes+"]]",u"[["+tnou+"|"+tpagdes+"]]") # primer canvi (canviar)
            text=text.replace(u"[["+tpagdes+"|",u"[["+tnou+"|") # primer canvi (canviar)
            text=text.replace(u"[["+tvellm+"]]",u"[["+tnou+"|"+tvellm+"]]") # primer canvi (canviar)
            text=text.replace(u"[["+tvellm+"|",u"[["+tnou+"|") # primer canvi (canviar)
            canvis=canvis+1
            tres=tnou
            print("Trobat",tres)
    if len(arguments) % 2 == 1:
        if re.search(arguments[-1],text):            # filtre negatiu (canviar)
            canvis=canvis+2
            print("Trobat",arguments[-1])
    if canvis==0:
        print (u"Cap dels casos")
    elif canvis==1:
        if text != text0:
            page.put(text,u"Robot substituint enllaç ambigu a [["+tpagdes+"]] per [["+tres+"]]"+qqtext)
        else:
            print ("Trobat però canvi no efectuat. Comprovar redireccions")
    elif canvis>1:
        print (u"No es pot decidir.", canvis)


# Troba articles en categories redirigides.
# Les redireccions les treu dels links d'una pàgina.

import pywikibot as pwb
from pywikibot import pagegenerators

site = pwb.Site('ca', 'wikipedia')
pagfont = pwb.Page(site, 'Usuari:Paucabot/Red') # pàgina on hi ha els enllaços a les redireccions
cats = pagfont.linkedPages()
print(cats)
informe = ""
for cat in cats:
    #print(cat)
    if cat.isRedirectPage():
        #print("redirecció")
        if "Categoria:" in cat.title():
            print(cat.title())
            #print("és categoria")
            articles = pagegenerators.CategorizedPageGenerator(cat)
            #print(articles)
            llistart = list(articles)
            print(llistart)
            if len(llistart)>0:
                liniainf = "# [[:"+cat.title()+"]]:"
                for art in llistart:
                    liniainf = liniainf + " [[" + art.title() + "]], "
                print(liniainf)
                informe = informe+liniainf+"\n"
print(informe)
paginf = pwb.Page(site, "Usuari:PereBot/articles en categories redirigides")
informe = "--~~~~\n\n"+informe
paginf.put(informe, "actualitzant articles en categories redirigides")

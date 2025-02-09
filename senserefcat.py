#versió que es mira directamet les categories
import pywikibot as pwb
from pywikibot import pagegenerators

catnom = "Categoria:Bàsquet"
site=pwb.Site('ca')
cat = pwb.Category(site,catnom)
profunditat = 7
articles = pagegenerators.CategorizedPageGenerator(cat, recurse=profunditat)
artcat = []
for article in articles:
    artcat.append(article)
print(len(artcat))
catFR = pwb.Category(site,"Categoria:Articles sense referències")
articles = pagegenerators.CategorizedPageGenerator(catFR, recurse=profunditat)
faltaref = []
for article in articles:
    faltaref.append(article)
print(len(faltaref))
#senseref = [x for x in artcat if x in faltaref]
senseref = list(set(artcat) & set(faltaref))
senseref.sort()
print(senseref)
informe = "\n".join(["# [["+x.title()+"]]" for x in senseref])
print(informe)
informe_inici = "Pàgines de la [[:"+cat.title()+"]] (profunditat "+str(profunditat)+") amb {{tl|Falten referències}}.\n\n"
informe_final = "--~~~~"
informe = informe_inici + informe +"\n"+ informe_final
paginforme = pwb.Page(site, "Usuari:PereBot/articles sense referències")
sumari = "Robot actualitzant articles sense referències de la [[:"+cat.title()+"]] amb profunditat "+str(profunditat)+" ("+str(len(senseref))+" articles)"
paginforme.put(informe, sumari)



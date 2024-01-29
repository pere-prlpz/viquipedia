import pywikibot as pwb
from pywikibot import pagegenerators
from pywikibot import site
import re

def artcat(cat):
    pagacat = pagegenerators.CategorizedPageGenerator(cat, recurse=True)
    print("comencem a llegir")
    return([pag.title() for pag in pagacat])

def treuplant(tit, plant="{{FR\|data=.* de 2021}}", site=pwb.Site('ca')):
    pag = pwb.Page(site, tit)
    print(pag)
    text = pag.get()
    #textnou = text.replace(plant, "")
    textnou = re.sub(plant, "", text)
    textnou = re.sub("^\\n", "", textnou)
    pag.put(textnou, summary="robot treu plantilla FR posada per un altre bot")

site=pwb.Site('ca')
cat = pwb.Category(site,'Categoria:Articles sense referències des de 2021')
artfr = artcat(cat)
print(len(artfr))
i=0
ir=0
for contr in site.usercontribs(user="EVA3.0 (bot)", start=pwb.Timestamp(year=2021, month=12, day=9),  end=pwb.Timestamp(year=2021, month=1, day=1)):
    i=i+1
    titol = contr["title"]
    comentari = contr["comment"]
    #print(titol, comentari)
    #if titol in artfr:
    #    print("trobada per títol",titol, comentari)
    #if comentari == "Plantilles de referències":
    #    print("trobada per comentari",titol, comentari)
    if comentari == "Plantilles de referències" and titol in artfr:
        ir=ir+1
        print(ir,"trobada per títol i comentari",titol, comentari)
        treuplant(titol)
    if i % 500 == 0:
        print (i, contr["timestamp"])


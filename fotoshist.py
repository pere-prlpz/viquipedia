# llistar fotos històriques amb referència
import re
import pywikibot as pwb
from pywikibot import pagegenerators


site=pwb.Site('commons')
paginforme = pwb.Page(site, "User:PereBot/taller")
catnom="Category:Photographs by Josep Domènech i Sàbat"
cat = pwb.Category(site,catnom)
print(cat)
articles = pagegenerators.CategorizedPageGenerator(cat)
dicc = dict()
for article in articles:
    titolfile=article.title()
    print (titolfile)
    text = article.get()
    #print(len(text))
    inventari = re.sub("^(.*\n)*.*accession number *= ?(.*)\n(.*\n)*.*$", "\\2", text)
    print(inventari)
    titol = re.sub("^(.*\n)*.*title *= ?(.*)\n(.*\n)*.*$", "\\2", text)
    #print (titol)
    titol = titol.replace("{{ca|", "")
    titol = titol.replace("}}", "")
    print(titol)
    lloc = re.sub("^(.*\n)*.*depicted place *= ?(.*)\n(.*\n)*.*$", "\\2", text)
    print(lloc)
    lloc = re.sub("^(.*?);.*$","\\1", lloc)
    #print(lloc)
    dicc[inventari] = {"inventari":inventari, "file":titolfile, "titol":titol, "lloc":lloc}
#print(dicc)
#print(sorted(dicc))
informe = "== [[:c:"+catnom+"]]==\n\n"
informe = informe + '{| class="wikitable sortable"\n|- class="hintergrundfarbe5"\n! número!! foto!! títol!! lloc!! <small>comentari</small>\n'
for index in sorted(dicc):
    dades = dicc[index]
    informe = informe + "|-\n"
    informe = informe + "|"+dades["inventari"]+"\n"
    informe = informe + "|[["+dades["file"]+"|thumb]]\n"
    informe = informe + "|"+dades["titol"]+"\n"
    informe = informe + "|"+dades["lloc"]+"\n"
    informe = informe + "|\n"
informe = informe +"|-\n|}\n"
informe = informe +"--~~~~\n\n"
print(informe)
sumari = "Robot llista imatges de [[:c:"+catnom+"]]"
paginforme.put(informe, summary=sumari)

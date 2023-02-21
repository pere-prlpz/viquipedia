# -*- coding: utf-8 -*-
# Actualitza Viquiprojecte:Discussions desateses/discussions

import sys
import pywikibot
import re,urllib.request, json,time
from pywikibot import pagegenerators

site=pywikibot.Site('ca')
paginforme=pywikibot.Page(site,u"Viquiprojecte:Discussions desateses/discussions")
#paginforme=pywikibot.Page(site,u"Usuari:PereBot/taller") #per proves
pagweb=[]
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=1&rclimit=150&rctype=new") #últimes 150 pàgines de discussió noves
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=15&rclimit=6&rctype=new") #últimes pàgines de categoria discussió noves
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=11&rclimit=6&rctype=new") #últimes pàgines de plantilla discussió noves
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=13&rclimit=5&rctype=new") #últimes pàgines
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=101&rclimit=5&rctype=new") #últimes pàgines
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=103&rclimit=5&rctype=new") #últimes pàgines
pagweb.append("https://ca.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rcnamespace=829&rclimit=4&rctype=new") #últimes pàgines

#print(pagweb)

informe=u"Actualització: --~~~~\n\n"
informeno=u"=Discussions noves no incloses=\n\n"
#Compilació dels regex fora del loop per optimitzar
re_trad = re.compile(r"\{\{([Tt]radu[iï]t|[Cc]opiat) de.*?\}\}")
re_sta = re.compile(r"\{\{STA\|.*?\}\}")
re_usr = re.compile(r"\[\[(Usuari|\{\{ns:2\}\}).*?\]\]")
re_span1 = re.compile(r"<(span|font).*?>")
re_span2 = re.compile(r"</(span|font)>")
re_negreta = re.compile(r"'''")
re_cometes = re.compile(r"''|\n")
re_imatge = re.compile(r"--.?\[\[(File|Fitxer).*?\]\]") # imatge a la signatura

for urlweb in pagweb:
        pllista=urllib.request.urlopen(urlweb) 
        print("obert")
        try:
                pbrut=pllista.read()
        except:
                print ("error en llegir. esperant")
                time.sleep(60)
                try:
                        pbrut=pllista.read()
                except:
                        print ("error en llegir. esperant")
                        time.sleep(100)
                        try:
                                pbrut=pllista.read()
                        except:
                                print ("error en llegir. esperant")
                                time.sleep(200)
                                pbrut=pllista.read()
        jpag=json.loads(pbrut)
        #print ("jpag:",jpag)
        dpags=jpag["query"]["recentchanges"]
        #print ("dpags:",dpags)
        pags=[]
        for el in dpags:
                tit=el["title"]
                print (tit)
                pags.append(pywikibot.Page(site,tit))
        print(pags)
        for pag in pagegenerators.PreloadingGenerator(pags):
                tit=pag.title()
                linia=u"=[[{}]]=\n".format(tit)
                linia=linia+u"<small>[[:{}|Article]]</small> - ".format(pag.toggleTalkPage().title())
                linia=linia+u"<small class=\"editlink noprint plainlinks\">[{{fullurl:"+tit+u"|action=edit}} Edita la discussió]</small>\n\n"
                linia=linia+u"{{"+tit+u"}}\n\n"
                try:
                        text=pag.get()
                except pywikibot.exceptions.IsRedirectPageError:
                        linia=u"*[[{}]] (redirecció)\n".format(tit)
                        informeno=informeno+linia
                        continue
                except pywikibot.exceptions.NoPageError:
                        linia=u"*[[{}]] (esborrada)\n".format(tit)
                        informeno=informeno+linia
                        continue
                llarg0=len(text)
                textnet=re.sub(re_trad,u"",text)
                textnet=re.sub(re_sta,u"",textnet)
                textnet=re.sub(re_usr,u"",textnet)
                textnet=re.sub(re_span1,u"",textnet)
                textnet=re.sub(re_span2,u"",textnet)
                textnet=re.sub(re_negreta,u"",textnet)
                textnet=re.sub(re_cometes,u"",textnet)
                textnet=re.sub(re_imatge,u"",textnet)
                textnet=textnet.replace("{{VPBDN}}","")
                textnet=textnet.replace(u"\n","")
                llargnet=len(textnet)
                hihatrad=re.search(re_trad,text)
                if hihatrad and llargnet < 35:
                        print (tit, u"Només etiqueta")
                        linia=u"*[[{}]] (només conté l'etiqueta de còpia o traducció)\n".format(tit)
                        informeno = informeno + linia
                elif u"{{discussió arxivada}}" in text:
                        print (tit, u"Discussió arxivada")
                        linia=u"*[[{}]] (discussió arxivada)\n".format(tit)
                        informeno = informeno + linia
                elif llargnet < 10:
                        print (tit, u"Discussió curta")
                        linia=u"*[[{}]]\n".format(tit)
                        informeno = informeno + linia
                else:
                        informe = informe + linia
                print (tit,llarg0,llargnet)
informe=informe+informeno
paginforme.put(informe,u"Robot inclou discussions recents")

print(informe)
print(informeno)
print("final")
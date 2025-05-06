#adaptat de https://ca.wikipedia.org/wiki/Usuari:Rebot/Desamb

import pywikibot
from pywikibot import pagegenerators as pg
import datetime
from datetime import date
import re
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock


site = pywikibot.Site('ca', 'wikipedia')
site.login()
disambig_cat = pywikibot.Category(site, u'Categoria:Pàgines de desambiguació')
disambig_pages = pg.CategorizedPageGenerator(disambig_cat, recurse=True)
disambig_list = []

total_links = 0
counted_links = 0

lock = Lock()


def list_links(pag):
    num_links = len(list(site.pagebacklinks(pag, namespaces=0)))
    if num_links > 3: # normalment 4
        disambig_list.append((pag.title(), num_links))
    global total_links, counted_links
    with lock:
        total_links += num_links
        if total_links - counted_links >= 1000:
            counted_links += 1000
            print(total_links)


pool = ThreadPool(20)
pool.map(list_links, disambig_pages)

disambig_list.sort(key=lambda x: x[0], reverse=False) # afegit
disambig_list.sort(key=lambda x: x[1], reverse=True)

# Obtenir la pàgina wiki
page = pywikibot.Page(site, 'Viquipèdia:Enllaços incorrectes a pàgines de desambiguació')

# Actualitzar la pàgina amb la llista de pàgines de desambiguació
page.text = 'Actualització de {{data|' + str(datetime.date.today()) + '}}: ' + str(total_links) + '\n'
for title, n_links in disambig_list:
    page.text += '# [[' + title + ']]: ' + str(n_links) + ' [[Special:Whatlinkshere/' + title + '|enllaços]]\n'

# Guardar els canvis a la pàgina wiki
page.save(summary='Actualització automàtica de la llista de pàgines de desambiguació ('+str(total_links)+")")

# Actualitzar el recompte

def posa_ambigus(x):
    site = pywikibot.Site('ca', 'wikipedia')
    page = pywikibot.Page(site, 'Viquipèdia:Manteniment')
    #page = pywikibot.Page(site, 'Usuari:PereBot/taller') # per proves
    text = page.get()
    linies = re.split("\\n", text)
    i0 = [i for i in range(1, len(linies)) if "| [[Viquipèdia:Enllaços incorrectes a pàgines de desambiguació|Enllaços incorrectes a pàgines de desambiguació]]" in linies[i]]
    #print(i0)
    i0 = i0[0]
    print (linies[i0:(i0+3)])
    linies[i0+1] = "| <big>"+str(x)+"</big>"
    linies[i0+2] = "| "+str(date.today())
    print (linies[i0:(i0+3)])
    text = "\n".join(linies)
    page.put(text, "bot actualitzant el nombre d'enllaços incorrectes a pàgines de desambiguació "+str(x))
    return

posa_ambigus(total_links)

def posa_ambigus_qq(x):
    site = pywikibot.Site('ca', 'wikipedia')
    page = pywikibot.Page(site, 'Viquipèdia:Gran Quinzena Anual de la Qualitat/2024')
    #page = pywikibot.Page(site, 'Usuari:PereBot/taller') # per proves
    text = page.get()
    linies = re.split("\\n", text)
    i0 = [i for i in range(1, len(linies)) if "|[[Viquipèdia:Enllaços incorrectes a pàgines de desambiguació|Enllaços incorrectes a pàgines de desambiguació]]" in linies[i]]
    #print(i0)
    i0 = i0[0]
    print (linies[i0:(i0+6)])
    linies[i0+5] = "| "+str(x)
    print (linies[i0:(i0+6)])
    text = "\n".join(linies)
    page.put(text, "bot actualitzant el nombre d'enllaços incorrectes a pàgines de desambiguació "+str(x))
    return

posa_ambigus_qq(total_links)

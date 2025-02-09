import csv
import urllib.parse
import re
import pywikibot
import requests
import json
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock

lock = Lock()

def trobamid(titol):
    queryurl="https://commons.wikimedia.org/w/api.php?action=query&format=json&titles="+titol
    #print(queryurl)
    llegit = requests.get(queryurl).json()
    #print(llegit)
    mid = list(llegit["query"]["pages"])[0]
    if mid == "-1":
        return
    page = pywikibot.Page(site, titol)
    if page.isRedirectPage():
        #print (titol, "és una redirecció")
        return
    midlist.append(mid)
    #print(len(midlist)) 


#llegim imatges conegudes
# (baixar query de https://w.wiki/6SMR )
imquery=list()
with open("C:\\Users\\Pere\\Documents\\varis\\query.csv") as csvfile:
    lector=csv.reader(csvfile)
    for row in lector:
        titol=urllib.parse.unquote(row[-1])
        titol=re.sub("http://commons.wikimedia.org/wiki/Special:FilePath/","File:",titol)
        #print(titol)
        imquery.append(titol)
print("Conegudes segons query:",len(imquery))

# llegim últimes imatges carregades
site=pywikibot.Site("commons")
usuari=pywikibot.User(site, "Pere prlpz")
imatges=usuari.uploadedImages(total=55000)
nomeves = ["File:Bavarian Admin Districts.jpg", "File:Guadalquivir River Coria del Rio.jpg"]
nomeves = nomeves + ["File:Retrat de Felip Vé exposat cap per avall al Museu de l'Almodí de Xàtiva per haver incendiat la ciutat el 1707.jpg"]
nomeves = nomeves + ["File:Sta-eulalia.jpg", "File:Cicle de la calç.png", "File:Canigou murano.jpg","File:Trainjaune082004.jpg"]
nomeves = nomeves + ["File:Illa de Xàtiva.jpg", "File:Pyrenean Brook Salamander (Euproctus asper).jpg"]
midlist = []
imnoves = list()
for imatge in imatges:
    #print(imatge)
    #print(imatge[0])
    titol=imatge[0].title()
    if titol in nomeves or ".svg" in titol:
        print(titol, "no és meva")
        continue
    #print(titol)
    if not(titol in imquery):
        #print(titol, "no hi és")
        imnoves.append(titol)
    #else:
        #print("Ja hi és")
#print(imnoves)
print("Imatges noves:", len(imnoves))
       
# amb for       
# for titol in imnoves[:10]:
    # print (titol)
    # mid = trobamid(titol)
    # print(mid)
    
# amb Lock
pool = ThreadPool(20)
pool.map(trobamid,imnoves)

print(len(midlist), "imatges per marcar")

instrlist = []
for mid in midlist:
    instr="M"+mid+'|P170|somevalue|P2093|"Pere López Brosa"|P4174|"Pere prlpz"|P2699|'
    instr=instr+'"https://commons.wikimedia.org/wiki/User:Pere_prlpz"'
    instrlist.append(instr)
print ("||".join(instrlist))
import pickle
import re
from operator import itemgetter
import pywikibot as pwb

def inicialitzadicc():
    # carregar fitxer de categories
    try:
        diccatvell=pickle.load(open(r"C:\Users\Pere\Documents\perebot\categories.pkl", "rb"))
    except FileNotFoundError:
        print ("Fitxer de categories no trobat. Començant de nou.")
        diccatvell={}
    diccat = {}
    lencats = 0
    return(diccat, diccatvell, lencats)

#
diccat, diccatvell, lencats = inicialitzadicc()
catmides = [{"nom":x,"numarts":len(diccatvell[x]["art0"]),"numcats":len(diccatvell[x]["cat0"])} for x in diccatvell]
#print (catmides)
catord = sorted(catmides, key=itemgetter('numarts'), reverse=True)
print(catord[0:400])
linies = ["# [[:"+x["nom"]+"]]: "+str(x["numarts"])+" articles i "+str(x["numcats"])+" categories" for x in catord[0:4000]]
#print(linies)
informe = "\n".join(linies)
paginf = pwb.Page(pwb.Site('ca'), "Usuari:PereBot/taller")
paginf.put(informe, "Categories per mida")

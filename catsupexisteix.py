import pickle
import re
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
catcic = [x for x in diccatvell.keys() if re.search("Feministes",x)]
#print(catcic)
linies = ["# [[:"+x+"]]: [[:"+x.replace("Feministes","Activistes")+"]]" for x in catcic if not re.search(" en ", x)]
#print(linies)
informe = "\n".join(linies)
paginf = pwb.Page(pwb.Site('ca'), "Usuari:PereBot/taller")
paginf.put(informe, "Categories de: feministes i activistes")

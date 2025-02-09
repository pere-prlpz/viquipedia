# posa els balanços finals a la quinzena de la qualitat
import pywikibot
import re

def valor(text):
    text = text.replace("|","").strip()
    text = text.replace(".","")
    return (int(text))

site = pywikibot.Site('ca', 'wikipedia')
page = pywikibot.Page(site, 'Viquipèdia:Gran Quinzena Anual de la Qualitat/2024')
#page = pywikibot.Page(site, 'Usuari:PereBot/taller') # per proves
text = page.get()
linies = re.split("\\n", text)
print(linies)
for i in range(0, (len(linies)-1)):
    if "|-" in linies[i].strip() and not "|-" in linies[i+2].strip():
        print(linies[i+1])
        print(linies[i+3])
        print(valor(linies[i+3]))
        print(linies[i+5])
        print(valor(linies[i+5]))
        v0 = valor(linies[i+3])
        v1 = valor(linies[i+5])
        balanç = v1-v0
        print(balanç)
        if balanç > 0:
            baltext = "{{Augment negatiu}} "+str(abs(balanç))
        elif balanç < 0:
            baltext = "{{Disminució positiva}} "+str(abs(balanç))
        else:
            baltext = "{{estabilitat}}"+str(abs(balanç))
        if v1==0:
            baltext = baltext+" {{fet}}"
        print (baltext)
        linies[i+7] = "| "+baltext
textnou = "\n".join(linies)
#page = pywikibot.Page(site, 'Usuari:PereBot/taller') # per proves
page.put(textnou, "robot calculant balanços de la quinzena de la qualitat") 
        

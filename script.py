## Lukee tiedoston, jonka saa Pandocista ja sekventiaalisesti ajaa siihen regex-sääntöjä, jolla muuttaa sitä
## TIMin vaatimaan muotoon. Toistaiseksi regexien ajamisen järjestyksellä on väliä!
## Testattu toistaiseksi vain yhdellä luentomonisteella eikä regex-lausekkeiden yleisyyteen ole kiinnitetty suurta huomiota.
## Toistaiseksi vain raakile koodista, tulevaisuudessa mahdollisesti parantelen koodia.
## (C) 2025 Onni Hinkkanen


#Sisääntulotiedoston nimi
filename = "pandoc.md"
import re

#Lukee tiedoston
def readfile(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

#Kirjoittaa tiedoston
def writefile(filename, contents):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(contents)

contents = readfile(filename)
#Etsitään lauseet yms, erotellaan numerot
thmregex = r":::\s?(\{\#(.*?)\s.*\})\n?(.*)(Esimerkki|Lause|Lemma|Propositio)\s?(\d+)((.|\n)*?):::"
#etsitään kaksoispisteet, HUOM järjestys tärkeä, yo. pitää ajaa ensin
colonregex = r":::\s?.*"

#turhat viittaukset
emptyrefregex = r"\[\]\{.*\}"
# kaavojen viittaukset (toki haistelee myös ympäristöjen labelit jos sellaisia on jäänyt yli; Pandocin ei kuitenkaan pitäisi niitä jättää)
labelregex = r'(.*)\\label\{(.*)\}(\s?\\\\)?'
#aligned-ympäristöt
alignedregex = r"(\$\$\\begin\{aligned})+((.|\n)*?)(\\end\{aligned\}\$\$)+"

#tyhjä array kaavojen viitteiden nimille
labelsarr = []
#laskuri, jos nimettömiä esimerkkejä
counter = 0

# Muuttaa määritelmät, lauseet, yms oikeaan muotoon, numeroi ne automaattisesti eri laskureilla
# matchobj on regexin match-objekti, josta saadaan tarvittavat tiedot. matchobj.groups() palauttaa listan, jossa on kaikki regexin ryhmät, jotka on määritelty sulkeilla. 
# Tämän voi nähdä visuaalisesti esim. regex101.com-sivustolla.
def definitions(matchobj):

    str = "#-"+matchobj.group(1).strip()+"\n" + matchobj.group(3).strip() + matchobj.group(4).strip() + " " + '%%"' +matchobj.group(2).strip() +'"|c_('+matchobj.group(4).strip().lower() +')%%'+ matchobj.group(6).strip() 

    if (matchobj.group(2).strip() == None or matchobj.group(2).strip() == ""):
        str = "#-"+matchobj.group(1).strip()+"\n" + matchobj.group(3).strip() + matchobj.group(4).strip() + " " + '%%"' +"placeholder" + int(counter) +'"|c_('+matchobj.group(4).strip().lower() +')%%'+ matchobj.group(6).strip() 
    
    return str
    #return f"#-{matchobj.group(1).strip()}\n{matchobj.group(2).strip()}\n"

# Muuttaa kaavojen \labelit TIMin laskurimuotoon
def labels(matchobj):
    labelsarr.append(matchobj.group(2).strip())
    return matchobj.group(1).strip() + "{§"+matchobj.group(2).strip() +"§}\n"

# Lisää automaattisen kaavanumeroinnin 
def counters(matchobj):
    return '%%""|c_begin%%' + matchobj.group(2).strip() + '%%""|c_end%%'


# Etsii lauseet/lemmat/määritelmät (suomeksi) ja ajaa niille funktion definitions, joka muuttaa ne oikeaan muotoon
contents = re.sub(thmregex,definitions,contents,flags=re.MULTILINE)
# Poistaa loput kaksoispisteet
contents = re.sub(colonregex, "#-", contents)

# Poistaa turhat viittaukset
contents = re.sub(emptyrefregex, "", contents)

# \\ jälkeen new line
contents = re.sub(r"\\\\", r"\\\\\n", contents)

# muuttaa aligned-ympäristöt TIMin laskureiksi (TIMin valintojen vuoksi laskurit ympäröi aligned*-ympäristö, mutta jos kaavoilla on label, saavat ne numeroinnin alla)
contents = re.sub(alignedregex, counters, contents, flags=re.MULTILINE)

# viittaukset kaavoihin
contents = re.sub(labelregex, labels, contents)

# muutetaan kaavojen viittaukset TIMin laskureiksi
for label in labelsarr:
    contents = re.sub(r"\[.*\]\(\#" + label +"\)\{(.|\n)*?\}", r'%%"'+label+r'"|ref%%', contents)

# kirjoittaa ulostulotiedoston
writefile("output.md", contents)

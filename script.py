filename = "pandoc.md"
import re

def readfile(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def writefile(filename, contents):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(contents)

contents = readfile(filename)
#Etsitään lauseet yms, erotellaan numerot
thmregex = r":::\s?(\{\#(.*?)\s.*\})\n?(.*)(Esimerkki|Lause|Lemma|Propositio)\s?(\d+)((.|\n)*?):::"
#etsitään kaksoispisteet
colonregex = r":::\s?.*"

#turhat viittaukset
emptyrefregex = r"\[\]\{.*\}"
# kaavojen viittaukset
labelregex = r'(.*)\\label\{(.*)\}(\s?\\\\)?'
#aligned-ympäristöt EI KÄYTETÄ 
counterregex = r"(\$\$\\begin\{aligned})+((.|\n)*?)(\\end\{aligned\}\$\$)+"

#tyhjä array kaavojen viitteille
labelsarr = []
#laskuri, jos nimettömiä esimerkkejä
counter = 0

## Muuttaa määritelmät, lauseet, yms oikeaan muotoon, numeroi ne automaattisesti eri laskureilla
def definitions(matchobj):

    str = "#-"+matchobj.group(1).strip()+"\n" + matchobj.group(3).strip() + matchobj.group(4).strip() + " " + '%%"' +matchobj.group(2).strip() +'"|c_('+matchobj.group(4).strip().lower() +')%%'+ matchobj.group(6).strip() 

    if (matchobj.group(2).strip() == None or matchobj.group(2).strip() == ""):
        str = "#-"+matchobj.group(1).strip()+"\n" + matchobj.group(3).strip() + matchobj.group(4).strip() + " " + '%%"' +"placeholder" + int(counter) +'"|c_('+matchobj.group(4).strip().lower() +')%%'+ matchobj.group(6).strip() 
    
    return str
    #return f"#-{matchobj.group(1).strip()}\n{matchobj.group(2).strip()}\n"

def labels(matchobj):
    labelsarr.append(matchobj.group(2).strip())
    return matchobj.group(1).strip() + "{§"+matchobj.group(2).strip() +"§}\n"

def counters(matchobj):
    return '%%""|c_begin%%' + matchobj.group(2).strip() + '%%""|c_end%%'

def numerointi(matchobj):
    return '%%"esim0"|c_ex%%'
# Muuttaa määritelmät, lauseet, yms oikeaan muotoon, numerointi automaattiseksi
contents = re.sub(thmregex,definitions,contents,flags=re.MULTILINE)
# Poistaa loput kaksoispisteet
contents = re.sub(colonregex, "#-", contents)

# Poistaa turhat viittaukset
contents = re.sub(emptyrefregex, "", contents)

# \\ jälkeen new line
contents = re.sub(r"\\\\", r"\\\\\n", contents)

# kaavojen laskurit
contents = re.sub(counterregex, counters, contents, flags=re.MULTILINE)

# viittaukset kaavoihin
contents = re.sub(labelregex, labels, contents)

for label in labelsarr:
    contents = re.sub(r"\[.*\]\(\#" + label +"\)\{(.|\n)*?\}", r'%%"'+label+r'"|ref%%', contents)


writefile("output.md", contents)

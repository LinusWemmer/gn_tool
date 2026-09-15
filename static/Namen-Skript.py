# -*- coding: utf-8 -*-
# Erzeugt personennamen.txt (Vor- und Nachnamen, die als Eigennamen markierbar sein sollen)
# und namen_auf_mann.txt (Namen auf "-mann", die keine gewöhnlichen Wörter sind).
# Aufzurufen aus dem Verzeichnis "static/".
#
# Quellen (werden heruntergeladen):
#   * firstname-database von Matthias Winkelmann -- rund 46000 Vornamen mit Genusangabe,
#     einschließlich der Markierung "?" für geschlechtsneutrale Namen.
#   * Nachnamenliste aus HBehrens/phonet4n -- die 9999 häufigsten deutschen Nachnamen.
#   * Wikidata (CC0) -- Familiennamen mit Sprache Deutsch sowie Vornamen, unterteilt in
#     männliche, weibliche und ausdrücklich geschlechtsneutrale.
#
# Aussortiert wird über zwei unabhängige Belege dafür, dass ein Name zugleich ein
# gewöhnliches Wort ist -- sonst würde aus "der Berg" ein "de Berg":
#   * die ParZu-Frequenzdaten (statistics/freq_data.pl): Wer dort als Substantiv, Adjektiv
#     oder Verb vorkommt, fällt raus ("Berg", "Klein", "Bauer", "Kai", "Community").
#   * Zmorge: Wer eine lexikalisierte Substantiv- oder Adjektivlesart hat, ohne im Korpus
#     belegt zu sein, fällt ebenfalls raus ("Ahorn", "Amsel", "Anemone").
# Beide Proben sind nötig: Die Frequenzdaten kennen seltene Wörter nicht, und Zmorge führt
# umgekehrt viele reine Vornamen fälschlich als Substantive ("Anna", "Julia", "Noah").
#
# namen_auf_mann.txt entsteht als Teilmenge: ein Name auf "-mann", den Zmorge nicht als
# Substantiv lexikalisiert hat. "Zimmermann", "Bergmann" und "Kaufmann" sind lexikalisiert
# und bleiben deshalb über person_pattern markierbar, "Hermann" und "Riemann" nicht.

import csv
import io
import re
import subprocess
import time
import unicodedata
import urllib.parse
import urllib.request

zmorge_model = '/home/marcos/Dropbox/geschlechtsneutral/zmorge-20150315-smor_newlemma.ca'
freq_data = '../statistics/freq_data.pl'

VORNAMEN_CSV = 'https://raw.githubusercontent.com/MatthiasWinkelmann/firstname-database/master/firstnames.csv'
NACHNAMEN_TXT = 'https://raw.githubusercontent.com/HBehrens/phonet4n/master/src/Tests/data/nachnamen.txt'
WIKIDATA = 'https://query.wikidata.org/sparql'

# Wikidata-Klassen: Familienname, Vorname, weiblicher, männlicher, geschlechtsneutraler Vorname.
# Der zweite Wert ist die Größenordnung, die die Klasse liefern muss. Während einer
# Störung antwortet der Endpunkt mit unvollständigen Ergebnissen, ohne einen Fehler zu
# melden -- der Lauf soll dann abbrechen statt eine verkürzte Liste zu schreiben.
WIKIDATA_KLASSEN = {'nachnamen': ('wdt:P31 wd:Q101352 ; wdt:P407 wd:Q188', 25000),
                    'vornamen': ('wdt:P31 wd:Q202444', 8000),
                    'vornamen_w': ('wdt:P31 wd:Q11879590', 8000),
                    'vornamen_m': ('wdt:P31 wd:Q12308941', 18000),
                    'vornamen_neutral': ('wdt:P31 wd:Q3409032', 1700)}

# Orts-, Länder- und Gewässernamen, die zugleich als Vor- oder Nachname geführt werden.
# Aus einem Abgleich mit den Wikidata-Klassen für Staaten, Gewässer, Gebirge und Regionen
# gewonnen und von Hand durchgesehen: Namen, die zwar auch einen Ort bezeichnen, aber vor
# allem Personennamen sind (Julia, Jordan, Roth, Beck, Lutz, Marion, Fischbach), bleiben drin.
ORTSNAMEN = """Iran Israel Kenia Kuba Liechtenstein Mali Mauritius Peru Schweden Togo Uruguay
Österreich Preußen Dominica Hohenlohe Waldeck Oldenburg Juda Elam Havel Rhein Oder Elbe Mosel
Lech Ural Aller Lauter Ville Nato Paris Timor Medina Lima Samara Bari Babel Milan Olympia
Siemens Boston Lothringen Aberdeen""".split()


def hole(url, accept=None):
    kopfzeilen = {'User-Agent': 'gn-tool-namelist/1.0'}
    if accept:
        kopfzeilen['Accept'] = accept
    # Wikidata drosselt zeitweise auf eine Anfrage pro Minute und lässt Abfragen ins Timeout
    # laufen; ohne Wiederholung bricht der Lauf dann mitten in den Namenklassen ab.
    for versuch in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=kopfzeilen),
                                        timeout=300) as antwort:
                return antwort.read()
        except Exception as fehler:
            if versuch == 5:
                raise
            print('  Abfrage fehlgeschlagen (%s), neuer Versuch in 70 s' % fehler)
            time.sleep(70)


def wikidata(bedingung):
    frage = ('SELECT DISTINCT ?l WHERE { ?s %s ; rdfs:label ?l . FILTER(lang(?l)="de") } '
             'LIMIT 200000' % bedingung)
    # Das Format muss über den Accept-Kopf angefordert werden; einen Parameter "format"
    # ignoriert der Endpunkt und liefert dann XML.
    daten = hole(WIKIDATA + '?' + urllib.parse.urlencode({'query': frage}), 'text/csv')
    # newline='' ist nötig, weil einzelne Bezeichnungen Zeilenumbrüche enthalten.
    treffer = {zeile[0].strip()
               for zeile in csv.reader(io.StringIO(daten.decode('utf-8'), newline=''))
               if zeile and zeile[0].strip() != 'l'}
    return treffer


vornamen_csv = list(csv.reader(io.StringIO(hole(VORNAMEN_CSV).decode('utf-8')), delimiter=';'))
winkelmann = {zeile[0].strip(): zeile[1].strip() for zeile in vornamen_csv[1:] if zeile[0].strip()}
nachnamen = {zeile.strip() for zeile in hole(NACHNAMEN_TXT).decode('latin-1').splitlines()
             if zeile.strip()}
# Diese Liste wird unbeschnitten als nachnamen.txt abgelegt. personennamen.txt sortiert gerade
# die Nachnamen aus, die zugleich gewoehnliche Woerter sind ("Richter", "Weber", "Bauer") --
# sonst wuerde aus "der Bauer" ein "de Bauer". Nach "Herr" oder "Frau" ist die Lesart aber
# eindeutig, und dort wird diese Liste gebraucht. Sie stammt allein aus dem statischen
# phonet4n-Download, nicht aus Wikidata, damit sie ohne Netzstoerungen reproduzierbar bleibt.
nachnamen_phonet4n = sorted(nachnamen)

for name, (bedingung, mindestens) in WIKIDATA_KLASSEN.items():
    treffer = wikidata(bedingung)
    print('  Wikidata %-17s %6d Bezeichnungen' % (name, len(treffer)))
    if len(treffer) < mindestens:
        raise RuntimeError('Wikidata lieferte nur %d statt mindestens %d Treffer für %s -- '
                           'vermutlich eine Störung des Endpunkts.'
                           % (len(treffer), mindestens, name))
    if name == 'nachnamen':
        nachnamen |= treffer
    else:
        winkelmann.update({eintrag: '' for eintrag in treffer if eintrag not in winkelmann})

# Nur einteilige Namen in lateinischer Schrift; einzelne Buchstaben und Kürzel bleiben draußen.
wohlgeformt = re.compile(r'^[A-ZÄÖÜ][a-zäöüßA-ZÄÖÜÀ-ſ-]+$')
kandidaten = sorted({name for name in set(winkelmann) | nachnamen
                     if len(name) >= 3 and wohlgeformt.match(name)
                     and all(unicodedata.name(z, '').startswith('LATIN') or z == '-'
                             for z in name)})

# --- Belegprobe 1: die Frequenzdaten von ParZu ---------------------------------------------
frequenz = {}
muster = re.compile(r"^occurs\((?:'([^']*)'|([^,]*)),([a-z]+),(\d+)\)\.$")
with open(freq_data, encoding='utf-8') as datei:
    for zeile in datei:
        treffer = muster.match(zeile.strip())
        if treffer:
            wort = treffer.group(1) if treffer.group(1) is not None else treffer.group(2)
            frequenz.setdefault(wort, {})[treffer.group(3)] = int(treffer.group(4))

# --- Belegprobe 2: Zmorge ------------------------------------------------------------------
analyse = subprocess.run(['fst-infl2', zmorge_model], input='\n'.join(kandidaten) + '\n',
                         capture_output=True, text=True, errors='replace').stdout
lexikalisiert_substantiv, lexikalisiert_anderes, aktuell = set(), set(), None
wortarten = re.compile(r'<\+(ADJ|V|ADV|INTJ|PREP|CONJ|ART|DEM|INDEF|PPRO|POSS|WPRO|PTCL)>')
for zeile in analyse.splitlines():
    if zeile.startswith('> '):
        aktuell = zeile[2:]
    elif aktuell and zeile.startswith(aktuell + '<+'):
        # Nur Lesarten, deren Lemma der Name selbst ist. Produktive Zerlegungen mit "<#>"
        # ("Neu<#>mann") zählen nicht, die bildet Zmorge zu jedem beliebigen Namen.
        if zeile.startswith(aktuell + '<+NN>'):
            lexikalisiert_substantiv.add(aktuell)
        elif wortarten.match(zeile[len(aktuell):]):
            lexikalisiert_anderes.add(aktuell)

ortsnamen = set(ORTSNAMEN)
namen, namen_auf_mann = [], []
for name in kandidaten:
    if name in ortsnamen:
        continue
    zaehlung = frequenz.get(name.lower(), {})
    if any(zaehlung.get(wortart, 0) for wortart in ('nn', 'adja', 'adjd', 'v')):
        continue
    if name.lower() not in frequenz and (name in lexikalisiert_substantiv
                                         or name in lexikalisiert_anderes):
        continue
    namen.append(name)
    if name.lower().endswith(('mann', 'männer')) and name not in lexikalisiert_substantiv:
        namen_auf_mann.append(name)

kopf = ('# Erzeugt von Namen-Skript.py -- nicht von Hand bearbeiten.\n'
        '# Quellen: firstname-database (M. Winkelmann), phonet4n-Nachnamen, Wikidata (CC0).\n')
with open('personennamen.txt', 'w', encoding='utf-8') as datei:
    datei.write(kopf + '\n'.join(namen) + '\n')
with open('namen_auf_mann.txt', 'w', encoding='utf-8') as datei:
    datei.write(kopf + '\n'.join(namen_auf_mann) + '\n')
with open('nachnamen.txt', 'w', encoding='utf-8') as datei:
    datei.write('# Erzeugt von Namen-Skript.py -- nicht von Hand bearbeiten.\n'
                '# Quelle: phonet4n-Nachnamen (die 9999 haeufigsten deutschen Nachnamen),\n'
                '# unbeschnitten. Wird nur gebraucht, um nach "Herr" oder "Frau" einen Nachnamen\n'
                '# zu erkennen, der zugleich ein gewoehnliches Wort ist ("Herr Richter").\n'
                + '\n'.join(nachnamen_phonet4n) + '\n')
neutral = {name for name, genus in winkelmann.items() if genus.startswith('?')}
print('personennamen.txt : %d Namen (davon %d geschlechtsneutral)'
      % (len(namen), len(neutral & set(namen))))
print('namen_auf_mann.txt: %d Namen' % len(namen_auf_mann))
print('nachnamen.txt     : %d Nachnamen' % len(nachnamen_phonet4n))

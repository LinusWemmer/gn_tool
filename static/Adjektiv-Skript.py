# Erzeugt substantivierbare_adjektive.txt, also die Substantivierungsformen aller Adjektive und
# Partizipien ("reisend" wird zu "Reisende").
# Grundlage ist eine deutsche Wortliste, die durch den Zmorge-Transducer geschickt wird. Alle
# Analysen mit "<+ADJ><Pos>" liefern das Adjektiv-Lemma; daraus entsteht die Substantivierung.
# Aufzurufen aus dem Verzeichnis "static/".

import re
import subprocess

word_list_name = '/usr/share/dict/ngerman'
zmorge_model = '/home/marcos/Dropbox/geschlechtsneutral/zmorge-20150315-smor_newlemma.ca'
output_file_name = 'substantivierbare_adjektive.txt'

with open(word_list_name, encoding='utf-8') as word_list:
    analysis = subprocess.run(['fst-infl2', '-q', zmorge_model], stdin=word_list,
                              capture_output=True, text=True, errors='replace').stdout

adjectives = set()
for line in analysis.splitlines():
    if '<+ADJ><Pos>' not in line:
        continue
    # Der Teil vor "<+ADJ>" ist das Lemma, kann aber Ableitungsmarken wie "<~>" enthalten.
    lemma = re.sub(r'<[^>]*>', '', line.split('<+ADJ>')[0]).strip()
    if lemma and re.fullmatch(r'[a-zäöüßA-ZÄÖÜ]{2,}', lemma):
        adjectives.add(lemma.lower())

# Die Substantivierung ist das Adjektiv mit angehängtem "e" ("groß" wird zu "Große"); endet das
# Adjektiv schon auf "e", bleibt es dabei ("böse" wird zu "Böse").
forms = {(a if a.endswith('e') else a + 'e').capitalize() for a in adjectives}

with open(output_file_name, 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(sorted(forms)) + '\n')

print("Processing completed. {} forms saved in '{}'".format(len(forms), output_file_name))

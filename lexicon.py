import re
import itertools


 # This class holds all the necessary information to construct the inclusivum form.
 # It is designed as a "static" class, so no lexicon object should be created, instead functions
 # are called by calling Lexicon.function()
class Lexicon:
    PRONOUNS = {"Nom": "en",
                "Gen": "enser",
                "Dat": "em",
                "Acc": "en"}
    
    ARTIKEL_DER = {"Nom": "de",
                "Gen": "ders",
                "Dat": "derm",
                "Acc": "de"}
    
    ARTIKEL_UNSER = {"Nom": "unse",
                "Gen": "unserers",
                "Dat": "unsererm",
                "Acc": "unse"}
    
    ARTIKEL_EUER = {"Nom": "eue",
                "Gen": "eurers",
                "Dat": "eurerm",
                "Acc": "eue"}
    
    # ein einers einerm ein
    ARTIKEL_EIN = {"Nom": "",
                "Gen": "ers",
                "Dat": "erm",
                "Acc": ""}
    
    # jedey jeders jederm jedey
    ARTIKEL_JEDER = {"Nom": "ey",
                "Gen": "ers",
                "Dat": "erm",
                "Acc": "ey"} 
    
    JEDER_PARADIGM = ["jedwed", "jed", "jen", "dies", "welch", "solch", "manch", "selbig", "jeglich"]

    EIN_PARADIGM = ["ein", "kein", "mein", "dein", "sein", "ihr", "ens"]

    ROMAN_NOUNS = [r"Alumn(a|us|i)", r"Ballerin(o|a)s?", r"Emerit(a|us|i)", r"Filipin(o|a)s?", r"Gueriller(o|a)s?", r"Latin(o|a)s?", r"Liber(o|a)s?", r"Mafios(o|a|i)", r"Torer(o|a)s?"]
    ROMAN_NOUNS_COMPOUND = [r"Alumn(a|us|i)", r"Ballerin(o|a)", r"Emerit(a|us|i)", r"Filipin(o|a)", r"Gueriller(o|a)", r"Latin(o|a)", r"Liber(o|a)", r"Mafios(o|a|i)", r"Torer(o|a)"]
    ROMAN_NOUN_STARTS = ["Alumn", "Ballerin", "Emerit", "Filipin", "Gueriller", "Latin", "Liber", "Mafios", "Torer"]

    # Apart from really irregular nouns, the following list also contains nouns that ParZu does not parse correctly, e.g. "Homöopathen", which ParZu does not recognize as a form of "Homöopath".
    IRREGULAR_NOUNS = [r"Prinz(essin)?", r"Hexer?", r"Witwer?", r"Br(a|ä)ut(igam)?", r"Hebamme", r"Amme", r"Homöopathen", r"Sympathisanten"]
    IRREGULAR_NOUNS_COMPOUND = [r"Prinz(en|essinnen)", r"Hexe(n|r)", r"Witwe(n|rn|r)", r"Br(a|ä)ut(igams)?", r"Hebammen", r"Ammen", r"Homöopathen", r"Sympathisanten"]
    IRREGULAR_NOUNS_NEUTRAL = ["Prinze", "Hexere", "Witwere", "Braute", "Hebammere", "Ammere", "Homöopathe", "Sympathisante"]

    # Vornamen, die daneben in nennenswertem Umfang gewöhnliche Substantive sind. Sie gelten nur
    # dann als Personenbezeichnung, wenn eines der PERSON_ADJECTIVES davorsteht -- sonst würde aus
    # "die schöne Rose" ein "de schöne Rose" und aus "der graue Wolf" ein "de graue Wolf".
    AMBIGUOUS_NAMES = ["Juli", "Mai", "August", "Rose", "Heide", "Linde", "Iris", "Erika",
                       "Horst", "Ernst", "Wolf"]

    # Namen, die sich am Genus vom gleichlautenden Substantiv unterscheiden: "Mark" ist als
    # Vorname ein Maskulinum, als Substantiv dagegen "die Mark" (Währung, Region) oder "das Mark"
    # (Knochenmark). Ein maskuliner Artikel oder ein maskulines Adjektiv zeigt daher den Namen an.
    MASCULINE_NAMES = ["Mark"]

    # Vornamen, die praktisch nur als Eigennamen vorkommen, von ParZu je nach Kontext aber als
    # gewöhnliche Substantive getaggt werden ("als heilige Maria"). Sie werden wie Eigennamen
    # behandelt. Die Liste lässt sich jederzeit erweitern.
    PROPER_NAMES = ["Maria", "Anna", "Julia", "Klara", "Nele", "Merle", "Frieda", "Jens", "Sven",
                    "Vera", "Silke", "Lisa", "Noah", "Luca", "Finn", "Emil", "Ida", "Mila",
                    "Johanna",
                    # Namen, die static/personennamen.txt aussortiert, weil sie im Korpus in
                    # geringem Umfang auch als gewöhnliches Wort vorkommen -- bei ihnen
                    # überwiegt der Name aber deutlich.
                    "Frank", "Peer", "Tim", "Bert", "Severin", "Leonardo", "Daphne", "Viola",
                    "Rosa"]

    # Wörter, die auf ein Adjektiv zurückgehen, aber keine Person bezeichnen -- meist
    # deadjektivische Abstrakta auf "-e" ("die Tiefe", "die Ebene", "die Weise"). Der Abgleich
    # erfolgt über das Wortende, damit Komposita mitgehen ("Vorgehensweise", "Arbeiterklasse",
    # "Regierungsebene"). Ermittelt aus den Kollisionen mit den häufigsten Substantiven der
    # ParZu-Frequenzdaten.
    NO_SUBST_ADJ = ["weise", "ebene", "klasse", "flotte", "note", "dichte", "breite", "weite",
                    "tiefe", "ferne", "reife", "schwere", "strenge", "wunde", "wüste", "dürre",
                    "rasse", "banane", "alternative", "kontroverse", "offensive", "exekutive",
                    "parallele", "weiche"]

    # "Linke" bezeichnet je nach Umgebung eine Person oder nicht. Mit bestimmtem Artikel oder
    # Possessivum im Femininum ist die Partei oder die Hand gemeint ("die Linke", "der Linken",
    # "mit seiner Linken"), sonst eine Person ("der Linke", "eine Linke").
    NO_SUBST_ADJ_FEM_DEFINITE = ["linke"]

    # Eigennamen, die keine Person bezeichnen. Nötig, weil die Regel für Eigennamen mit Artikel
    # ("Wo ist die Kim?" wird zu "Wo ist de Kim?") sonst auch Länder-, Gewässer- und
    # Organisationsnamen erfasst und "aus der Community" zu "aus derm Community" machte.
    # Akronyme wie EU oder NATO sind bereits über die Grossschreibung ausgenommen, artikellose
    # Namen wie Deutschland oder China stehen ohnehin aussen vor. Die Liste ist erweiterbar.
    NO_PERSON_NAMES = [
        # Fremdwörter, die ParZu als Eigennamen führt:
        "community", "location", "performance", "message", "story", "crew", "lobby", "szene",
        # Länder und Regionen, die einen Artikel tragen:
        "schweiz", "türkei", "ukraine", "irak", "iran", "kosovo", "balkan", "niederlande",
        "slowakei", "mongolei", "philippinen", "sudan", "libanon", "jemen", "kongo", "krim",
        "elfenbeinküste", "sahara", "karibik", "arktis", "antarktis", "toskana", "bretagne",
        "normandie", "provence", "riviera", "algarve", "pfalz", "lausitz", "eifel", "uckermark",
        "sowjetunion", "bundesrepublik", "emirate", "seychellen", "malediven", "kanaren", "azoren",
        # Gewässer und Gebirge:
        "rhein", "donau", "elbe", "main", "mosel", "spree", "oder", "themse", "seine", "wolga",
        "nil", "amazonas", "harz", "schwarzwald", "himalaya", "anden", "alpen",
        # Organisationen:
        "union", "kommission", "bundestag", "bundesrat", "sowjetunion",
    ]

    # Adjektive auf "-männisch" gehen auf ein Substantiv auf "-mann" zurück, dessen Plural auf
    # "-leute" endet. Das Inklusivum bildet sie darauf: "kaufmännisch" wird zu "kaufleutisch".
    # Geprüft wird das Wortende des Stammes, damit Komposita mitgehen ("unfachmännisch",
    # "wirtschaftsfachmännisch").
    MANN_ADJECTIVE_STEMS = ["kauf", "berg", "lands", "fach", "see", "staats", "weid"]

    # Wörter mit einer eigenen Form im Inklusivum, die keiner Regel folgen. "weltmännisch" lässt
    # sich nicht auf "-leute" bilden und wird durch "weltgewandt" ersetzt. Neben Adjektiven
    # stehen hier auch ein Substantiv und das Pronomen "jedermann".
    IRREGULAR_WORDS = {"jungfräulichkeit": "jungferlichkeit",
                       "jungfräulich": "jungferlich",
                       "weltmännisch": "weltgewandt",
                       "jedermann": "jedermensch"}

    # Die Endungen, die ein attributives Adjektiv tragen kann. Ohne Endung steht es adverbial
    # oder prädikativ ("Er grüsste landsmännisch"). Das "s" deckt den Genitiv von "jedermann" ab.
    WORD_ENDINGS = r"(e|em|en|er|es|s)?"

    # Gibt die Inklusivum-Form eines unregelmässigen Wortes zurück, oder None, wenn es keine gibt.
    # Neben Adjektiven laufen hier das Substantiv "Jungfräulichkeit" und das Pronomen "jedermann"
    # mit, deren Formen sich aus keiner Regel ergeben.
    def neutralize_irregular_word(word: str):
        if not word:
            return None
        match = re.fullmatch(r"(.*)männisch" + Lexicon.WORD_ENDINGS, word.lower())
        if match and any(match.group(1).endswith(stem)
                         for stem in Lexicon.MANN_ADJECTIVE_STEMS):
            neutral = match.group(1) + "leutisch" + (match.group(2) or "")
        else:
            for original, replacement in Lexicon.IRREGULAR_WORDS.items():
                match = re.fullmatch(original + Lexicon.WORD_ENDINGS, word.lower())
                if match:
                    neutral = replacement + (match.group(1) or "")
                    break
            else:
                return None
        return neutral[0].upper() + neutral[1:] if word[0].isupper() else neutral

    # Adjektive, die vor einem Namen eine angeredete Person anzeigen.
    PERSON_ADJECTIVES = ["lieb", "geehrt", "verehrt", "wert"]

    # Pronominaladjektive, die ParZu nicht lemmatisiert: Wortform und Grundform stimmen dort
    # überein ("anderen" hat die Grundform "anderen"), obwohl das Wort dekliniert ist. Ohne diese
    # Liste hielte neutralize_adjectives sie für undekliniert und liesse sie unverändert.
    # Ermittelt durch einen Parse aller in Frage kommenden Pronominaladjektive.
    UNLEMMATIZED_ADJ = ["ander", "derartig", "manch", "welch", "jen", "etlich", "selbig",
                        "irgendwelch"]

    # Komposita auf "-mann", die zu "-mensch" statt zu "-person" werden. Eingetragen wird der
    # Wortteil vor "-mann"; die Pluralform "-männer" wird mit abgedeckt.
    # Das Prinzip: Ist weder die Form auf "-frau" noch der Plural auf "-leute" gebräuchlich,
    # passt "-mensch" besser als "-person".
    MENSCH_COMPOUNDS = ["hampel", "ehren", "buh", "bieder", "schnee", "weihnachts", "butze",
                        "stroh", "knochen", "sauber", "blöd", "pfeifen", "welt",
                        # "Hauptperson" ist im Deutschen schon belegt und meint etwas anderes;
                        # der Dienstgrad wird deshalb zu "Hauptmensch". Gilt ueber die
                        # Endungspruefung auch fuer "Stabshauptmann" und "Oberhauptmann".
                        "haupt"]

    ALREADY_NEUTRAL_NOUNS = ["Gast", "Vormund", "Anarcho", "Hetero", "Homo", "Normalo", "Realo", "Waise", "Geisel", "Koryphäe", "Abkömmling", "Ankömmling", "Eindringling", "Erdling", "Flüchtling", "Fremdling", "Günstling", "Häftling", "Häuptling", "Jüngling", "Lehrling", "Liebling", "Neuling", "Pflegling", "Prüfling", "Säugling", "Schützling", "Sträfling", "Täufling", "Zögling", "Zwilling", "Flüchtling", "Charakter", "Wache", "Profi", "Studi", "Nazi", "Admin", "Fan", "Star", "Boss", "Clown", "Punk", "Hippie", "Freak", "Nerd", "Yuppie", "Hooligan", "Judoka", "Aikidoka", "Karateka", "Barista", "Jedi", "Sith", "Engel"]

    # Neologismen, die ein vorhandenes deutsches Wort mit eigenem Genus sind und deshalb ihren
    # Artikel behalten: "der Wassergeist", nicht "de Wassergeist". Ein Wassergeist ist keine
    # Person. Die übrigen Neologismen sind Inklusivum-Neubildungen ("Geschwister", "Elter",
    # "Owa") oder Personenbezeichnungen ("Sprössling") und bekommen wie diese den Artikel "de".
    NEOLOGISMS_KEEP_ARTICLE = ["Wassergeist"]

    # NEOLOGISMS lists singular forms as well as forms that occur in compounds
    NEOLOGISMS = [r"(Br(u|ü)der)|(Schwester)", r"(V(a|ä)ter)|(M(u|ü)tter)", r"O(p|m)a", r"Uro(p|m)a", r"Ururo(p|m)a", r"(Onkel)|(Tanten?)", r"Cousin(e|en)?|Vetter|Base", r"Jungfrau(en)?", r"Mädchen|Jung(e|en|s)", r"Neffen?|Nichten?", r"O(p|m)i", r"Uro(p|m)i", r"Ururo(p|m)i", r"(Mam|Pap)a", r"(Mam|Pap)i", r"Wasserm(a|ä)nn(er)?", r"Sohnem(a|ä)nn(er)?"]  
    NEOLOGISMS_NEUTRAL = ["Geschwister", "Elter", "Owa", "Urowa", "Ururowa", "Tonke", "Couse", "Jungfere", "Kid", "Nifte", "Owi", "Urowi", "Ururowi", "Sasa", "Sasi", "Wassergeist", "Sprössling"]
    NEOLOGISMS_PLURAL = ["Geschwister", "Eltern", "Owas", "Urowas", "Ururowas", "Tonken", "Cousen", "Jungferne", "Kids", "Niften", "Owis", "Urowis", "Ururowis", "Sasas", "Sasis", "Wassergeister", "Sprösslinge"]
    NEOLOGISMS_COMPOUND = ["Geschwister", "Elter", "Owa", "Urowa", "Ururowa", "Tonken", "Cousen", "Jungferne", "Kid", "Niften", "Owi", "Urowi", "Ururowi", "Sasa", "Sasi", "Wassergeist", "Sprössling"]

    # The next section generates List of Male/Female role nouns an their corresponding neutral forms
    # from the corresponding text files (also for substanivized adjectives, e.g. "Jugendliche")
    MALE_NOUNS = []
    FEMALE_NOUNS = []
    NEUTRAL_NOUNS = []
    COMPOSITE_NOUNS = []
    ALTERNATIVE_COMPOSITE_NOUNS = []
    SUBST_ADJ = []
    with open("static/movierbare_Substantive.txt") as f_male_nouns:
        for line in f_male_nouns:
            MALE_NOUNS.append(line.rstrip())

    with open("static/movierbare_Substantive_feminin.txt") as f_female_nouns:
        for line in f_female_nouns:
            FEMALE_NOUNS.append(line.rstrip())

    with open("static/movierbare_Substantive_inklusivum.txt") as f_inclusive_nouns:
        for line in f_inclusive_nouns:
            NEUTRAL_NOUNS.append(line.rstrip())
    
    with open("static/movierbare_Substantive_in_Komposita.txt") as f_composite_nouns:
        for line in f_composite_nouns:
            COMPOSITE_NOUNS.append(line.rstrip())

    with open("static/movierbare_Substantive_in_Komposita_alternativ.txt") as f_composite_nouns:
        for i, line in enumerate(f_composite_nouns):
            if not line.startswith("%"):
                ALTERNATIVE_COMPOSITE_NOUNS.append([i,line.rstrip()])

    with open("static/substantivierte_adjektive.txt") as f_sub_adj:
        for line in f_sub_adj:
            SUBST_ADJ.append(line.rstrip())

    # Substantivierungsformen aller Adjektive und Partizipien, erzeugt mit dem Zmorge-Transducer
    # aus /usr/share/dict/ngerman (siehe static/Adjektiv-Skript.py). Sie greifen nur, wenn ParZu
    # ein eindeutiges Genus liefert; die kuratierte Liste oben bleibt für die Fälle zuständig, in
    # denen Maskulinum und Neutrum formal zusammenfallen.
    SUBSTANTIVIZABLE_ADJ = set()
    with open("static/substantivierbare_adjektive.txt") as f_adj:
        for line in f_adj:
            SUBSTANTIVIZABLE_ADJ.add(line.rstrip())

    # Vor- und Nachnamen, an denen ein Artikel oder Adjektiv markierbar wird ("die Kim" wird
    # zu "de Kim"). Erzeugt von static/Namen-Skript.py aus drei Namensammlungen; wer im Korpus
    # oder in Zmorge als gewöhnliches Wort belegt ist, steht nicht drin ("Berg", "Bauer",
    # "Community"), ebensowenig Länder- und Gewässernamen.
    PERSON_NAMES = set()
    with open("static/personennamen.txt") as f_person_names:
        for line in f_person_names:
            if not line.startswith("#"):
                PERSON_NAMES.add(line.rstrip())

    # Namen auf "-mann", die keine gewöhnlichen Wörter sind. Ohne sie würde aus "Hermann"
    # ein "Herperson" und aus "Riemann" ein "Rieperson". "Zimmermann", "Bergmann" und
    # "Kaufmann" stehen nicht drin und bleiben deshalb über person_pattern markierbar.
    NAMES_IN_MANN = set()
    with open("static/namen_auf_mann.txt") as f_mann_names:
        for line in f_mann_names:
            if not line.startswith("#"):
                NAMES_IN_MANN.add(line.rstrip())

    # Die haeufigsten deutschen Nachnamen, unbeschnitten. PERSON_NAMES enthaelt sie nur, soweit
    # sie nicht zugleich gewoehnliche Woerter sind -- "Richter", "Weber" und "Bauer" fehlen dort,
    # weil sonst aus "der Bauer" ein "de Bauer" wuerde. Nach "Herr" oder "Frau" ist die Lesart
    # dagegen eindeutig, und nur dort wird diese Liste herangezogen.
    SURNAMES = set()
    with open("static/nachnamen.txt") as f_surnames:
        for line in f_surnames:
            if not line.startswith("#"):
                SURNAMES.add(line.rstrip())

    # Woerter, die in den Wortlisten stehen, weil ihr Kopf eine Personenbezeichnung ist, die aber
    # nie eine Person bezeichnen. Aufnahmekriterium: Das Wort bezeichnet ausschliesslich ein
    # Gremium oder eine Sache, niemals auch eines seiner Mitglieder. "Betriebsrat", "Gemeinderat",
    # "Stadtrat", "Aufsichtsrat" und die uebrigen Woerter auf "-rat" gehoeren deshalb NICHT hierher
    # -- sie bezeichnen beides. Zusammensetzungen ohne eigenen Eintrag in
    # movierbare_Substantive.txt sind ohnehin gesperrt ("Sicherheitsrat", "Ethikrat"), hier stehen
    # nur die Woerter mit eigenem Eintrag.
    NEVER_PERSON_NOUNS = {
        "Bundesrat",
        # Der blosse "Rat" ist weit ueberwiegend der Ratschlag oder das Gremium; als Amtstitel
        # ("Rat am Landgericht") ist er veraltet. Ohne diesen Eintrag wurde aus "ein guter Rat"
        # ein "ein gute Rate".
        "Rat",
    }

    # Laender- und Landschaftsnamen, die zugleich der Plural einer Einwohnerbezeichnung sind.
    # Eine Person ist gemeint, wenn ein Artikel dabeisteht UND das Wort im Plural oder in einem
    # anderen Kasus als dem Nominativ steht: "die Sachsen kamen", "er half dem Sachsen". Im
    # artikellosen Singular und im Nominativ Singular bezeichnet es das Gebiet: "Sachsen liegt im
    # Osten", "das heutige Sachsen", "1568 verfuegte Preussen". Gefuehrt werden die Formen auf
    # "-en"; der Singular ("der Sachse") ist eindeutig eine Person und laeuft normal durch.
    PEOPLE_OR_PLACE_NAMES = {
        "Sachsen", "Preußen", "Hessen", "Franken", "Bayern", "Schwaben", "Westfalen",
        "Pommern", "Polen", "Ungarn", "Schweden",
    }

    # ParZu lemmatisiert einige dieser Einwohnerbezeichnungen falsch: "Sachsen" und "Sachse"
    # beide zu "Sachs", "Pole" und "Polen" zu "Pol", "Hessen", "Bayern", "Pommern" und "Ungarn"
    # gar nicht. Die Wortliste findet sie dann nicht. Hier steht zu jeder betroffenen Wortform die
    # richtige Grundform. "Preuße", "Franke", "Schwabe", "Westfale" und "Schwede" fehlen, weil
    # ParZu sie richtig zurueckfuehrt.
    INHABITANT_LEMMAS = {
        "Sachse": "Sachse", "Sachsen": "Sachse",
        "Hessen": "Hesse", "Bayern": "Bayer", "Pommern": "Pommer",
        "Pole": "Pole", "Polen": "Pole", "Ungarn": "Ungar",
    }

    # Hinterglieder, bei denen die Vater/Mutter-Komponente als "Eltern" und nicht als "Elter"
    # erscheint, weil das Deutsche dafuer bereits ein Wort mit "Eltern" kennt: "Mutterschutz"
    # ergibt "Elternschutz". Bei den uebrigen Zusammensetzungen bleibt es bei "Elter"
    # ("Vaterland" -> "Elterland", "Muttersprache" -> "Eltersprache").
    ELTERN_COMPOUNDS = ("schutz",)

    # Zeilennummer von "Krankenpflegere"; sie wird berechnet, damit sie beim Bearbeiten der
    # Wortlisten nicht verrutscht.
    KRANKENPFLEGE_INDEX = NEUTRAL_NOUNS.index("Krankenpflegere")

    UMLAUTS = {"a": "ä", "o": "ö", "u": "ü"}

    # Substantive, die im Inklusivum-Plural keinen Umlaut bekommen, obwohl eine der beiden
    # traditionellen Pluralformen einen hat. Die Regel lautet: Umlaut nur dann, wenn der
    # maskuline UND der feminine Plural umlauten. Der Abgleich erfolgt über das Ende der
    # maskulinen Grundform, damit Komposita automatisch mit abgedeckt sind.
    NO_PLURAL_UMLAUT = [
        # Nur der feminine Plural lautet um; der maskuline ist schwach:
        "bauer",     # die Bauern    / die Bäuerinnen
        "graf",      # die Grafen    / die Gräfinnen
        "sachse",    # die Sachsen   / die Sächsinnen
        "schwabe",   # die Schwaben  / die Schwäbinnen
        "westfale",  # die Westfalen / die Westfälinnen
        "franke",    # die Franken   / die Fränkinnen
        "franzose",  # die Franzosen / die Französinnen
        "narr",      # die Narren    / die Närrinnen
        # Nur der maskuline Plural lautet um:
        "herzog",    # die Herzöge   / die Herzoginnen
        "general",   # die Generäle  / die Generalinnen
        "bass",      # die Bässe     / die Bassinnen
        "fuchs",     # die Füchse    / die Fuchsinnen
    ]

    # Überträgt den Umlaut der Plural-Eingabeform auf die Inklusivum-Form, damit aus "Ärzte"
    # oder "Ärztinnen" nicht "Arzterne", sondern "Ärzterne" wird. Der Umlaut wird aus der
    # Eingabe abgelesen und nicht aus den Wortlisten, weil deren feminine Spalte stellenweise
    # fehlerhaft ist ("Zahnarztin" statt "Zahnärztin"); Wörter, bei denen der Umlaut nichts
    # über den Plural aussagt, stehen in NO_PLURAL_UMLAUT.
    # Prüft, ob ein Wort grossgeschrieben ist. Der erste Buchstabe ist nicht immer das erste
    # Zeichen: "37-Jährige" beginnt mit einer Ziffer.
    def starts_uppercase(word) -> bool:
        letters = [character for character in word if character.isalpha()]
        return bool(letters) and letters[0].isupper()

    # Schlägt die Endung zum Kasus nach. Fehlt der Kasus in ParZus Analyse oder ist er unbekannt,
    # wird er als Nominativ behandelt. Das kann falsch sein, ist aber besser als ein Abbruch: Bei
    # ungrammatischer Eingabe wie "ein dumme Frau" lässt ParZu den Kasus offen, und der Zugriff
    # auf das Paradigma lieferte dann None.
    def case_ending(paradigm, case) -> str:
        return paradigm.get(case, paradigm["Nom"])

    def apply_plural_umlaut(head_base, original, male_noun) -> str:
        for exception in Lexicon.NO_PLURAL_UMLAUT:
            if male_noun.lower().endswith(exception):
                return head_base
        plain = original.lower()
        for vowel, umlaut in Lexicon.UMLAUTS.items():
            plain = plain.replace(umlaut, vowel)
        if plain == original.lower():
            return head_base
        # Nur umlauten, wenn Eingabe- und Inklusivum-Form denselben Stamm haben. Sonst würde
        # aus "Ehemänner" über "Ehepartnere" ein "Ehepärtnerne". Die Prüfung schließt zugleich
        # Stämme aus, die den Umlaut ohnehin schon tragen ("Schüler", "Händler").
        stem = head_base.lower()
        if stem.endswith("e"):
            stem = stem[:-1]
        if stem not in plain:
            return head_base
        # Der Umlaut steht auf dem letzten umlautfähigen Stammvokal ("Anwalte" -> "Anwälte",
        # "Notarzte" -> "Notärzte"). "au" wird dabei zu "äu", "eu" hat keine Umlautform.
        for i in range(len(head_base) - 1, -1, -1):
            if head_base[i].lower() not in Lexicon.UMLAUTS:
                continue
            if head_base[i].lower() == "u" and i > 0:
                if head_base[i-1].lower() == "a":
                    i -= 1
                elif head_base[i-1].lower() == "e":
                    continue
            umlaut = Lexicon.UMLAUTS[head_base[i].lower()]
            if head_base[i].isupper():
                umlaut = umlaut.upper()
            return head_base[:i] + umlaut + head_base[i+1:]
        return head_base

    # Neutralizes words where a neologism is the neutral form 
    def neutralize_neologism(feats, index) -> str:
        if feats[2] == "Pl":
            noun = Lexicon.NEOLOGISMS_PLURAL[index]
            if index in [0,7] and feats[1] == "Dat":
                return noun + "n"
            else:
                return noun
        else:
            noun = Lexicon.NEOLOGISMS_NEUTRAL[index]
            if feats[1] == ("Gen"):
                return noun + "s"
            else:
                return noun
        
    def neutralize_possesive_pronoun(pos,selected_components,nounlist,feats) -> str:
        all_components = []
        for nouninfo in nounlist:
            if nouninfo[0] == pos+1:
                all_components.append(nouninfo)
        if -5 in selected_components:
            possessive_pronoun_base = all_components[0][2]
        elif -3 in selected_components:
            possessive_pronoun_base = all_components[0][3]
            if all_components[0][-2]:
                possessive_pronoun_base = possessive_pronoun_base.capitalize()
        else:
            possessive_pronoun_base = all_components[0][2]
        if feats[1] == "_":
            feats[1] = "Nom"
        if -5 in selected_components or -4 in selected_components:
            ending = Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
        else:
            ending = all_components[1][2]
        if ending == "s":
            ending = "es"
        return possessive_pronoun_base + ending
        
    def neutralize_possesive_pronoun_with_sonderzeichen(pos,selected_components,nounlist,feats,sonderzeichen_with_second_base) -> str:
        all_components = []
        for nouninfo in nounlist:
            if nouninfo[0] == pos+1:
                all_components.append(nouninfo)
        if feats[1] == "_":
            feats[1] = "Nom"
        if -4 in selected_components:
            ending = Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
        else:
            ending = all_components[1][2]
        if ending == "s":
            ending = "es"
        if -3 in selected_components:
            possessive_pronoun_base = all_components[0][3]
            if all_components[0][-2]:
                possessive_pronoun_base = possessive_pronoun_base.capitalize()
        else:
            possessive_pronoun_base = all_components[0][2] + ending + sonderzeichen_with_second_base
        return possessive_pronoun_base + ending
        

    def neutralize_possesive_article(word_parse) -> str:
        # The following case distinction is needed to ensure that "ihr*sein" becomes "ens" and not "ens*ens".
        sonderzeichen_match = re.match(r"((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)([/*_:])((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)$", word_parse[-2])
        if sonderzeichen_match:
            pronoun = sonderzeichen_match.group(8) + sonderzeichen_match.group(11)
        else:
            pronoun = word_parse[-2]
        pronoun = pronoun.replace("ihr", "ens")
        pronoun = pronoun.replace("sein", "ens")
        pronoun = pronoun.replace("Ihr", "Ens")
        pronoun = pronoun.replace("Sein", "Ens")
        return pronoun

    
    def neutralize_attributive_pronoun(word_parse) -> str:
        article = "dersen"
        return article.capitalize() if word_parse[1][0].isupper() else article
    
    def neutralize_article(word_parse) -> str:
        # Neuter and plural articles should not be changed:
        if "Neut" in word_parse[5] or "Pl" in word_parse[5]:
            return word_parse[1]
        feats = word_parse[5].split("|")
        is_capitalized = word_parse[1][0].isupper()
        # Case Definitive Articles
        if feats[0] == "Def":
            if feats[2] == "_":
                feats[2] = "Nom"
            article =  Lexicon.case_ending(Lexicon.ARTIKEL_DER, feats[2])
            return article.capitalize() if is_capitalized else article
        # Case Indifinitive Artikels, only ein
        elif feats[0] == "Indef":
            if feats[2] == "_":
                feats[2] = "Nom"
            article = "ein" +  Lexicon.case_ending(Lexicon.ARTIKEL_EIN, feats[2])
            return article.capitalize() if is_capitalized else article
        # All other types of article
        else:
            word = word_parse[1].lower()
            # in case no grammatical case is found, treat as nominative, even if wrong.
            if feats[1] == "_":
                feats[1] = "Nom"
            # derselbe/dieselbe:
            if re.match(r"d..selbe.?$", word):
                if feats[1] == "Nom" or feats[1] == "Acc":
                    return "Deselbe" if is_capitalized else "deselbe"
                else:
                    article =  Lexicon.case_ending(Lexicon.ARTIKEL_DER, feats[1]) + "selben"
                    return article.capitalize() if is_capitalized else article
            # derjenige/diejenige:
            if re.match(r"d..jenige.?$", word):
                if feats[1] == "Nom" or feats[1] == "Acc":
                    return "Dejenige" if is_capitalized else "dejenige"
                else:
                    article =  Lexicon.case_ending(Lexicon.ARTIKEL_DER, feats[1]) + "jenigen"
                    return article.capitalize() if is_capitalized else article
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon.JEDER_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
                    return article.capitalize() if is_capitalized else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon.EIN_PARADIGM:
                if word.startswith(start):
                    sonderzeichen_match = re.match(r"((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)([/*_:])((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)$", word_parse[-2])
                    if sonderzeichen_match:
                        article = sonderzeichen_match.group(1) + Lexicon.case_ending(Lexicon.ARTIKEL_EIN, feats[1]) + sonderzeichen_match.group(7) + sonderzeichen_match.group(8) + Lexicon.case_ending(Lexicon.ARTIKEL_EIN, feats[1])
                    else:
                        article = start + Lexicon.case_ending(Lexicon.ARTIKEL_EIN, feats[1])
                    return article.capitalize() if is_capitalized else article
            if re.match(r"unse?re?.?$", word):
                article = Lexicon.case_ending(Lexicon.ARTIKEL_UNSER, feats[1])
                return article.capitalize() if is_capitalized else article
            elif re.match(r"eue?re?.?$", word):
                article = Lexicon.case_ending(Lexicon.ARTIKEL_EUER, feats[1])
                return article.capitalize() if is_capitalized else article
            # Some articles don't have to be neutralized, just return them.
            else:
                return word_parse[1]

    def neutralize_adjectives(word_parse, has_article) -> str:
        print("neutralize adjective:", word_parse, has_article)
        feats = word_parse[5].split("|")
        # ParZu lässt die Merkmale eines Adjektivs manchmal ganz offen und liefert nur "_" statt
        # der üblichen Anordnung "Steigerung|Genus|Kasus|Numerus|Flexion|" -- etwa wenn das
        # zugehörige Substantiv kleingeschrieben ist ("vor einem anderen spieler"). Die Liste
        # wird deshalb auf die Länge aufgefüllt, die diese Funktion erwartet. Ein fehlender
        # Kasus gilt weiter unten ohnehin als Nominativ, ein fehlender Numerus als Singular.
        while len(feats) < 4:
            feats.append("_")
        # Plural adjectives don't need to be changed.
        # Undeclined adjectives don't need to be changed.
        # Undekliniert ist ein Adjektiv, wenn Wortform und Grundform übereinstimmen ("die rosa
        # Lehrerin", "der Schweizer Lehrer", "der super Lehrer"). Die Pronominaladjektive aus
        # UNLEMMATIZED_ADJ lemmatisiert ParZu nicht, dort sind beide Formen ebenfalls gleich,
        # obwohl das Wort dekliniert ist ("den anderen Lehrer"). Sie sind daran zu erkennen, dass
        # sie zugleich mit einem der Stämme beginnen und eine Deklinationsendung tragen --
        # "mancherlei" beginnt zwar mit "manch", trägt aber keine Endung und bleibt unverändert.
        word = word_parse[1].lower()
        declined_pronominal = (any(word.startswith(stem) for stem in Lexicon.UNLEMMATIZED_ADJ)
                               and re.search(r"(e|em|en|er|es)$", word))
        if feats[3] == "Pl" or (word_parse[1] == word_parse[2] and not declined_pronominal):
            return word_parse[1]
        # This is a hack to make sure "letzt-" works correctly
        if word_parse[2] == ("letzte"):
            word_parse[2] = "letzt"
        # This is a hack to make sure that adjectival usage of "jed-", "jen-" etc works correctly  
        # This is a hack to make sure "ander-" works correctly (no longer needed)
        #if word_parse[2].startswith("ander") and len(word_parse[2]) < 8:
        #    word_parse[2] = "ander"
        # Differentiate Superlative/Comparative/Normal adjectives
        adjective = ""
        if "Sup" in word_parse[5]:
            match = re.search(r".+st", word_parse[1])
            adjective = match.group(0)
        elif "Comp" in word_parse[5]:
            match1 = re.search(r".+er.", word_parse[1])
            adjective = match1.group(0)[:-1]
        else:
            # If word_parse[1] ends in "e" possibly followed by "r", "m", "n" or "s", we have to remove this ending 
            if word_parse[1].endswith("e"):
                adjective = word_parse[1][:-1]
            elif word_parse[1].endswith("er") or word_parse[1].endswith("en") or word_parse[1].endswith("em") or word_parse[1].endswith("es"):
                adjective = word_parse[1][:-2]
            elif word_parse[2].endswith("e"):
                adjective = word_parse[2][:-1]
            else:
                adjective = word_parse[2]
        # Weak Flexion, after article der/die/das (de), also "Jeder"-list
        print("adjective root:",adjective)
        if has_article:
            # Differentiate case
            if feats[2] == "Acc" or feats[2] == "Nom":
                adjective = adjective + "e"
                return adjective.capitalize() if word_parse[1][0].isupper() else adjective
            else:
                adjective = adjective + "en"
                return adjective.capitalize() if word_parse[1][0].isupper() else adjective
        # Strong Flexion, on it's own
        # If we for some reason don't get a case, pretend it is nominative.
        if feats[2] == "_":
            feats[2] = "Nom"
        adjective =  adjective + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[2])
        print("adjective:", adjective)
        return adjective.capitalize() if word_parse[1][0].isupper() else adjective
    
    # Neutralize possesive jemand, this often doesn't get parsed correctly
    def neutralize_pos_jemand(word_parse) -> str:
        word = "jemanders"
        return word.capitalize() if word_parse[1][0].isupper() else word
    
    def neutralize_pronoun(word_parse,has_article) -> str:
        feats = word_parse[5].split("|")
        if len(feats) < 4:
            feats.append("_")
            feats.append("_")
            feats.append("_")
        is_capitalized = word_parse[1][0].isupper()
        if feats[0] == "Neut":
            return word_parse[1]
        if word_parse[4] == "PPER":
            if feats[3] == "_":
                if word_parse[1] == "ihr" or word_parse[1] == "Ihr":
                    feats[3] = "Dat"
                else:
                    feats[3] = "Nom"
            pronoun = word_parse[1]
            if feats[0] == "3" or feats[0] == "_":
                pronoun = Lexicon.case_ending(Lexicon.PRONOUNS, feats[3])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PIS":
            pronoun = word_parse[1]
            if feats[1] == "_":
                feats[1] = "Nom"
            if word_parse[2] == "man":
                pronoun = "mensch"
            elif word_parse[2].endswith("mand"):
                if feats[1] == "Dat" or feats[1] == "Gen":
                    pronoun = word_parse[2] + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
                else:
                    pronoun = word_parse[2]
            else: 
                if word_parse[2].endswith("er"):
                    word_parse[2] = word_parse[2][:-1]
                if word_parse[1].endswith("as"):
                    # This case should normally not arise, as such pronouns should not be markable.
                    # But to ensure that the result is not wrong, we just return the original word.
                    pronoun = word_parse[1]
                else:
                    if has_article:
                        # Differentiate case
                        if feats[1] == "Acc" or feats[1] == "Nom":
                            pronoun = word_parse[2]
                            return pronoun.capitalize() if is_capitalized else pronoun
                        else:
                            pronoun = word_parse[2] + "n"
                            return pronoun.capitalize() if is_capitalized else pronoun
                    else:
                        pronoun = word_parse[2][:-1] + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" and word_parse[1].startswith("d"):
            if feats[1] == "_":
                feats[1] = "Nom"
            pronoun = Lexicon.case_ending(Lexicon.ARTIKEL_DER, feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" or word_parse[4] == "PDS" or word_parse[4] == "PWS":
            if feats[1] == "_":
                feats[1] = "Nom"
            for start in Lexicon.JEDER_PARADIGM:
                if re.match(start + "e.?$", word_parse[2]):
                    pronoun = word_parse[2][:-1] + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1]) 
                    return pronoun.capitalize() if is_capitalized else pronoun
            pronoun = Lexicon.case_ending(Lexicon.ARTIKEL_DER, feats[1])
            if re.match(r"d..jenige$", word_parse[2]):
                pronoun += "jenige"
                if feats[1] == "Gen" or feats[1] == "Dat":
                    pronoun += "n"
            if re.match(r"d..selbe$", word_parse[2]):
                pronoun += "selbe"
                if feats[1] == "Gen" or feats[1] == "Dat":
                    pronoun += "n"
            return pronoun.capitalize() if is_capitalized else pronoun

    def neutralize_word(word_parse,has_article) -> str:
        print("neutralize_word")
        print("word_parse:", word_parse)
        # Plural cases don't have to be changed and can be ignored
        if "Pl" in word_parse[5]:
            return word_parse[1]
        # neutralize Articles
        elif word_parse[3] == "ART" and not word_parse[4] == "PRELAT":
            return Lexicon.neutralize_article(word_parse)
        # neutralize Pronouns
        elif word_parse[3] == "PRO":
            return Lexicon.neutralize_pronoun(word_parse,has_article)
        else:
            return word_parse[-2]

    # This function searches for all person nouns in a (potentially composite) noun.
    # It returns a Boolean indicating whether the head of the noun has been identified as a person noun, 
    # a string "prefix" and a list of tuples of the form [i, original, neutralized, suffix, noun_type, capitalized],
    # where i the position of the person noun in the composite noun, original is the original person noun,
    # neutralized is the neutralized person noun (but for the head, "neutralized" is the line number in the list of
    # person nouns, as the neutralization is created later in Marking_Tool.neutralize_nounphrase), suffix is the 
    # string between the person noun and the next person noun or the end of the composite noun, noun_type is the type
    # of noun ("standard" for nouns from Lexicon.MALE_NOUNS or Lexicon.FEMALE_NOUNS, "romanism" for nouns from
    # Lexicon.ROMAN_NOUNS, "irregular" for nouns from Lexicon.IRREGULAR_NOUNS, "neologism" for nouns from
    # Lexicon.NEOLOGISMS, "neutral" for nouns from Lexicon.NEUTRAL_NOUNS, "beamtey" for "Beamter"/"Beamte"/"Beamten",
    # "substantivized adjective" for nouns from Lexicon.SUBST_ADJ or ending in "sprachige", "person" for "Mann", "Frau",
    # "Herr" and "Dame", "kind" for "Sohn" and "Tochter"), and capitalized is a Boolean indicating whether the head of the nounphrase is capitalized.
    def check_noun(word_parse,feats,has_article,has_possessive,has_adjective=False,has_person_adjective=False,has_masculine_modifier=False,is_epithet=False,has_definite_article=False,inferred_gender="_"):
        print("check_noun")
        print("word_parse:", word_parse)
        noun = word_parse[2]

        # Neben der Grundform wird an mehreren Stellen die Wortform gegen Namenslisten geprüft,
        # weil ParZu Namen gelegentlich falsch lemmatisiert. Ein Eigenname wird aber nicht
        # gebeugt -- ausser im Genitiv auf "-s". Weicht die Wortform sonst von der Grundform ab,
        # ist sie eine Beugung und taugt nicht als Beleg: "Sinne", "Grade", "Männer", "Wahlen"
        # und "Ecken" sind zwar alle Nachnamen, in einem Satz aber weit häufiger Beugungsformen
        # von "Sinn", "Grad", "Mann", "Wahl" und "Ecke".
        name_form = word_parse[1] if word_parse[1] in (noun, noun + "s") else None

        # Bezeichnungen, die nie eine Person meinen, bekommen kein Kaestchen.
        if noun in Lexicon.NEVER_PERSON_NOUNS or word_parse[1] in Lexicon.NEVER_PERSON_NOUNS:
            return False, "", []

        # search_lonely_adjectives schreibt allein stehende Adjektive vor dem Reparse gross, damit
        # ParZu sie als substantiviert erkennt. Steht die Wortform gross, die Realisierung aus dem
        # Eingabetext aber klein, ist die Grossschreibung künstlich: Das Wort ist ein Adjektiv und
        # darf nicht über die Substantivlisten laufen. Aus "den jungen und den alten Lehrer" würde
        # sonst "die junge Person" (Junge als Knabe) oder über die Neologismen "de kid".
        # Der Zweig weiter unten behandelt denselben Fall, kam bisher aber zu spät.
        if word_parse[1][:1].isupper() and word_parse[-2][:1].islower():
            if noun.endswith(("er", "en", "em", "es")):
                neutral_base = noun[:-1]
            else:
                neutral_base = noun
            return True, "", [[0, noun, neutral_base, "", "substantivized adjective", False]]

        noun_base = noun[0:-1]
        noun_suffix_length = len(word_parse[1]) - word_parse[1].rfind(noun_base) - len(noun)

        if feats[0] == "Masc" or feats[0] == "_":
            for j, line in enumerate(Lexicon.MALE_NOUNS):
                if noun.lower().endswith(line.lower()):
                    prenoun = noun[:-len(line)]
                    if len(prenoun) != 1 and not (prenoun.endswith("c") and line.lower().startswith("h")) and not (len(prenoun) != 0 and (line == "Tor" or line == "Rat" or line == "Ire" or line == "Ahn" or line == "Erbe" or line == "Same" or line == "Ober" or line == "Elfe" or line == "Graf"
                                                       or line == "Inder" or line == "Recke")) and not (prenoun.endswith("h") and line.lower().startswith("enkel")) and not (prenoun.endswith("hä") and line == "User"): # The last case is to avoid false positives with "Henkel" and "Schenkel"
                        prefix, list = Lexicon.check_composite_noun(prenoun,False)
                        original = word_parse[1][-len(line)-noun_suffix_length:]
                        capitalized = noun[-len(line)].isupper()
                        list.append([len(word_parse[1])-len(line)+noun_suffix_length, original, j, "", "standard", capitalized])
                        return True, prefix, list


        # As ParZu sometimes does not recognize the gender of nouns in "-in" correctly, we do not check for
        # the nouns ending in "-in" whether they were recognized as feminine.
        #if feats[0] == "Fem" or feats[0] == "_":
        for j, line in enumerate(Lexicon.FEMALE_NOUNS):
            if noun.lower().endswith(line.lower()):
                prenoun = noun[:-len(line)]
                if len(prenoun) != 1 and not (prenoun.endswith("c") and line.lower().startswith("h")):
                    prefix, list = Lexicon.check_composite_noun(prenoun,False)
                    original = word_parse[1][-len(line)-noun_suffix_length:]
                    capitalized = noun[-len(line)].isupper()
                    list.append([len(word_parse[1])-len(line)+noun_suffix_length, original, j, "", "standard", capitalized])
                    return True, prefix, list


        # "Junge" und "Mädchen" werden zu "junge Person" (im Plural "junge Leute").
        # Diese Prüfung steht vor den NEOLOGISMS, die dieselben Wörter sonst zu "Kid" machen würden.
        junge_person_pattern = r"(mädchen|jung(e|en|s))$"
        match = re.search(junge_person_pattern, noun.lower())
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            if len(prenoun) != 1:
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "junge_person", capitalized])
                return True, prefix, list

        # "Krankenschwester" ist eine Berufsbezeichnung, keine Verwandtschaftsbezeichnung -- das
        # Hinterglied stammt aus der Ordenstradition. Der Beruf heisst im Inklusivum wie die
        # maskuline Entsprechung "Krankenpfleger". Die Pruefung steht vor den Neologismen, weil
        # dort sonst die Regel Schwester -> Geschwister griffe ("Krankengeschwister").
        match = re.search(r"krankenschwestern?$", noun.lower())
        if match:
            match_position = match.start()
            prefix, list = Lexicon.check_composite_noun(noun[:match_position], False)
            original = word_parse[1][match_position:]
            capitalized = noun[match_position].isupper()
            list.append([match_position, original, Lexicon.KRANKENPFLEGE_INDEX, "",
                         "standard", capitalized])
            return True, prefix, list

        for j, neologism in enumerate(Lexicon.NEOLOGISMS):
            neologism = "(" + neologism + ")$"
            match = re.search(neologism.lower(), noun.lower())
            if match:
                match_position = match.start()
                prenoun = noun[:match_position]
                # The part after "and" of the following condition ensures that words like "Aroma" and "Europa" are not
                # falsely recognized as compounds involving "Oma" and "(Ur)opa".
                if len(prenoun) != 1 and (len(prenoun) == 0 or not j in [2,3]):
                    prefix, list = Lexicon.check_composite_noun(prenoun,False)
                    original = word_parse[1][match_position:]
                    capitalized = noun[match_position].isupper()
                    list.append([match_position, original, j, "", "neologism", capitalized])
                    return True, prefix, list
                
        if has_possessive and noun in ["Mann", "Frau"]:
            # Line 967 is the line number of "Ehepartnere" in Lexicon.NEUTRAL_NOUNS
            return True, "", [[0, noun, 967, "", "standard", True]]

        # "Mannschaft" wird zu "Team". Das ist ein Neutrum, deshalb müssen die abhängigen
        # Wörter ins Neutrum gesetzt werden.
        team_pattern = r"mannschaft(en)?$"
        match = re.search(team_pattern, noun.lower())
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            if len(prenoun) != 1:
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "team", capitalized])
                return True, prefix, list

        # Manche Komposita auf "-mann" werden zu "-mensch" statt zu "-person".
        for stem in Lexicon.MENSCH_COMPOUNDS:
            match = re.search(stem + r"(m(a|ä)nn(er)?)$", noun.lower())
            if match:
                match_position = match.start(1)
                prenoun = noun[:match_position]
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "mensch", capitalized])
                return True, prefix, list

        # "Ehemann"/"Ehefrau" werden zu "Ehepartnere" und nicht über person_pattern zu "Eheperson".
        ehepartner_pattern = r"ehe(m(a|ä)nn(er)?|frau(en)?)$"
        match = re.search(ehepartner_pattern, noun.lower())
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            if len(prenoun) != 1:
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                # Zeile 967 ist die Zeilennummer von "Ehepartnere" in Lexicon.NEUTRAL_NOUNS
                list.append([match_position, original, 967, "", "standard", capitalized])
                return True, prefix, list

        person_pattern = r"((m(a|ä)nn(er)?)|(frau(en)?)|herr(e?n)?|damen?)$"
        match = re.search(person_pattern, noun.lower())
        # Namen wie "Hermann" oder "Pellmann" enden zwar auf "-mann", sind aber keine
        # Komposita mit einer Personenbezeichnung.
        if noun in Lexicon.NAMES_IN_MANN or name_form in Lexicon.NAMES_IN_MANN:
            match = None
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            # "Mannomann" ist ein Ausruf und keine Personenbezeichnung.
            if len(prenoun) != 1 and prenoun.lower() != "manno":
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "person", capitalized])
                return True, prefix, list
            
        kind_pattern = r"(s(o|ö)hn(e|en)?|t(o|ö)chtern?)$"
        match = re.search(kind_pattern, noun.lower())
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            if len(prenoun) != 1:
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "kind", capitalized])
                return True, prefix, list
            
        beamt_pattern = r"(beamt(in(nen)?|e(r|n|m)?))$"
        match = re.search(beamt_pattern, noun.lower())
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            if len(prenoun) != 1:
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "beamtey", capitalized])
                return True, prefix, list
        
        for j, romanism in enumerate(Lexicon.ROMAN_NOUNS):
            romanism = "(" + romanism + ")$"
            match = re.search(romanism.lower(), noun.lower())
            if match:
                match_position = match.start()
                prenoun = noun[:match_position]
                if len(prenoun) != 1 and not (prenoun.endswith("c") and noun[match_position:].startswith("h")):
                    prefix, list = Lexicon.check_composite_noun(prenoun,False)
                    original = word_parse[1][match_position:]
                    capitalized = noun[match_position].isupper()
                    list.append([match_position, original, j, "", "romanism", capitalized])
                    return True, prefix, list
            
        for j, irregular_noun in enumerate(Lexicon.IRREGULAR_NOUNS):
            irregular_noun = "(" + irregular_noun + ")$"
            match = re.search(irregular_noun.lower(), noun.lower())
            if match:
                match_position = match.start()
                prenoun = noun[:match_position]
                if len(prenoun) != 1 and not (prenoun.endswith("c") and noun[match_position:].lower().startswith("h")) and not (prenoun.lower().endswith("zus") and noun[match_position:].lower().startswith("ammen")):
                    prefix, list = Lexicon.check_composite_noun(prenoun,False)
                    original = word_parse[1][match_position:]
                    capitalized = noun[match_position].isupper()
                    list.append([match_position, original, j, "", "irregular", capitalized])
                    return True, prefix, list

        if feats[2] != "Pl":
            for neutral_noun in Lexicon.ALREADY_NEUTRAL_NOUNS:
                neutral_noun = "(" + neutral_noun + ")$"
                match = re.search(neutral_noun.lower(), noun.lower())
                if match:
                    match_position = match.start()
                    prenoun = noun[:match_position]
                    if len(prenoun) != 1 and not (prenoun.endswith("c") and noun[match_position:].lower().startswith("h")):
                        prefix, list = Lexicon.check_composite_noun(prenoun,False)
                        original = word_parse[1][match_position:]
                        capitalized = noun[match_position].isupper()
                        list.append([match_position, original, original, "", "neutral", capitalized])
                        return True, prefix, list
                
            # Ein substantiviertes Adjektiv im Neutrum bezeichnet keine Person ("das Gute",
            # "fürs Erste") und braucht daher nie markiert zu werden. Im Genitiv und Dativ, wo
            # Maskulinum und Neutrum formal zusammenfallen, lässt ParZu das Genus offen und meldet
            # gar kein "Neut"; die kuratierte Liste bleibt dort also zuständig.
            # Wo ParZu fälschlich "Neut" meldet -- etwa weil es ein Relativpronomen als Artikel
            # liest ("ein Geschenk, das Zweiterer schon besaß") --, verrät die Endung den Irrtum:
            # Im Neutrum endet die Form auf "-e" ("das Gute") oder "-es" ("ein Gutes"), nie auf
            # "-er", "-en" oder "-em".
            if not (feats[0] == "Neut" and noun.lower().endswith(("e", "es"))):
                for j, subadj in enumerate(Lexicon.SUBST_ADJ):
                    subadj = "(" + subadj + ")(r|n)?$"
                    match = re.search(subadj.lower(), noun.lower())
                    if match:
                        # Im Genitiv und Dativ trägt ein substantiviertes Adjektiv immer eine Endung
                        # ("der Jugendlichen", "meiner Verlobten"). Steht dort die blosse Grundform,
                        # handelt es sich um ein gewöhnliches Substantiv ("aus Liebe").
                        if len(feats) > 1 and feats[1] in ("Gen", "Dat") and word_parse[1].lower().endswith(match.group(1).lower()):
                            continue
                        match_position = match.start()
                        prenoun = noun[:match_position]
                        if len(prenoun) != 1 and not (prenoun.endswith("c") and noun[match_position:].lower().startswith("h")):
                            prefix, list = Lexicon.check_composite_noun(prenoun,False)
                            original = word_parse[1][match_position:]
                            capitalized = noun[match_position].isupper()
                            list.append([match_position, original, match.group(1).capitalize(), "", "substantivized adjective", capitalized])
                            return True, prefix, list
            
            # Über die kuratierte Liste hinaus zählt jedes Adjektiv als substantiviert, sofern
            # ParZu ein eindeutiges Genus liefert: Ein neutrum substantiviertes Adjektiv bezeichnet
            # keine Person ("das Gute"), ein maskulines oder feminines dagegen schon ("die
            # Reisende"). Im Genitiv und Dativ fallen Maskulinum und Neutrum formal zusammen, dort
            # bleibt die kuratierte Liste zuständig.
            # Auch hier gilt die Endungsprobe: Im Genitiv und Dativ trägt ein substantiviertes
            # Adjektiv eine Endung, die blosse Grundform ist dort ein gewöhnliches Substantiv
            # ("aus Liebe").
            # Fehlt das Genus, wird das aus der Form des Determinierers erschlossene verwendet.
            gender = feats[0] if feats[0] in ("Masc", "Fem") else inferred_gender
            # Bei Altersangaben wie "37-Jährige" steht das substantivierte Adjektiv im zweiten
            # Bestandteil; die Zahl davor wird als Vorderglied unverändert übernommen.
            number_match = re.match(r"(\d+-)(.+)$", noun)
            number_prefix = number_match.group(1) if number_match else ""
            core = number_match.group(2) if number_match else noun
            if (gender in ("Masc", "Fem") and core in Lexicon.SUBSTANTIVIZABLE_ADJ
                    and not (len(feats) > 1 and feats[1] in ("Gen", "Dat")
                             and word_parse[1].lower().endswith(core.lower()))
                    and not any(core.lower().endswith(exception) for exception in Lexicon.NO_SUBST_ADJ)
                    and not (gender == "Fem" and (has_definite_article or has_possessive)
                             and any(core.lower().endswith(exception)
                                     for exception in Lexicon.NO_SUBST_ADJ_FEM_DEFINITE))):
                return True, number_prefix, [[len(number_prefix), core, core, "", "substantivized adjective", True]]

            sprachige_pattern = r"(..+sprachige)(r|n|m|s)?$"
            match = re.search(sprachige_pattern, noun.lower())
            if match:
                match_position = match.start()
                prenoun = noun[:match_position]
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, match.group(1).capitalize(), "", "substantivized adjective", capitalized])
                return True, prefix, list
        
        # The following case covers lonely adjectives that were artificially capitalized before
        # reparsing, sowie Beinamen wie "Peter dem Großen", die von Haus aus grossgeschrieben sind:
        if (word_parse[1][0].isupper() and word_parse[-2][0].islower()) or is_epithet:
            if noun.endswith("er") or noun.endswith("en") or noun.endswith("em") or noun.endswith("es"):
                neutral_base = noun[:-1]
            else:
                neutral_base = noun
            # Künstlich kapitalisierte Adjektive werden wieder kleingeschrieben, ein Beiname
            # ("Peter dem Großen") behält dagegen seine Grossschreibung.
            return True, "", [[0, noun, neutral_base, "", "substantivized adjective", is_epithet]]
        
        # Eigennamen sind markierbar, wenn ein Artikel oder ein Adjektiv an ihnen hängt und der
        # Name als Vor- oder Nachname geführt wird. Die Liste der Personennamen ersetzt die
        # frühere Regel, jedes von ParZu als NE getaggte Wort zu nehmen -- die erfasste auch
        # Länder-, Gewässer- und Organisationsnamen. Namen aus AMBIGUOUS_NAMES sind zugleich
        # gebräuchliche Substantive und zählen nur mit einem Anrede-Adjektiv.
        # Abkürzungen wie "DDR" oder "USA" bezeichnen keine Personen und bleiben unmarkiert.
        # Aus "im engeren Sinne" wurde ohne die Prüfung von name_form "in derm engeren Sinn".
        if noun in Lexicon.MASCULINE_NAMES or name_form in Lexicon.MASCULINE_NAMES:
            is_name = has_masculine_modifier
        elif noun in Lexicon.AMBIGUOUS_NAMES or name_form in Lexicon.AMBIGUOUS_NAMES:
            is_name = has_person_adjective
        else:
            is_name = ((noun in Lexicon.PERSON_NAMES or name_form in Lexicon.PERSON_NAMES
                        or noun in Lexicon.PROPER_NAMES)
                       and (has_article or has_adjective)
                       and noun.lower() not in Lexicon.NO_PERSON_NAMES)
        if is_name and not (len(noun) > 1 and noun.isupper()):
            capitalized = word_parse[1][0].isupper()
            # Die Wortform statt der Grundform: Ein Eigenname bleibt unveraendert stehen, und
            # sonst ginge im Genitiv das "-s" verloren ("des bekannten Eulers" ergaebe "Eulers"
            # -> "Euler"). Wo ParZu falsch lemmatisiert, ist der Schaden groesser.
            return True, "", [[0, word_parse[1], word_parse[1], "", "proper noun", capitalized]]

        prefix, list = Lexicon.check_composite_noun(word_parse[1],True)
        return False, prefix, list


    
    # This function complements the function check_noun. It parses a noun from the back to the front and checks whether
    # there is a person noun in the noun. If there is, it returns a string "prefix" and a list of tuples of the same
    # form as in check_noun. 
    # The first argument is the noun to be parsed. The second argument is a Boolean indicating whether the noun is the
    # head of the nounphrase.
    def check_composite_noun(noun,is_head):
        if noun == "":
            return "", []
        for j in range(len(noun), -1, -1):
            if (is_head and j <= len(noun)-2) or (not is_head and (j == len(noun) or j <= len(noun)-3)):
                for i, line in enumerate(Lexicon.COMPOSITE_NOUNS):
                    if j-len(line) != 1 and noun[:j].lower().endswith(line.lower()) and noun[j:] != "in" and not (noun[j:].lower().startswith("ch") and line.endswith("s")) and not (noun[:j-len(line)].endswith("c") and line.lower().startswith("h")) and not noun[j:j+8] == "lichkeit" and not noun[j:j+3] == "iat" and not noun[j:j+3] == "ium" and not noun[j:j+3] == "ien" and not noun[j:j+7] == "laubnis" and not (noun[j:j+3] == "ung" and (line.lower().endswith("arzt") or line.lower().endswith("bürger") or line.lower().endswith("partner") or line.lower().endswith("inder") or line.lower().endswith("könig"))) and not (noun[:j-len(line)].endswith("h") and line.lower().startswith("enkel")): # The last case is to avoid false positives with "Henkel" and "Schenkel"
                        if Lexicon.NEUTRAL_NOUNS[i].endswith("re"):
                            neutral_core = Lexicon.NEUTRAL_NOUNS[i][:-1] + "ne"
                        else:
                            neutral_core = Lexicon.NEUTRAL_NOUNS[i] + "rne"
                        later_part = noun[j:]
                        if not noun[j-len(line)].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:j-len(line)],False)
                        list.append([j-len(line), noun[j-len(line):j], neutral_core, later_part, "standard", False])
                        return prefix, list
                    
                for pair in Lexicon.ALTERNATIVE_COMPOSITE_NOUNS:
                    i = pair[0]
                    line = pair[1]
                    if j-len(line) != 1 and noun[:j].lower().endswith(line.lower()) and not (noun[j:].lower().startswith("ch") and line.endswith("s")) and not (noun[:j-len(line)].endswith("c") and line.lower().startswith("h")):
                        if Lexicon.NEUTRAL_NOUNS[i].endswith("re"):
                            neutral_core = Lexicon.NEUTRAL_NOUNS[i][:-1] + "ne"
                        else:
                            neutral_core = Lexicon.NEUTRAL_NOUNS[i] + "rne"
                        later_part = noun[j:]
                        if not noun[j-len(line)].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:j-len(line)],False)
                        list.append([j-len(line), noun[j-len(line):j], neutral_core, later_part, "standard", False])
                        return prefix, list
                    
                for i, line in enumerate(Lexicon.FEMALE_NOUNS):
                    if j-len(line) != 1 and noun[:j].lower().endswith(line.lower()) and (line != "Erbin" or noun[j:j+3] == "nen") and (line != "Göttin" or noun[j:j+3] == "nen"):
                        if Lexicon.NEUTRAL_NOUNS[i].endswith("re"):
                            neutral_core = Lexicon.NEUTRAL_NOUNS[i][:-1] + "ne"
                        else:
                            neutral_core = Lexicon.NEUTRAL_NOUNS[i] + "rne"
                        if noun[j:j+3] == "nen":
                            later_part = noun[j+3:]
                        else:
                            later_part = noun[j:]
                        if not noun[j-len(line)].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:j-len(line)],False)
                        list.append([j-len(line), noun[j-len(line):j], neutral_core, later_part, "standard", False])
                        return prefix, list
                    
                for i, neologism in enumerate(Lexicon.NEOLOGISMS):
                    neologism = "(" + neologism + ")$"
                    match = re.search(neologism.lower(), noun[:j].lower())
                    if match:
                        match_position = match.start()
                        found_neologism = match.group(0)
                        if match_position != 1 and not (noun[:match_position].endswith("c") and found_neologism.lower().startswith("h")) and not (noun[j:].lower().startswith("ch") and found_neologism.endswith("s")) and not found_neologism.lower() in ("base", "opa", "oma", "opi", "omi"):
                            neutral_core = Lexicon.NEOLOGISMS_COMPOUND[i]
                            later_part = noun[j:]
                            if (neutral_core == "Elter"
                                    and later_part.lower() in Lexicon.ELTERN_COMPOUNDS):
                                neutral_core = "Eltern"
                            if not noun[match_position].isupper():
                                neutral_core = neutral_core.lower()
                            prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                            list.append([match_position, noun[match_position:j], neutral_core, later_part, "neologism", False])
                            return prefix, list
                    
                person_pattern = r"(männer|frauen|herren|damen)$"
                match = re.search(person_pattern, noun[:j].lower())
                if match:
                    match_position = match.start()
                    if match_position != 1:
                        later_part = noun[j:]
                        neutral_core = "Personen"
                        if not noun[match_position].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                        list.append([match_position, noun[match_position:j], neutral_core, later_part, "person", False])
                        return prefix, list
                
                team_pattern = r"mannschafts?$"
                match = re.search(team_pattern, noun[:j].lower())
                if match:
                    match_position = match.start()
                    if match_position != 1:
                        later_part = noun[j:]
                        neutral_core = "Team"
                        if not noun[match_position].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                        list.append([match_position, noun[match_position:j], neutral_core, later_part, "team", False])
                        return prefix, list

                kind_pattern = r"(töchter|söhne)$"
                match = re.search(kind_pattern, noun[:j].lower())
                if match:
                    match_position = match.start()
                    if match_position != 1:
                        later_part = noun[j:]
                        neutral_core = "Kinder"
                        if not noun[match_position].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                        list.append([match_position, noun[match_position:j], neutral_core, later_part, "kind", False])
                        return prefix, list
                
                beamt_pattern = r"beamt(en|innen)$"
                match = re.search(beamt_pattern, noun[:j].lower())
                if match:
                    match_position = match.start()
                    if match_position != 1:
                        later_part = noun[j:]
                        neutral_core = "Beamterne"
                        if not noun[match_position].isupper():
                            neutral_core = neutral_core.lower()
                        prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                        list.append([match_position, noun[match_position:j], neutral_core, later_part, "beamtey", False])
                        return prefix, list
                
                for i, romanism in enumerate(Lexicon.ROMAN_NOUNS_COMPOUND):
                    romanism = "(" + romanism + ")$"
                    match = re.search(romanism.lower(), noun[:j].lower())
                    if match:
                        match_position = match.start()
                        original = noun[match_position:j]
                        later_part = noun[j:]
                        if match_position != 1 and not (noun[:match_position].endswith("c") and noun[match_position:].lower().startswith("h")) and not (original.lower() == "libera" and later_part.startswith("l")):
                            neutral_core = Lexicon.ROMAN_NOUN_STARTS[i] + "erne"
                            if not noun[match_position].isupper():
                                neutral_core = neutral_core.lower()
                            prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                            list.append([match_position, original, neutral_core, later_part, "romanism", False])
                            return prefix, list
                    
                for i, irregular_noun in enumerate(Lexicon.IRREGULAR_NOUNS_COMPOUND):
                    irregular_noun = "(" + irregular_noun + ")$"
                    match = re.search(irregular_noun.lower(), noun[:j].lower())
                    if match:
                        match_position = match.start()
                        if match_position != 1 and not (noun[:match_position].endswith("c") and noun[match_position:].lower().startswith("h")) and not (noun[:match_position].lower().endswith("zus") and noun[match_position:].lower().startswith("ammen")):
                            if Lexicon.IRREGULAR_NOUNS_NEUTRAL[i].endswith("re"):
                                neutral_core = Lexicon.IRREGULAR_NOUNS_NEUTRAL[i][:-1] + "ne"
                            else:
                                neutral_core = Lexicon.IRREGULAR_NOUNS_NEUTRAL[i] + "rne"
                            later_part = noun[j:]
                            if not noun[match_position].isupper():
                                neutral_core = neutral_core.lower()
                            prefix, list = Lexicon.check_composite_noun(noun[:match_position],False)
                            list.append([match_position, noun[match_position:j], neutral_core, later_part, "irregular", False])
                            return prefix, list

        return noun, []
            
    # This creates a neutralized noun based on which components were selected. Apart from the noun it returns two Booleans:
    # - head_selected indicates whether the head of the noun phrase was selected and changed into inklusivum.
    # - person indicates whether the head was changed into "Person", so that dependent modifiers need to be made feminine.
    # - kind indicates whether the head was changed into "Kind", so that dependent modifiers need to be made neuter.
    def make_neutralized_noun(pos,selected_components,nounlist,feats,has_article,has_marked_article=False):
        head_selected = False
        person = False
        kind = False
        junge_person = False
        noun = ""
        all_components = []
        for nouninfo in nounlist:
            if nouninfo[0] == pos+1:
                all_components.append(nouninfo)
        print("all_components:")
        print(all_components)
        print("selected_components:")
        print(selected_components)
        for i, component in enumerate(all_components):
            if i in selected_components:
                if i == len(all_components)-1 and component[-1] == True:
                    head_selected = True
                    j = component[3]
                    if component[-3] == "neologism":
                        head = Lexicon.neutralize_neologism(feats, j)
                        # Behält der Neologismus seinen eigenen Artikel, dürfen die abhängigen
                        # Wörter nicht neutralisiert werden; head_selected steuert das.
                        if Lexicon.NEOLOGISMS_NEUTRAL[j] in Lexicon.NEOLOGISMS_KEEP_ARTICLE:
                            head_selected = False
                    elif component[-3] == "person":
                        # if plural, head is "Leute", otherwise "Person"
                        if feats[2] == "Pl" and feats[1] != "Dat":
                            head = "Leute"
                        elif feats[2] == "Pl" and feats[1] == "Dat":
                            head = "Leuten"
                        else:
                            head = "Person"
                            head_selected = False
                            person = True
                    elif component[-3] == "junge_person":
                        # Im Plural "junge Leute", im Singular "junge Person" (mit femininer Kongruenz).
                        if feats[2] == "Pl":
                            adjective = "jungen" if has_article else "junge"
                            head = adjective + (" Leuten" if feats[1] == "Dat" else " Leute")
                        else:
                            if feats[1] == "_":
                                feats[1] = "Nom"
                            if feats[1] == "Nom" or feats[1] == "Acc":
                                adjective = "junge"
                            else:
                                adjective = "jungen" if has_article else "junger"
                            head = adjective + " Person"
                            head_selected = False
                            person = True
                            junge_person = True
                    elif component[-3] == "team":
                        # "das Team", Genitiv "des Teams", Plural "die Teams".
                        if feats[2] == "Pl":
                            head = "Teams"
                        else:
                            if feats[1] == "_":
                                feats[1] = "Nom"
                            head = "Teams" if feats[1] == "Gen" else "Team"
                            head_selected = False
                            kind = True
                    elif component[-3] == "mensch":
                        # "Mensch" wird schwach dekliniert: der Mensch, aber des/dem/den Menschen.
                        if feats[1] == "_":
                            feats[1] = "Nom"
                        if feats[2] == "Pl" or feats[1] in ("Gen", "Dat", "Acc"):
                            head = "Menschen"
                        else:
                            head = "Mensch"
                        # "Mensch" ist ein Maskulinum und behält es, so wie "-person" das
                        # Femininum bekommt. head_selected verhindert, dass die abhängigen
                        # Wörter neutralisiert werden.
                        head_selected = False
                    elif component[-3] == "kind":
                        # if plural, head is "Kinder", otherwise "Kind"
                        if feats[2] == "Pl" and feats[1] != "Dat":
                            head = "Kinder"
                        elif feats[2] == "Pl" and feats[1] == "Dat":
                            head = "Kindern"
                        elif feats[2] == "Sg" and feats[1] == "Gen":
                            head = "Kindes"
                            head_selected = False
                            kind = True
                        else:
                            head = "Kind"
                            head_selected = False
                            kind = True
                    elif component[-3] == "beamtey":
                        if feats[2] == "Pl":
                            head = "Beamternen" if feats[1] == "Dat" else "Beamterne"
                        else:
                            if feats[1] == "_":
                                feats[1] = "Nom"
                            # Wie beim substantivierten Adjektiv: "das Beamter" gibt es nicht,
                            # der Artikel gehört dann nicht zu diesem Wort.
                            strong_ending = component[2].lower().endswith("beamter")
                            if has_article and not (strong_ending and has_marked_article):
                                if feats[1] == "Nom" or feats[1] == "Acc": 
                                    head = "Beamte"
                                else:
                                    head = "Beamten"
                            else:
                                head = "Beamt" + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
                    elif component[-3] == "neutral":
                        head = j
                    elif component[-3] == "substantivized adjective":
                        if j.endswith("e"):
                            head_base = j
                        else:
                            head_base = j + "e"
                        if feats[1] == "_":
                            feats[1] = "Nom"
                        # Trägt die Eingabeform die starke Endung "-er", kann ein Artikel, der Genus
                        # und Kasus selbst anzeigt, nicht zu ihr gehören -- "das Zweiterer" gibt es
                        # nicht. In Relativsätzen hängt ParZu aber genau solche Artikel an, und die
                        # Nominalphrase würde dann fälschlich schwach flektiert. Nach dem
                        # ein-Paradigma bleibt es schwach, weil das Inklusivum dort bewusst von der
                        # Standardgrammatik abweicht ("ein Jugendlicher" wird zu "ein Jugendliche").
                        strong_ending = component[2].lower().endswith(j.lower() + "r")
                        # Weak Flexion, after article
                        if has_article and not (strong_ending and has_marked_article):
                            if feats[1] == "Nom" or feats[1] == "Acc": 
                                head = head_base
                            else:
                                head = head_base + "n"
                        # Strong Flexion, on it's own
                        else:
                            head = head_base[:-1] + Lexicon.case_ending(Lexicon.ARTIKEL_JEDER, feats[1])
                    elif component[-3] == "proper noun":
                        head = j
                    else:
                        if component[-3] == "standard":
                            head_base = Lexicon.NEUTRAL_NOUNS[j]
                        elif component[-3] == "romanism":
                            head_base = Lexicon.ROMAN_NOUN_STARTS[j] + "e"
                        elif component[-3] == "irregular":
                            head_base = Lexicon.IRREGULAR_NOUNS_NEUTRAL[j]

                        
                        if feats[2] == "Pl":
                            # Nur der Typ "standard" hat einen Eintrag in MALE_NOUNS.
                            if component[-3] == "standard":
                                head_base = Lexicon.apply_plural_umlaut(head_base, component[2], Lexicon.MALE_NOUNS[j])
                            if feats[1] ==  "Dat":
                                if head_base.endswith("re"):
                                    head = head_base[:-1] + "nen"
                                else:
                                    head = head_base + "rnen"
                            else:
                                if head_base.endswith("re"):
                                    head = head_base[:-1] + "ne"
                                else:
                                    head = head_base + "rne"
                        else:
                            if feats[1] == "Gen":
                                head = head_base + "s"
                            else:
                                head = head_base
                    if component[-2] == False:
                        head = head.lower()
                    noun += head
                else:
                    noun += component[3] + component[4]
            else:
                noun += component[2] + component[4]
        return noun, head_selected, person, kind, junge_person
    
    def __init__(self):
        pass
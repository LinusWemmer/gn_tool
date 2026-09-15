from lexicon import Lexicon
from lexicon_fem import Lexicon_Fem
from lexicon_neuter import Lexicon_Neuter
from html import escape
import re

# The Marking_tool class is a class that stores the parsing data for a sentence.
# It also has functionality to work with the data:
#   - finding nounphrases
#   - getting the sentence from the parse
#   - converting a nounphrase into the inklusive form based on the de-e System.

class Marking_Tool:
    # nounphrases und nounlist sind bewusst auf None vorbelegt: Ein veränderliches Standardobjekt
    # wird in Python nur einmal beim Laden der Datei erzeugt und von allen Aufrufen geteilt, die
    # das Argument weglassen. Ein Satz würde dann Einträge eines früheren Satzes erben, und weil
    # der Arbeitsprozess der App über Anfragen hinweg lebt, sogar über Anfragen hinweg.
    # Übergebene Objekte werden weiterhin per Referenz gehalten -- die Wiederherstellung aus der
    # Session gibt Objekte herein, die die Instanz anschliessend verändert.
    def __init__(self, parse_list, nounphrases = None, nounlist = None, noun_pair_spans = None):
    
        # List of the conll parse strings split into a list 
        # The format of the list is as follows (conll format):
        # 0:POSTION 1:FORM 2:STEM 3:CPOSTAG 4:POSTAG 5:FEATS 6:HEAD 7:DEPREL 8:PHEAD
        self.parse_list = parse_list
        self.nounphrases = {} if nounphrases is None else nounphrases
        # nounlist is a list of lists, where each list contains the following information about a noun:
        # [word_index_from_1, position_of_noun_in_composite_noun, original, neutralized, suffix, noun_type, capitalized, head_identified_as_person_noun]
        self.nounlist = [] if nounlist is None else nounlist
        # Indizes der Substantive, die ein Kästchen bekommen haben. nounlist taugt dafür nicht:
        # Dort landet für jedes Substantiv ein "prefix"-Eintrag, auch für nicht markierbare.
        self.marked_nouns = []
        # Zu jeder Doppelnennung die Positionen, die in ihrem Kästchen aufgehen: die Konjunktion,
        # ein etwaiger zweiter Artikel und das zweite Substantiv. Schlüssel ist die 1-basierte
        # Position des ersten Substantivs. Diese Wörter dürfen erst dann aus dem Ausgabetext
        # verschwinden, wenn das Kästchen auch ausgewählt wurde.
        self.noun_pair_spans = {} if noun_pair_spans is None else noun_pair_spans
        self.repair_pronominal_articles()
        self.repair_detached_articles()
        self.repair_detached_possessives()
        self.repair_detached_relative_pronouns()
        self.repair_apposition_before_name()
        self.repair_predicate_after_sein()
        self.find_nounphrases()

    # "der Oppositionspolitiker Igor Lednik" liest ParZu als Genitiv Plural -- die Form "der" ist
    # dort nicht von der des maskulinen Nominativ Singular zu unterscheiden. Folgt auf das
    # Substantiv ein Personenname, ist die Apposition gemeint und damit der Singular. Ohne diese
    # Prüfung wurde daraus "der Oppositionspolitikerne".
    def repair_apposition_before_name(self):
        for pos, word_parse in enumerate(self.parse_list[:-1]):
            feats = word_parse[5].split("|")
            if word_parse[3] != "N" or feats[-2:] != ["Gen", "Pl"]:
                continue
            following = self.parse_list[pos+1]
            if following[4] != "NE" or not (following[1] in Lexicon.PERSON_NAMES
                                            or following[1] in Lexicon.PROPER_NAMES):
                continue
            # Ein echtes Genitivattribut modifiziert ein Substantiv ("das Gericht der
            # Nationalsozialisten"). Hängt es an etwas anderem -- im Beispielsatz an der Jahreszahl
            # "2024" --, ist die Genitivlesart nicht zu halten und die Apposition gemeint.
            head = int(word_parse[6]) if word_parse[6].isdigit() else 0
            if head != 0 and self.parse_list[head-1][3] == "N":
                continue
            feats[-2:] = ["Nom", "Sg"]
            word_parse[5] = "|".join(feats)
            for other in self.parse_list:
                if other[6] == word_parse[0] and other[3] == "ART":
                    article_feats = other[5].split("|")
                    if article_feats[-2:] == ["Gen", "Pl"]:
                        article_feats[-2:] = ["Nom", "Sg"]
                        other[5] = "|".join(article_feats)

    # "Damals waren es Soldaten aus den USA" -- ParZu macht "Soldaten" zum Dativobjekt von "sein".
    # Ein Dativ bei "sein" begleitet aber immer ein Prädikativ ("Das ist Kindern egal"); fehlt
    # das, ist das Substantiv selbst das Prädikatsnomen und steht im Nominativ. Ohne diese
    # Prüfung wurde daraus der Dativ Plural "Soldaternen".
    def repair_predicate_after_sein(self):
        for word_parse in self.parse_list:
            if word_parse[3] != "N" or word_parse[7] != "objd" or word_parse[6] == "0":
                continue
            verb = self.parse_list[int(word_parse[6])-1]
            if verb[2] != "sein":
                continue
            if any(other[6] == verb[0] and other[7] == "pred" for other in self.parse_list):
                continue
            feats = word_parse[5].split("|")
            if len(feats) >= 2 and feats[-2] == "Dat":
                feats[-2] = "Nom"
                word_parse[5] = "|".join(feats)

    # Bindet ParZu ein Relativpronomen gar nicht an, fehlt ihm auch der Numerus, und es wird als
    # Singular behandelt -- also markierbar, obwohl es sich auf einen Plural bezieht: In "...
    # werden Bezeichnungsformen verwendet, die mit dem Geschlecht ... übereinstimmen" wurde aus
    # "die" ein "de". Das Bezugswort eines Relativpronomens ist im Regelfall das nächste
    # vorangehende Substantiv; dessen Numerus wird deshalb übernommen.
    def repair_detached_relative_pronouns(self):
        for pos, word_parse in enumerate(self.parse_list):
            if word_parse[4] != "PRELS" or word_parse[6] != "0":
                continue
            if word_parse[5].split("|")[-1] != "_":
                continue
            for other in reversed(self.parse_list[:pos]):
                if other[3] == "N":
                    number = other[5].split("|")[-1]
                    if number in ("Sg", "Pl"):
                        feats = word_parse[5].split("|")
                        feats[-1] = number
                        word_parse[5] = "|".join(feats)
                    break

    # ParZu liest das Dativpronomen "ihr" gelegentlich als Possessivform ("Kannst Du ihr bitte
    # sagen, dass ich komme"). Daraus wurde dann "ens" statt "em". Eine echte Possessivform
    # bestimmt immer ein Substantiv und hängt als "det" daran; bleibt sie unangebunden, bestimmt
    # sie nichts und ist in Wahrheit das Pronomen. Das "ihr" der zweiten Person Plural ist davon
    # nicht betroffen, das gibt ParZu als "2|Pl|_|Nom" aus.
    def repair_detached_possessives(self):
        for word_parse in self.parse_list:
            if (word_parse[4] == "PPOSAT" and word_parse[1].lower() == "ihr"
                    and word_parse[6] == "0"):
                word_parse[3] = "PRO"
                word_parse[4] = "PPER"
                word_parse[5] = "3|Sg|_|Dat"

    # ParZu bindet einen Artikel gelegentlich gar nicht an und deutet ihn als Pronomen ("...,
    # ihr die Bücher nach Hause zu tragen"). Das Substantiv dahinter verliert dadurch seinen
    # Artikel -- es wird nicht mitneutralisiert -- und der vermeintliche Pronomen-Artikel wird
    # fälschlich selbst markierbar. Steht ein solcher Artikel unmittelbar vor einem Substantiv,
    # das noch keinen hat, wird er diesem zugeschlagen.
    # Hängt der Artikel dagegen an einer Konjunktion ("..., und der Vater hatte..."), bleibt er
    # unangetastet: Dort liegt ParZu meist auch beim Kasus des Substantivs daneben, und der
    # Artikel bekäme dann die falsche Form.
    def repair_detached_articles(self):
        for pos, word_parse in enumerate(self.parse_list[:-1]):
            if word_parse[1].lower() not in ("der", "die", "das", "den", "dem", "des"):
                continue
            head = int(word_parse[6]) if word_parse[6].isdigit() else 0
            if head != 0 and self.parse_list[head-1][3] != "KON":
                continue
            following = self.parse_list[pos+1]
            if following[3] != "N":
                continue
            # Nur wenn das Substantiv noch keinen Artikel hat.
            if any(other[6] == following[0] and other[3] == "ART" for other in self.parse_list):
                continue
            word_parse[3] = "ART"
            word_parse[4] = "ART"
            word_parse[6] = following[0]
            word_parse[7] = "det"
            # Hängt der Artikel an einer Konjunktion, liegt ParZu oft auch beim Kasus des
            # Substantivs daneben. Die Artikelform schränkt ihn aber ein: "der" vor einem
            # Maskulinum kann nur Nominativ sein, "den" nur Akkusativ.
            if head != 0:
                noun_feats = following[5].split("|")
                if len(noun_feats) >= 3 and noun_feats[0] == "Masc":
                    erzwungen = {"der": "Nom", "den": "Acc", "dem": "Dat", "des": "Gen"}.get(
                        word_parse[1].lower())
                    if erzwungen and noun_feats[1] != erzwungen:
                        noun_feats[1] = erzwungen
                        following[5] = "|".join(noun_feats)

    # ParZu liest "der andere" in "Der eine kam, der andere ging." nicht als Nominalphrase aus
    # Artikel und substantiviertem Adjektiv, sondern als Relativpronomen im Dativ plus
    # Indefinitpronomen. Die Neutralisierung ergab dadurch "derm anderey" statt "de andere".
    # Erkennbar ist der Fall daran, dass ein als Relativpronomen getaggtes "der", "die" oder "das"
    # unmittelbar vor einem singularischen "eine" oder "andere" steht, das ParZu als Subjekt
    # desselben Kopfes führt. Als Relativsatz kommt diese Folge kaum vor ("die Frau, der andere
    # half"), als Nominalphrase dagegen häufig. Die Endung auf "-e" grenzt sie zusätzlich ab:
    # Nach einem bestimmten Artikel steht die schwache Form, "der einer" gibt es nicht.
    def repair_pronominal_articles(self):
        for pos, word_parse in enumerate(self.parse_list[:-1]):
            following = self.parse_list[pos+1]
            if (word_parse[4] == "PRELS" and word_parse[1].lower() in ("der", "die", "das")
                    and word_parse[7] != "subj"
                    and following[4] == "PIS" and following[2] in ("andere", "eine")
                    and following[1].lower().endswith("e") and "Pl" not in following[5]
                    and following[7] == "subj"
                    # Das Relativpronomen hängt entweder am selben Kopf wie das Indefinitpronomen
                    # oder, wenn ParZu es gar nicht anbinden konnte, an der Satzwurzel.
                    and word_parse[6] in ("0", following[6])):
                word_parse[3] = "ART"
                word_parse[4] = "ART"
                word_parse[5] = "Def|" + following[5]
                word_parse[6] = following[0]
                word_parse[7] = "det"

    # Determinierer, die im Maskulinum Nominativ und im Neutrum endungslos sind. Nach ihnen
    # steht das folgende Adjektiv in der starken Deklination und trägt das Genus selbst.
    ENDINGLESS_DETERMINERS = ("ein", "mein", "dein", "sein", "ihr", "unser", "euer", "kein")

    # Zeichen, die im Eingabetext unmittelbar auf ein Wort folgen dürfen. find_realizations
    # sucht jedes Wort des Parses im Eingabetext wieder und prüft dabei, dass dahinter eines
    # dieser Zeichen oder das Textende steht. Fehlt ein Zeichen, wird das Wort nicht gefunden
    # und die Zuordnung bricht mit einer Ausnahme ab: "Das Wort “gender” ist schwierig."
    # scheiterte daran, dass das schliessende typografische Anführungszeichen fehlte. Die Liste
    # stand früher an zwei Stellen doppelt und war dabei nicht einmal deckungsgleich.
    WORD_DELIMITERS = r"[\s.,!?;:‑–—„“”‚‘’»«›‹'\"(){}<>|\[\]+/*_…]"

    # ParZu lässt den Kasus bei substantivierten Adjektiven häufig offen ("meiner Lieben" liefert
    # "_|_|_"). Die Dependenzrelation des Kopfes verrät ihn aber.
    DEPREL_CASES = {"subj": "Nom", "pred": "Nom", "obja": "Acc", "objd": "Dat", "objg": "Gen", "gmod": "Gen"}

    # Präpositionen, nach denen ein von ParZu nicht erkannter Kasus als Dativ gelesen wird. Die
    # übrigen Wechselpräpositionen ("an", "auf", "in", "über") regieren in dieser Lage eher den
    # Akkusativ; siehe die Kasusergänzung in neutralize_nounphrase.
    DATIVE_PREPOSITIONS = ("zwischen", "unter", "vor", "hinter", "neben", "von", "bei")

    # Praepositionen, die ausschliesslich den Dativ regieren. ParZu laesst bei "von" den Kasus
    # offen; weil "von" zugleich in DATIVE_PREPOSITIONS steht, unterblieb die Kasus-Ergaenzung
    # ersatzlos und der Dativ ging verloren: "Das Buch von der Tochter" wurde zu "von das Kind",
    # "von der Lehrerin" zu "von de Lehrere" statt "von derm Lehrere".
    DATIVE_ONLY_PREPOSITIONS = ("von", "bei", "aus", "mit", "nach", "seit", "zu",
                                "außer", "gegenüber", "entgegen", "gemäß")

    # Praeposition und dativisches "dem" ziehen sich im Deutschen zusammen. Bisher tat das nur
    # "zu" + "dem"; "von dem Kind" blieb stehen, statt zu "vom Kind" zu werden. "vorm", "ueberm",
    # "unterm" und "hinterm" fehlen hier mit Absicht -- sie sind umgangssprachlich. Steht die
    # Zusammenziehung schon im Eingabetext, hat split_prepositions sie zerlegt und die
    # Realisierungen ("vo" und "m") ergeben sie von selbst wieder.
    DATIVE_CONTRACTIONS = {"an": "am", "bei": "beim", "in": "im", "von": "vom", "zu": "zum"}

    # Dasselbe fuer den Akkusativ mit "das". Hier bleibt die Praeposition vollstaendig, es kommt
    # nur das "s" des Artikels hinzu. "vors", "uebers", "unters" und "hinters" fehlen wieder als
    # umgangssprachliche Formen.
    ACCUSATIVE_CONTRACTIONS = {"an": "ans", "in": "ins", "auf": "aufs", "für": "fürs",
                               "um": "ums", "durch": "durchs"}

    # Der Kasus steht je nach Wortart an unterschiedlicher Stelle der Merkmalsliste:
    # "Fem|Dat|Sg" und "_|_|_" haben ihn an Position 1, "Def|Fem|Dat|Sg" und
    # "Pos|Neut|Acc|Sg|St|" an Position 2.
    def case_index(self, pos:int) -> int:
        return 1 if len(self.parse_list[pos][5].split("|")) == 3 else 2

    def get_case(self, pos:int) -> str:
        feats = self.parse_list[pos][5].split("|")
        index = self.case_index(pos)
        return feats[index] if len(feats) > index else "_"

    # Trägt einen Kasus nach, sofern die Zeile noch keinen hat.
    def set_missing_case(self, pos:int, case:str):
        feats = self.parse_list[pos][5].split("|")
        index = self.case_index(pos)
        if len(feats) > index and feats[index] == "_":
            feats[index] = case
            self.parse_list[pos][5] = "|".join(feats)

    def serialize(self):
        return {"parse_list": self.parse_list,
                "nounphrases": self.nounphrases}

    # Returns the output sentence.
    # Gibt den Satz als HTML zurück und hebt hervor, was sich gegenüber dem Eingabetext geändert
    # hat. Verglichen wird über das gemeinsame Wortanfang- und Wortende-Stück, sodass nur der
    # geänderte Teil farbig wird: "Nachbarin" ergibt "Nachbar" plus hervorgehobenes "e", "Mutter"
    # ergibt hervorgehobenes "El" plus "ter". Wird nur gestrichen, ohne dass etwas hinzukommt
    # ("der" zu "de"), bleibt kein Stück zum Hervorheben übrig -- dann wird das ganze Wort
    # hervorgehoben, damit die Änderung überhaupt sichtbar ist.
    @staticmethod
    def highlight_change(original: str, neutralized: str) -> str:
        if original == neutralized:
            return escape(neutralized)
        # Die Pronomen "en" und "em" werden immer ganz hervorgehoben. Sonst sähe ein "en" aus
        # "er" anders aus als eines aus "sie" oder "ihn": Beim gemeinsamen Anfang "e" bliebe nur
        # das "n" farbig. Dasselbe gilt für "em" aus "ihm" gegenüber "em" aus "ihr".
        if neutralized in ("en", "En", "em", "Em"):
            return f'<span class="changed">{escape(neutralized)}</span>'
        if neutralized == "":
            # Ganz gestrichene Wortformen ergäben ein leeres Element, etwa bei der Zusammenführung
            # einer Doppelnennung ("Bürgerinnen und Bürger" wird zu "Bürgerne").
            return ""
        limit = min(len(original), len(neutralized))
        prefix = 0
        while prefix < limit and original[prefix] == neutralized[prefix]:
            prefix += 1
        suffix = 0
        while (suffix < limit - prefix
               and original[len(original)-1-suffix] == neutralized[len(neutralized)-1-suffix]):
            suffix += 1
        changed = neutralized[prefix:len(neutralized)-suffix]
        if changed == "":
            return f'<span class="changed">{escape(neutralized)}</span>'
        return (escape(neutralized[:prefix])
                + f'<span class="changed">{escape(changed)}</span>'
                + escape(neutralized[len(neutralized)-suffix:]))

    # Wie get_sentence, aber als HTML mit hervorgehobenen Änderungen. Das Argument enthält die
    # Wortformen vor der Neutralisierung, in derselben Reihenfolge wie parse_list.
    def get_highlighted_sentence(self, original_realizations) -> str:
        sentence = ""
        for i, word_parse in enumerate(self.parse_list):
            original = original_realizations[i] if i < len(original_realizations) else word_parse[-2]
            sentence += Marking_Tool.highlight_change(original, word_parse[-2])
            sentence += escape(word_parse[-1])
        return sentence

    def get_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            sentence += word_parse[-2]
            sentence += word_parse[-1]
        return sentence
    
    # Returns the input sentence with slight modifications for reparsing.
    def get_internal_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            if (len(word_parse[-2]) != len(word_parse[1]) and not word_parse[2] == "glauben" and not word_parse[2] == "zeigen") or word_parse[1] == '"':
                sentence = sentence + word_parse[-2]
            else:
                sentence += word_parse[1]
            sentence += word_parse[-1]
        return sentence

    # Adds all nounphrases to the dictionary "nounphrases". 
    def find_nounphrases(self):
        for word_parse in self.parse_list:
            if word_parse[3] == "N" or word_parse[3] == "PRO":
                self.find_nounphrase(word_parse)

    # Adds a single nounphrase to the dictionary "nounphrases". The key is
    # the index of the head of the nounphrase, while the value is the list of
    # all indices of its children.
    def find_nounphrase(self, word_parse):
        # If the word isn't yet in the dictionary, we add it.
        if int(word_parse[0]) not in self.nounphrases:
            self.nounphrases[int(word_parse[0])] = self.find_children(word_parse[0],False)
        print(self.nounphrases)

    # Ein Relativpronomen braucht kein eigenes Kästchen, wenn es schon als abhängiges Wort einer
    # markierten Nominalphrase erfasst ist. In "einen Sohn, Max, der 1863 geboren wurde" hängt es
    # über die Apposition an "Sohn" und wird mit diesem neutralisiert; ein eigenes Kästchen würde
    # dessen Kongruenz überschreiben, denn "ein Kind" verlangt "das" und nicht "de". Hängt es
    # dagegen an einem nicht markierbaren Namen ("Kim, die gestern kam"), bleibt es nötig.
    def covered_by_marked_nounphrase(self, word_parse) -> bool:
        index = int(word_parse[0])
        return any(index in self.nounphrases.get(marked, []) for marked in self.marked_nouns)

    # Sammelt die Relativpronomen der Relativsätze, die an den Appositionen unterhalb von "pos"
    # hängen. Appositionen können gestaffelt sein ("der Lehrerin, Frau Meier"), deshalb wird die
    # Kette ganz verfolgt.
    def find_apposition_relatives(self, pos: str, preposition: bool):
        children = []
        for word_parse in self.parse_list:
            if word_parse[6] == pos and word_parse[3] == "N" and word_parse[7] == "app":
                for relative_parse in self.parse_list:
                    if relative_parse[6] == word_parse[0] and relative_parse[7] == "rel":
                        children.extend(self.find_children(relative_parse[0], preposition))
                children.extend(self.find_apposition_relatives(word_parse[0], preposition))
        return children

    # The last argument keeps track of whether we have traversed a preposition in the parse tree.
    def find_children(self, pos: str, preposition: bool):
        children = []
        for word_parse in self.parse_list:
            if word_parse[6] == pos and word_parse[3] != "N":
                # Once we have traversed a preposition, we only include relative pronouns:
                if not preposition or word_parse[4] == "PRELS":
                    children.append(int(word_parse[0]))
                if word_parse[3] == "PREP":
                    children.extend(self.find_children(word_parse[0],True))
                else:
                    children.extend(self.find_children(word_parse[0],preposition))
                # In relative sentences that depend on the noun phrase, we want to include the relative pronoun, but nothing else.
                if word_parse[4] == "PRELS":
                    break
            #else:
            #    children.extend(self.find_dessen(word_parse[0]))
        # Ein Relativsatz an einer Apposition gehört zur Nominalphrase ihres Kopfes, denn die
        # Apposition bezeichnet dieselbe Person: In "eine Tochter, Ida, hatte, die 1863 geboren
        # wurde" hängt der Relativsatz an "Ida" und meint damit die Tochter. Zugerechnet wird er
        # nur dem Kopf der Appositionskette -- richtete sich das Relativpronomen nach einer
        # Apposition, die selbst umgeschrieben wird, ergäbe "der Lehrerin, Frau Meier, die kam"
        # ein "Person Meier, die kam" statt des zum Kopf passenden "Lehrere, de kam".
        # Andere abhängige Substantive bleiben aussen vor, weil ihr Relativsatz sich auf sie
        # selbst bezieht ("das Buch der Lehrerin, die ...").
        if self.parse_list[int(pos)-1][3] == "N" and self.parse_list[int(pos)-1][7] != "app":
            children.extend(self.find_apposition_relatives(pos, preposition))
        # If the word is a noun followed by a comma followed by an independent der/die/das, the independent der/die/das should be added to childen
        if len(self.parse_list) >= int(pos)+2 and self.parse_list[int(pos)-1][3] == "N" and self.parse_list[int(pos)][1] == "," and self.parse_list[int(pos)+1][2] in ["der","die","das"] and self.parse_list[int(pos)+1][6] == "0":
            children.append(int(self.parse_list[int(pos)+1][0]))
        return children
    
    # search_lonely_adjectives schreibt allein stehende Adjektive vor dem Reparse gross, damit
    # ParZu sie als substantiviert erkennt; mark_nouns macht das an der Realisierung rückgängig,
    # nicht aber an der Wortform. Steht die Wortform gross und die Realisierung klein, ist die
    # Grossschreibung künstlich und darf nicht in die Ausgabe gelangen: "der andere ging" ergab
    # sonst "derm Anderey".
    def artificially_capitalized(self, pos:int) -> bool:
        word_parse = self.parse_list[pos]
        return word_parse[1][:1].isupper() and word_parse[-2][:1].islower()

    # split_prepositions hat "im", "am" und "vom" in zwei Woerter zerlegt; vom ersten steht im
    # Eingabetext nur das Bruchstueck "i", "a" oder "vo". Zieht sich der Artikel nicht wieder mit
    # der Praeposition zusammen (wie "zu" + "derm" zu "zurm"), muss die Praeposition wieder
    # vollstaendig werden -- sonst entsteht "vo der Kaufperson" statt "von der Kaufperson".
    PREPOSITION_FRAGMENTS = {"i": "in", "I": "In", "vo": "von", "Vo": "Von", "a": "an", "A": "An"}

    def restore_split_preposition(self, pos:int):
        if pos == 0:
            return
        self.parse_list[pos-1][-1] = " "
        fragment = self.parse_list[pos-1][-2]
        if fragment in Marking_Tool.PREPOSITION_FRAGMENTS:
            self.parse_list[pos-1][-2] = Marking_Tool.PREPOSITION_FRAGMENTS[fragment]

    # This function neutralizes the word that has been selected.
    def neutralize_word(self, pos:int, has_article:bool, article_pos:int):
        word_parse = self.parse_list[pos]
        was_artificially_capitalized = self.artificially_capitalized(pos)
        if word_parse[3] == "ADJA":
            self.parse_list[pos][-2] = Lexicon.neutralize_adjectives(word_parse, has_article)
        elif word_parse[4] == "PIDAT" and pos != article_pos-1:
            # This case covers morphologically adjectival determiners like the word "jeden" in "eines jeden Bürgers".
            # Since the feature list of a PIDAT determiner has a differnt structure than that of an
            # adjective, we need to first adapt its structure:
            word_parse[5] = "POS|" + word_parse[5] + "|_|"
            if word_parse[2] != "alle":
                if word_parse[2].endswith("e"):
                    word_parse[2] = word_parse[2][:-1]
                self.parse_list[pos][-2] = Lexicon.neutralize_adjectives(word_parse, has_article)
        else:
            neutralized_word = Lexicon.neutralize_word(self.parse_list[pos],has_article)
            if neutralized_word == "derm" and (self.parse_list[pos-1][1] == "Zu" or self.parse_list[pos-1][1] == "zu"):
                self.parse_list[pos-1][-1] = ""
                self.parse_list[pos][-2] = "rm"
            elif neutralized_word == self.parse_list[pos][1]:
                # Der Artikel selbst aendert sich nicht. Dann bleibt auch seine Schreibung aus dem
                # Eingabetext unangetastet -- vor allem eine Zusammenziehung mit der Praeposition:
                # "fuers Erste" wurde sonst zu "fuerdas Erste".
                pass
            elif self.parse_list[pos][-2] in ("r", "m", "s"):
                # split_prepositions hat die Zusammenziehung zerlegt und die neue Artikelform passt
                # nicht mehr hinein; die Praeposition muss wieder vollstaendig werden.
                self.restore_split_preposition(pos)
                self.parse_list[pos][-2] = neutralized_word
            else:
                self.parse_list[pos][-2] = neutralized_word
        if was_artificially_capitalized and self.parse_list[pos][-2][:1].isupper():
            self.parse_list[pos][-2] = (self.parse_list[pos][-2][:1].lower()
                                        + self.parse_list[pos][-2][1:])

    # This function feminizes the word that has been selected.
    def feminize_word(self, pos:int, has_article:bool, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to be included when neutralizing the word.
            self.parse_list[pos][-2] = Lexicon_Fem.feminize_adjectives(word_parse, has_article)
        elif word_parse[4] == "PIDAT" and pos != article_pos-1:
            # This case covers morphologically adjectival determiners like the word "jeden" in "einem jeden Mann".
            # Since the feature list of a PIDAT determiner has a differnt structure than that of an
            # adjective, we need to first adapt its structure:
            word_parse[5] = "POS|" + word_parse[5] + "|_|"
            if word_parse[2] != "alle":
                if word_parse[2].endswith("e"):
                    word_parse[2] = word_parse[2][:-1]
                self.parse_list[pos][-2] = Lexicon_Fem.feminize_adjectives(word_parse, has_article)
        else:
            feminized_word = Lexicon_Fem.feminize_word(self.parse_list[pos],has_article)
            if feminized_word == "der" and (self.parse_list[pos-1][1] == "Zu" or self.parse_list[pos-1][1] == "zu"):
                self.parse_list[pos-1][-1] = ""
                self.parse_list[pos][-2] = "r"
            elif feminized_word == self.parse_list[pos][1]:
                # Der Artikel selbst aendert sich nicht. Dann bleibt auch seine Schreibung aus dem
                # Eingabetext unangetastet -- vor allem eine Zusammenziehung mit der Praeposition:
                # "fuers Erste" wurde sonst zu "fuerdas Erste".
                pass
            elif self.parse_list[pos][-2] in ("r", "m", "s"):
                # split_prepositions hat die Zusammenziehung zerlegt und die neue Artikelform passt
                # nicht mehr hinein; die Praeposition muss wieder vollstaendig werden.
                self.restore_split_preposition(pos)
                self.parse_list[pos][-2] = feminized_word
            else:
                self.parse_list[pos][-2] = feminized_word

    # This function makes the word that has been selected neuter.
    def neuterize_word(self, pos:int, has_article:bool, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to be included when neutralizing the word.
            self.parse_list[pos][-2] = Lexicon_Neuter.neuterize_adjectives(word_parse, has_article)
        elif word_parse[4] == "PIDAT" and pos != article_pos-1:
            # This case covers morphologically adjectival determiners like the word "jeden" in "einem jeden Mann".
            # Since the feature list of a PIDAT determiner has a differnt structure than that of an
            # adjective, we need to first adapt its structure:
            word_parse[5] = "POS|" + word_parse[5] + "|_|"
            if word_parse[2] != "alle":
                if word_parse[2].endswith("e"):
                    word_parse[2] = word_parse[2][:-1]
                self.parse_list[pos][-2] = Lexicon_Neuter.neuterize_adjectives(word_parse, has_article)
        else:
            neuter_word = Lexicon_Neuter.neuterize_word(self.parse_list[pos],has_article)
            print("neuter_word:",neuter_word)
            contraction = None
            if pos > 0 and self.parse_list[pos-1][3] == "PREP":
                preposition = self.parse_list[pos-1][2].lower()
                if neuter_word == "dem":
                    contraction = Marking_Tool.DATIVE_CONTRACTIONS.get(preposition)
                elif neuter_word == "das":
                    contraction = Marking_Tool.ACCUSATIVE_CONTRACTIONS.get(preposition)
            if contraction:
                if self.parse_list[pos-1][1][:1].isupper():
                    contraction = contraction.capitalize()
                # Vom Artikel bleibt nur der letzte Buchstabe, der Rest gehoert zur Praeposition.
                self.parse_list[pos-1][-2] = contraction[:-1]
                self.parse_list[pos-1][-1] = ""
                self.parse_list[pos][-2] = contraction[-1]
            elif neuter_word == self.parse_list[pos][1]:
                # Der Artikel selbst aendert sich nicht. Dann bleibt auch seine Schreibung aus dem
                # Eingabetext unangetastet -- vor allem eine Zusammenziehung mit der Praeposition:
                # "fuers Erste" wurde sonst zu "fuerdas Erste".
                pass
            elif self.parse_list[pos][-2] in ("r", "m", "s"):
                # split_prepositions hat die Zusammenziehung zerlegt und die neue Artikelform passt
                # nicht mehr hinein; die Praeposition muss wieder vollstaendig werden.
                self.restore_split_preposition(pos)
                self.parse_list[pos][-2] = neuter_word
            else:
                self.parse_list[pos][-2] = neuter_word

    # Numerus des zweiten Substantivs einer schon zusammengezogenen Doppelnennung, sofern an pos
    # deren erstes Substantiv steht. Erkennbar ist die Zusammenziehung daran, dass die Konjunktion
    # im Ausgabetext bereits geleert wurde.
    def paired_noun_number(self, pos:int):
        if pos + 1 >= len(self.parse_list):
            return None
        if pos + 1 not in self.noun_pair_spans:
            return None
        conjunction = self.parse_list[pos+1]
        if conjunction[1] not in ("und", "oder", "/", "bzw.", "bzw", "+"):
            return None
        second = self.second_noun_position(pos+1)
        if second is None or self.parse_list[second][3] != "N":
            return None
        second_feats = self.parse_list[second][5].split("|")
        if len(second_feats) > 2 and second_feats[2] in ("Sg", "Pl"):
            return second_feats[2]
        return None

    # This function determines the number of a noun for which no number has been recognized by ParZu.
    def determine_number(self, pos:int, feats:list):
        # Wenn das Substantiv auf "mann", "frau", "herr" oder "dame" endet, dann ist es im Singular.
        if self.parse_list[pos][1].lower().endswith("mann") or self.parse_list[pos][1].lower().endswith("frau") or self.parse_list[pos][1].lower().endswith("herr") or self.parse_list[pos][1].lower().endswith("dame"):
           feats[2] = "Sg"
        # Wenn das Substantiv auf "ern" endet und nicht auf "bauern", dann ist es im Plural.
        elif self.parse_list[pos][1].endswith("ern") and not self.parse_list[pos][1].lower().endswith("bauern"):
            feats[1] = "Dat"
            feats[2] = "Pl"
        # Wenn das substantiv auf "innen" endet, dann ist es im Plural.
        elif self.parse_list[pos][1].endswith("innen"):
            feats[2] = "Pl"
        # Wenn das Substantiv ein Prädikativ eines singularischen Verbes ist, dann ist es im Singular:
        elif self.parse_list[pos][7] == "pred" and self.parse_list[int(self.parse_list[pos][6])-1][3] == "V" and self.singular_verb(int(self.parse_list[pos][6])-1):
            feats[2] = "Sg"
        # Wenn bei "Ahnen"/"Vorfahren"/"Nachfahren" erkannt wird, dass es Nominativ ist, aber kein Numerus erkannt wird, dann ist es ein Plural.
        elif (self.parse_list[pos][1] == "Ahnen" or self.parse_list[pos][1] == "Vorfahren" or self.parse_list[pos][1] == "Nachfahren") and feats[1] == "Nom":
                feats[2] = "Pl"
        # Wenn das Substantiv das erste Wort in einer Doppelnennung mit einem anderen Substantiv steht, dann übernehme den Numerus des anderen Substantivs:
        # (Überprüfe dabei auch, ob das Substantiv vorher als Teil einer Doppelnennung erkannt wurde, also der Output der Konjunktion auf "" gesetzt wurde.)
        elif self.paired_noun_number(pos) is not None:
            feats[2] = self.paired_noun_number(pos)
        else:
            print("Else case of determining number for noun without number")
            article = False
            for child in self.nounphrases.get(pos+1):
                if self.parse_list[child-1][3] == "ART":
                    article = True
                    article_position = child-1
                    break
            if article:
                # Wenn ein Substantiv einen Artikel hat und im Parzu-Parse kein Numerus hat, im Maskulinum steht (oder auf "-er" endet) und sich ein auf "-e" endender Artikel drauf bezieht, dann ist das Substantiv im Plural.
                if (feats[0] == "Masc" or self.parse_list[pos][1].endswith("er")) and self.parse_list[article_position][1].endswith("e"):
                    feats[2] = "Pl"
                # Wenn der Artikel "alle" lautet, setze den Numerus des Substantivs auf Plural.
                elif self.parse_list[article_position][2] == "alle":
                    feats[2] = "Pl"
                # Wenn ein Substantiv einen Artikel hat und im Parzu-Parse kein Numerus hat, im Dativ steht und sich ein auf "-en" endender Artikel drauf bezieht, dann ist das Substantiv im Plural.
                elif feats[1] == "Dat" and self.parse_list[article_position][1].endswith("en"):
                    feats[2] = "Pl"
                # Steht vor einem substantivierten Adjektiv ein Determinierer auf "-e", so
                # entscheidet dessen eigene Endung: "ihre Herrschende" ist ein Femininum
                # Singular, "ihre Herrschenden" ein Plural. Nur in diesen beiden Formen endet
                # der Determinierer auf "-e"; in den übrigen Kasus lautet er "ihren", "ihrem",
                # "ihrer" oder "ihres". Bei Possessivformen lässt ParZu den Numerus offen, weil
                # "ihre" für sich genommen mehrdeutig ist.
                elif (self.parse_list[article_position][1].endswith("e")
                      and self.parse_list[pos][1] == self.parse_list[pos][2] + "n"):
                    feats[2] = "Pl"
                # Ansonsten ist ein Substantiv mit Artikel und einem nicht erkannten Numerus im Singular.
                else:
                    feats[2] = "Sg"
            # Wenn der Satz nur das Substantiv enthält und das Substantiv nicht auf "-en" endet und nicht "Bauern" lautet, setze es in den Singular:
            elif (len(self.parse_list) == 1 or (len(self.parse_list) == 2 and self.parse_list[1][3] == "$.")) and not self.parse_list[pos][1].endswith("en") and not self.parse_list[pos][1] == "Bauern":
                feats[2] = "Sg"
            # Ein Substantiv mit einer nicht pluralischen Apposition steht selbst im Singular
            # ("Lieber Thomas!", "Liebe Rose!" -- dort lässt ParZu den Numerus der Apposition
            # offen); ohne diese Prüfung greift unten die Voreinstellung Plural.
            elif any(other[6] == self.parse_list[pos][0] and other[7] == "app" and "Pl" not in other[5]
                     for other in self.parse_list):
                feats[2] = "Sg"
            # Ein attributives Adjektiv auf "-er" im Maskulinum ist der starke Nominativ Singular
            # ("Du kleiner Lehrer"); im Plural stünde dort "kleine" oder "kleinen". Damit lässt sich
            # der Numerus bestimmen, den ParZu beim Substantiv offenlässt.
            elif any(other[6] == self.parse_list[pos][0] and other[3] == "ADJA"
                     and other[1].lower().endswith("er") and "Pl" not in other[5]
                     and other[5].split("|")[1:2] == ["Masc"]
                     for other in self.parse_list):
                feats[2] = "Sg"
            # Ein Substantiv, das als Apposition an einem Pronomen der ersten oder zweiten Person
            # hängt, steht im Singular ("Du Armer!", "Ich Armer!"). ParZu lässt den Numerus des
            # Pronomens dort selbst offen, das Lemma ist aber eindeutig. Ohne diese Prüfung greift
            # unten die Voreinstellung Plural, und ein pluralisches substantiviertes Adjektiv ist
            # nicht markierbar.
            elif (self.parse_list[pos][7] == "app" and int(self.parse_list[pos][6]) != 0
                  and self.parse_list[int(self.parse_list[pos][6])-1][4] == "PPER"
                  and self.parse_list[int(self.parse_list[pos][6])-1][2] in ("ich", "du")):
                feats[2] = "Sg"
            # Wenn das Substantiv nicht von "als" abhängig ist (lässt sich im ParZu-Parsebaum überprüfen),
            # setze den Numerus des Substantivs auf "Pl":
            elif not re.match(r"(A|a)ls", self.parse_list[int(self.parse_list[pos][6])-1][1]):
                feats[2] = "Pl"
            else:
                # Wenn eine davorstehende Nominalphrase (oder eine Propositionalphrase mit einer Nominalphrase) im Syntaxbaum an "als" angebunden ist (manchmal erzeugt Parzu komische Anbindungen an danachstehende Nominalphrasen, sodass die Bedingung "davorstehende" wichtig ist),
                # kopiere den Numerus und Kasus von dieser Nominalphrase auf das Substantiv ohne Numerus:
                print("Else-else case of determining number for noun without number")
                index_of_last_np_before_als = self.find_last_np_before_index(int(self.parse_list[pos][6]))
                if index_of_last_np_before_als > 0:
                    otherfeats = self.parse_list[index_of_last_np_before_als-1][5].split("|")
                    if self.parse_list[index_of_last_np_before_als-1][2] == "man":
                        feats[2] = "Sg"
                    elif self.parse_list[index_of_last_np_before_als-1][3] == "N":
                        if len(otherfeats) >= 3:
                            feats[1] = otherfeats[1]
                            feats[2] = otherfeats[2]
                    elif self.parse_list[index_of_last_np_before_als-1][3] == "PRO":
                        # Die Merkmale eines Pronomens sind je nach Art anders angeordnet:
                        # Personalpronomen tragen "Person|Numerus|Genus|Kasus" (vier Felder),
                        # Relativ- und Indefinitpronomen "Genus|Kasus|Numerus" (drei). Ohne diese
                        # Unterscheidung griff der Zugriff auf den Kasus bei einem
                        # Relativpronomen ins Leere: "Die Leute, die als Reisende kommen,
                        # warten." stürzte deshalb ab.
                        if len(otherfeats) >= 4:
                            feats[1] = otherfeats[3]
                            feats[2] = otherfeats[1]
                        elif len(otherfeats) == 3:
                            feats[1] = otherfeats[1]
                            feats[2] = otherfeats[2]
                    # Hier oben und unten werden wahrscheinlich noch mehr Fälle als "N" und "PRO" benötigt, zum Beispiel für den Fall, dass "jemand" als Adjektiv geparst wird.
                else:
                    # Suche die erste Nominalphrase nach dem Substantiv ohne Numerus (da sich die als-Konstruktion jetzt höchstwahrscheinlich darauf bezieht) und
                    # kopiere den Numerus (aber nicht den Kasus) von dieser Nominalphrase auf das Substantiv ohne Numerus:
                    # Zuerst muss der letzte Index der als-Konstruktion gefunden werden:
                    indices_within_als_construction = [int(self.parse_list[pos][6])]
                    print("indices_within_als_construction start:", indices_within_als_construction)
                    previous_indices_within_als_construction = []
                    while previous_indices_within_als_construction != indices_within_als_construction:
                        previous_indices_within_als_construction = indices_within_als_construction.copy()
                        for i in range(int(self.parse_list[pos][6])+1, len(self.parse_list)+1):
                            if int(self.parse_list[i-1][6]) in indices_within_als_construction and i not in indices_within_als_construction:
                                indices_within_als_construction.append(i)
                                print("indices_within_als_construction append:", indices_within_als_construction)
                    last_index_of_als_construction = max(indices_within_als_construction)
                    index_of_first_np_after_als_construct = self.find_first_np_after_index(last_index_of_als_construction)
                    print("index_of_first_np_after_als_construct:", index_of_first_np_after_als_construct)
                    if index_of_first_np_after_als_construct > 0:
                        otherfeats = self.parse_list[index_of_first_np_after_als_construct-1][5].split("|")
                        if self.parse_list[index_of_first_np_after_als_construct-1][2] == "man":
                            feats[2] = "Sg"
                        elif self.parse_list[index_of_first_np_after_als_construct-1][3] == "N":
                            if otherfeats[2] in ["Sg","Pl"]:
                                feats[2] = otherfeats[2]
                            else:
                                feats[2] = "Sg"
                        elif self.parse_list[index_of_first_np_after_als_construct-1][3] == "PRO":
                            if otherfeats[1] in ["Sg","Pl"]:
                                feats[2] = otherfeats[1]
                            else:
                                feats[2] = "Sg"
                    else:
                        feats[2] = "Sg"

    # Zwei singularische Substantive, die zusammen das Subjekt eines pluralischen Verbs bilden,
    # bezeichnen zwei verschiedene Personen: "Wo sind Mutter und Vater?" fragt nach zweien. Solche
    # Paare dürfen nicht wie eine Doppelnennung ("Bürgerinnen und Bürger", die dieselbe Gruppe
    # zweimal benennt) zu einer Form zusammengezogen werden.
    # Das Argument ist die Position der Konjunktion.
    # Die Lemmata der Adjektive, die an dem Substantiv an position haengen, in Textreihenfolge.
    def adjective_lemmas(self, position:int) -> list:
        return [word[2].lower() for word in self.parse_list
                if word[3] == "ADJA" and word[6] == self.parse_list[position][0]]

    # Findet bei einer Doppelnennung das zweite Substantiv. Es steht normalerweise unmittelbar
    # hinter der Konjunktion ("Lehrer oder Lehrerin"), darf aber auch einen eigenen Artikel und
    # eigene Attribute mitbringen ("der Lehrer oder die gute Lehrerin"). Die dazwischenstehenden
    # Woerter muessen dann im Parse als Dependenten genau dieses Substantivs haengen -- sonst
    # beginnt hinter der Konjunktion etwas anderes als die parallele zweite Nennung.
    def second_noun_position(self, pos:int):
        if pos + 1 >= len(self.parse_list):
            return None
        if self.parse_list[pos+1][3] != "ART":
            return pos + 1
        for other in range(pos + 2, len(self.parse_list)):
            if self.parse_list[other][3] in ("ART", "ADJA"):
                continue
            if self.parse_list[other][3] != "N":
                return None
            between = self.parse_list[pos+1:other]
            if not all(word[6] == self.parse_list[other][0] for word in between):
                return None
            # Beide Nennungen muessen dieselben Attribute tragen. "Der gute Lehrer oder die gute
            # Lehrerin" bezeichnet eine Person und wird zusammengezogen, "der gute Lehrer oder die
            # schlechte Lehrerin" dagegen zwei -- dort ginge beim Zusammenziehen die Haelfte der
            # Aussage verloren.
            if self.adjective_lemmas(pos-1) != self.adjective_lemmas(other):
                return None
            return other
        return None

    def is_plural_subject_pair(self, pos:int, second:int=None) -> bool:
        if second is None:
            second = pos + 1
        if pos < 1 or second >= len(self.parse_list):
            return False
        first_noun = self.parse_list[pos-1]
        second_noun = self.parse_list[second]
        if "Sg" not in first_noun[5] or "Sg" not in second_noun[5]:
            return False
        if first_noun[7] != "subj" or int(first_noun[6]) == 0:
            return False
        head = self.parse_list[int(first_noun[6])-1]
        return head[3] == "V" and "Pl" in head[5]

    # Erkennt Beinamen wie "Peter dem Großen" oder "Katharina die Große": ein grossgeschriebenes
    # Adjektiv, dem unmittelbar ein Artikel und davor ein Eigenname vorangeht. ParZu hängt solche
    # Adjektive als Attribut an ein späteres Substantiv, sodass sie sonst unmarkiert blieben.
    # Der vorangehende Artikel gehört mit zur Nominalphrase, auch wenn ParZu ihn anders anbindet.
    def is_name_epithet(self, pos:int) -> bool:
        if pos < 2:
            return False
        adjective, article, name = self.parse_list[pos], self.parse_list[pos-1], self.parse_list[pos-2]
        if not (Lexicon.starts_uppercase(adjective[1]) and article[3] == "ART"
                and not article[1].lower().startswith("das") and name[4] == "NE"):
            return False
        if adjective[3] == "ADJA":
            return True
        # In den obliquen Kasus gibt ParZu den Beinamen oft als Substantiv aus, lemmatisiert ihn
        # aber adjektivisch ("Großen" zu "Große"). Diese Endung unterscheidet ihn von einer
        # gewöhnlichen Apposition, deren Grundform mit der Wortform übereinstimmt ("die Metropole").
        return (adjective[3] == "N" and "Pl" not in article[5]
                and adjective[1].lower() in [adjective[2].lower() + ending for ending in ("n", "r", "s", "m")])

    # Lässt ParZu den Numerus eines Personalpronomens offen, entscheidet das folgende Finitverb
    # darüber. In "Sie haben ein Keil zwischen die Bürger getrieben" verliert ParZu wegen des
    # fehlerhaften "ein Keil" den Bezug und gibt "Sie" ohne Numerus als Akkusativobjekt aus.
    # Wegen "haben" kann es aber nur Plural oder Höflichkeitsform sein, und beides ist nicht
    # markierbar. Ein ausgewiesener Singular bleibt unberührt ("Sie hat das Buch gelesen").
    def plural_by_verb(self, pos:int) -> bool:
        if "Sg" in self.parse_list[pos][5].split("|"):
            return False
        for later_parse in self.parse_list[pos+1:]:
            if later_parse[4] in ("VVFIN", "VAFIN", "VMFIN"):
                return "Pl" in later_parse[5].split("|")
        return False

    def singular_verb(self, pos:int):
        if "Sg" in self.parse_list[pos][5]:
            return True
        elif self.parse_list[pos][7] == "aux" and int(self.parse_list[pos][6]) != 0:
            return self.singular_verb(int(self.parse_list[pos][6])-1)
        else:
            return False
    
    def find_last_np_before_index(self, als_index:int):
        for i in range(als_index-1,0,-1):
            if i in self.nounphrases and self.parse_list[i-1][1] != "sich":
                return i
        return 0
    
    def find_first_np_after_index(self, als_index:int):
        for i in range(als_index+1,len(self.parse_list)+1):
            if i in self.nounphrases and self.parse_list[i-1][1] != "sich":
                return i
        return 0


    # This function neutralizes the word that has been selected. Then, all dependent words in the sentence are neutralized.
    # Lässt die Wörter verschwinden, die im Kästchen einer Doppelnennung aufgegangen sind. Das
    # geschieht erst hier und nicht schon beim Erzeugen des Formulars: Sonst fehlten sie auch dann
    # im Ausgabetext, wenn der Benutzer das Kästchen gar nicht ausgewählt hat -- aus "Die
    # Bürgerinnen und Bürger stimmen ab." wurde so "Die Bürgerinnen stimmen ab."
    def absorb_noun_pair(self, pos:int):
        span = self.noun_pair_spans.get(pos+1)
        if not span:
            return
        self.parse_list[pos][-1] = ""
        for other in span:
            self.parse_list[other][-2] = ""
            # Der Leerraum hinter dem letzten Wort trennt die Doppelnennung vom Rest des Satzes
            # und muss im Ausgabetext stehenbleiben.
            if other != span[-1]:
                self.parse_list[other][-1] = ""

    def neutralize_nounphrase(self, pos:int, selected_components):
        print("about to neutralize nounphrase")
        print(self.parse_list[pos])
        self.absorb_noun_pair(pos)
        # Fehlt der Kasus, wird er aus der Dependenzrelation ergänzt. Das muss vor der
        # Neutralisierung geschehen, damit sowohl der Kopf als auch die abhängigen Wörter ihn
        # kennen: "meiner Lieben" ist ein Dativ und ergibt "meinerm Lieben", nicht "meinerm Liebe".
        if self.get_case(pos) == "_":
            inferred_case = Marking_Tool.DEPREL_CASES.get(self.parse_list[pos][7])
            if inferred_case:
                self.set_missing_case(pos, inferred_case)
            elif (self.parse_list[pos][7] == "pn" and int(self.parse_list[pos][6]) != 0
                    and self.parse_list[int(self.parse_list[pos][6])-1][2].lower()
                        in Marking_Tool.DATIVE_ONLY_PREPOSITIONS):
                self.set_missing_case(pos, "Dat")
            elif (self.parse_list[pos][7] == "pn" and int(self.parse_list[pos][6]) != 0
                    and self.parse_list[int(self.parse_list[pos][6])-1][2]
                        not in Marking_Tool.DATIVE_PREPOSITIONS):
                # Ein Substantiv, das von einer Präposition regiert wird, steht nie im Nominativ.
                # Bei Wechselpräpositionen wie "an" oder "auf" lässt ParZu den Kasus offen, weil
                # sie Akkusativ und Dativ regieren können; dann wird der Akkusativ angenommen.
                # Für die Ausgabe macht das nur bei der schwachen Deklination einen Unterschied
                # ("Ich glaube an den Weihnachtsmenschen"), denn im Inklusivum sind Nominativ und
                # Akkusativ in allen Paradigmen gleich.
                preposition_feats = self.parse_list[int(self.parse_list[pos][6])-1][5].split("|")
                preposition_case = preposition_feats[0] if preposition_feats else "_"
                self.set_missing_case(pos, preposition_case
                                      if preposition_case in ("Acc", "Dat", "Gen") else "Acc")
        feats = self.parse_list[pos][5].split("|")
        if len(feats) == 1:
            feats.append("_")
            feats.append("_")
        plural = True

        # Determine whether the noun phrase has an article:
        has_article = False
        if pos+1 in self.nounphrases:
            for child in self.nounphrases.get(pos+1):
                if self.parse_list[child-1][3] == "ART":
                    has_article = True
                    break
        # Check whether the noun phrase is conjuncted with a noun phrase that has an article:
        # if int(self.parse_list[pos][6]) != 0: 
        #     print("step 1:", pos)
        #     if self.parse_list[int(self.parse_list[pos][6])-1][3] == "KON": 
        #         print("step 2:", int(self.parse_list[pos][6])-1)
        #         if int(self.parse_list[int(self.parse_list[pos][6])-1][6]) != 0: 
        #             print("step 3:", int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1)
        #             if self.parse_list(int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1)[3] == "N":
        #                 print("step 4:", int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1)
        #                 for child in self.nounphrases.get(int(self.parse_list[int(self.parse_list[pos][6])-1][6])):
        #                     if self.parse_list[child-1][3] == "ART":
        #                         has_article = True
        #                         break
        if int(self.parse_list[pos][6]) != 0 and self.parse_list[int(self.parse_list[pos][6])-1][3] == "KON" and int(self.parse_list[int(self.parse_list[pos][6])-1][6]) != 0 and self.parse_list[int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1][3] == "N":
            for child in self.nounphrases.get(int(self.parse_list[int(self.parse_list[pos][6])-1][6])):
                if self.parse_list[child-1][3] == "ART":
                    has_article = True
                    break
        # Artikel, die Genus und Kasus selbst anzeigen (der, dieser, welcher ...), im Unterschied
        # zum ein-Paradigma, das im Maskulinum Nominativ endungslos ist (ein, mein, unser ...).
        has_marked_article = False
        if pos+1 in self.nounphrases:
            for child in self.nounphrases.get(pos+1):
                child_parse = self.parse_list[child-1]
                if child_parse[3] == "ART" and not any(child_parse[1].lower().startswith(start)
                                                       for start in Lexicon.EIN_PARADIGM + ["unser", "eue"]):
                    has_marked_article = True
                    break

        # Determine whether the noun phrase has an article that is not from the ein-Paradigma:
        has_non_ein_article = False
        if pos+1 in self.nounphrases:
            for child in self.nounphrases.get(pos+1):
                if self.parse_list[child-1][3] == "ART" and self.parse_list[child-1][2] not in ["ein","eine","einer","einem","eines"]:
                    has_non_ein_article = True
                    break

        # Adjektive mit einer eigenen Form im Inklusivum ("kaufmännisch" wird zu "kaufleutisch").
        # Ersetzt wird auch die Wortform und die Grundform, damit eine spätere Neutralisierung als
        # abhängiges Adjektiv die Endung am neuen Stamm bildet und nicht am alten: In "der
        # kaufmännische Angestellte" hängt das Adjektiv zugleich an einer Nominalphrase.
        neutralized_adjective = Lexicon.neutralize_irregular_word(self.parse_list[pos][-2])
        if neutralized_adjective is not None:
            self.parse_list[pos][-2] = neutralized_adjective
            self.parse_list[pos][1] = Lexicon.neutralize_irregular_word(self.parse_list[pos][1]) or self.parse_list[pos][1]
            self.parse_list[pos][2] = Lexicon.neutralize_irregular_word(self.parse_list[pos][2]) or self.parse_list[pos][2]
            return
        # Neutralize a possessive pronoun
        if self.parse_list[pos][4] == "PPOSAT" and self.parse_list[pos][6] == "0":
            if feats[2] == "Sg" or feats[2] == "_":
                plural = False
            match = re.search(r"[/*_:]([Ii]hr|[Ss]ein)", self.parse_list[pos][-2])
            if match:
                print("sonderzeichen:",match.group(0))
                self.parse_list[pos][-2] = Lexicon.neutralize_possesive_pronoun_with_sonderzeichen(pos,selected_components,self.nounlist,feats,match.group(0))
            else:
                self.parse_list[pos][-2] = Lexicon.neutralize_possesive_pronoun(pos,selected_components,self.nounlist,feats)
        # Neutralize a possessive article
        elif self.parse_list[pos][4] == "PPOSAT":
            self.parse_list[pos][-2] = Lexicon.neutralize_possesive_article(self.parse_list[pos])
            # Here we additionally need to modify the input possessive pronoun, so that the output is correct when this pronoun needs to be modified further due to the noun it modifies being put into the inklusivum.
            self.parse_list[pos][1] = Lexicon.neutralize_possesive_article(self.parse_list[pos])
        # Neutralize a Noun
        elif self.parse_list[pos][3] == "N":
            article = False
            for child in self.nounphrases.get(pos+1):
                if self.parse_list[child-1][3] == "ART":
                    article = True
                    article_position = child-1
                    break
            if article:
                if self.parse_list[article_position][2] == "alle":
                        feats[2] = "Pl"
            if feats[2] == "_":
                print("Noun without number:")
                print(self.parse_list[pos][1])
                print(pos)
                print(feats)
                self.determine_number(pos,feats)
                print("Determined number:", feats)
            if feats[1] == "_" and self.parse_list[pos][1].endswith("ern") and not self.parse_list[pos][1] == "Bauern":
                feats[1] = "Dat"
            # Nach "zwischen", "unter", "vor", "hinter", "neben", "von", "bei" nicht erkanntes Kasus zu Dativ machen.
            if feats[1] == "_":
                if int(self.parse_list[pos][6]) != 0:
                    if self.parse_list[int(self.parse_list[pos][6])-1][2] in Marking_Tool.DATIVE_PREPOSITIONS:
                        feats[1] = "Dat"
                    elif int(self.parse_list[int(self.parse_list[pos][6])-1][6]) != 0:
                        if int(self.parse_list[int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1][6]) != 0:
                            if self.parse_list[int(self.parse_list[int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1][6])-1][2] in Marking_Tool.DATIVE_PREPOSITIONS:
                                feats[1] = "Dat"
            if feats[2] == "Sg" or feats[2] == "_":
                plural = False
            print("about to neutralize noun")
            print(self.parse_list[pos])
            print(pos)
            print(feats)
            print(selected_components)
            print(self.nounlist)
            self.parse_list[pos][-2], head_selected, person, kind, junge_person = Lexicon.make_neutralized_noun(pos,selected_components,self.nounlist,feats,has_article,has_marked_article)
            print(self.parse_list[pos][-2])
            # The following line prevents articles of composite nouns with a person noun in non-final position from being neutralized.
            if not head_selected:
                plural = True
            # If word ends in -mann or -frau and is neutralized to -person, make dependent words feminine.
            if person:
                # In order not to neutralize the dependent words later, we set "plural" to True.
                plural = True
                feats = self.parse_list[pos][5].split("|")
                # "Mädchen" ist neutrum, muss aber wie "Junge" feminine Kongruenz bekommen.
                if (feats[0] == "Masc" or feats[0] == "_" or junge_person) and feats[2] != "Pl":
                    print("about to feminize dependent words", self.parse_list[pos][1], self.nounphrases.get(pos+1))
                    # Der Kasus des Kopfes wird an die abhängigen Wörter weitergereicht -- genau
                    # wie beim Neutralisieren. Ohne das verloren sie ihn, wo ParZu ihn nicht
                    # erkannt hat ("von der Tochter" ergab "von das Kind" statt "von dem Kind").
                    head_case = self.get_case(pos)
                    for child in self.nounphrases.get(pos+1):
                        article_pos = min(self.nounphrases.get(pos+1))
                        if head_case != "_":
                            self.set_missing_case(child-1, head_case)
                        child_parse = self.parse_list[child-1]
                        # Aus "junges Mädchen" wird "sehr junge Person", damit das Adjektiv
                        # nicht doppelt erscheint ("junge junge Person"). Steigerungsformen
                        # bleiben dagegen stehen, sonst ginge der Vergleich verloren: "das
                        # jüngere Mädchen" ist keine "sehr junge Person".
                        if (junge_person and child_parse[3] == "ADJA" and child_parse[2] == "jung"
                                and "Comp" not in child_parse[5] and "Sup" not in child_parse[5]):
                            child_parse[-2] = "sehr"
                        else:
                            self.feminize_word(child-1, has_article, article_pos)
            # If word ends in -sohn or -tochter, make dependent words neuter.
            if kind:
                # In order not to neutralize the dependent words later, we set "plural" to True.
                plural = True
                if feats[2] != "Pl":
                    print("about to make dependent words neuter", self.parse_list[pos][1], self.nounphrases.get(pos+1))
                    head_case = self.get_case(pos)
                    for child in self.nounphrases.get(pos+1):
                        article_pos = min(self.nounphrases.get(pos+1))
                        if head_case != "_":
                            self.set_missing_case(child-1, head_case)
                        self.neuterize_word(child-1, has_non_ein_article, article_pos)
        # Neutralized attributive pronoun
        elif self.parse_list[pos][1].lower() in ["dessen","deren"]:
            self.parse_list[pos][-2] = Lexicon.neutralize_attributive_pronoun(self.parse_list[pos])
        elif re.match(r"(J|j)emand(e?)s" , self.parse_list[pos][1]):
                self.parse_list[pos][-2] = Lexicon.neutralize_pos_jemand(self.parse_list[pos])
        #Neutralize everything else
        else:
            if feats[2] == "Sg" or feats[2] == "_":
                plural = False
            head_artificially_capitalized = self.artificially_capitalized(pos)
            self.parse_list[pos][-2] = Lexicon.neutralize_word(self.parse_list[pos],has_article)
            # Auch beim Kopf der Nominalphrase darf eine künstliche Grossschreibung nicht in die
            # Ausgabe gelangen ("der andere ging" ergab sonst "derm Anderey").
            if head_artificially_capitalized and self.parse_list[pos][-2][:1].isupper():
                self.parse_list[pos][-2] = (self.parse_list[pos][-2][:1].lower()
                                            + self.parse_list[pos][-2][1:])
        # Neutralize the remaining words in the nounphrase:
        if not plural or self.parse_list[pos][2].endswith("jenige"):
            print("about to neutralize dependent words", self.parse_list[pos][1], self.nounphrases.get(pos+1))
            # Der Kasus des Kopfes wird an die abhängigen Wörter weitergereicht.
            case = self.get_case(pos)
            for child in self.nounphrases.get(pos+1):
                article_pos = min(self.nounphrases.get(pos+1))
                if case != "_":
                    self.set_missing_case(child-1, case)
                self.neutralize_word(child-1, has_article, article_pos)


    def find_verb_dependencies(self, pos:int, recognized_verb_dependencies:list):
        verb_dependencies = []
        for word_parse in self.parse_list:
            if not int(word_parse[0]) in verb_dependencies and not int(word_parse[0]) in recognized_verb_dependencies and (int(word_parse[6]) == pos or word_parse[3] == "ADV" or word_parse[3] == "PREP"):
                verb_dependencies.append(int(word_parse[0]))
                recognized_verb_dependencies.append(int(word_parse[0]))
                children = self.find_verb_dependencies(int(word_parse[0]),recognized_verb_dependencies)
                verb_dependencies.extend(children)
                recognized_verb_dependencies.extend(children)
        return verb_dependencies

    def search_genitive_pronoun(self, pos:int):
        verb_dependencies = self.find_verb_dependencies(pos+1,[])
        print("verb_dependencies:",verb_dependencies)
        searching_before_verb = True
        searching_after_verb = True
        i = 1
        while searching_before_verb or searching_after_verb:
            print("i:",i)
            print("searching_before_verb:",searching_before_verb)
            print("searching_after_verb:",searching_after_verb)
            if searching_before_verb:
                if pos-i < 0:
                    print("reached beginning of sentence")
                    searching_before_verb = False
                elif self.parse_list[pos-i][1] == "seiner" and self.parse_list[pos-i][6] == "0":
                    print("found seiner before verb")
                    self.parse_list[pos-i][2] = "er"
                    self.parse_list[pos-i][3] = "PRO"
                    self.parse_list[pos-i][4] = "PPER"
                    self.parse_list[pos-i][5] = "3|Sg|Masc|Gen"
                    self.parse_list[pos-i][6] = str(pos+1)
                    self.parse_list[pos-i][7] = "objg"
                    break
                elif self.parse_list[pos-i][1] == "ihrer" and self.parse_list[pos-i][6] == "0":
                    print("found ihrer before verb")
                    self.parse_list[pos-i][2] = "sie"
                    self.parse_list[pos-i][3] = "PRO"
                    self.parse_list[pos-i][4] = "PPER"
                    self.parse_list[pos-i][5] = "3|Sg|Fem|Gen"
                    self.parse_list[pos-i][6] = str(pos+1)
                    self.parse_list[pos-i][7] = "objg"
                    break
                elif not pos-i+1 in verb_dependencies:
                    print("stopped searching before verb")
                    searching_before_verb = False
            if searching_after_verb:
                if len(self.parse_list) <= pos+i:
                    print("reached end of sentence")
                    searching_after_verb = False
                elif self.parse_list[pos+i][1] == "seiner" and self.parse_list[pos+i][6] == "0":
                    print("found seiner after verb")
                    self.parse_list[pos+i][2] = "er"
                    self.parse_list[pos+i][3] = "PRO"
                    self.parse_list[pos+i][4] = "PPER"
                    self.parse_list[pos+i][5] = "3|Sg|Masc|Gen"
                    self.parse_list[pos+i][6] = str(pos+1)
                    self.parse_list[pos+i][7] = "objg"
                    break
                elif self.parse_list[pos+i][1] == "ihrer" and self.parse_list[pos+i][6] == "0":
                    print("found ihrer after verb")
                    self.parse_list[pos+i][2] = "sie"
                    self.parse_list[pos+i][3] = "PRO"
                    self.parse_list[pos+i][4] = "PPER"
                    self.parse_list[pos+i][5] = "3|Sg|Fem|Gen"
                    self.parse_list[pos+i][6] = str(pos+1)
                    self.parse_list[pos+i][7] = "objg"
                    break
                elif not pos+i+1 in verb_dependencies:
                    print("stopped searching after verb")
                    searching_after_verb = False
            i += 1

    # Recognizes noun phrases that refer to people and generates the html form, with checkboxes next to recognized noun phrases. 
    # [word_index_from_1, position_of_noun_in_composite_noun, original, neutralized, suffix, noun_type, capitalized, head_identified_as_person_noun]
    def get_marking_form(self, sentence_number) -> str:
        self.marked_nouns = []
        # Suche pronominale Genitivobjekte:
        # Suche Verben, die sinnvollerweise eine Person als Genitivobjekt haben können:
        for pos, word_parse in enumerate(self.parse_list):
            if word_parse[3] == "V" and word_parse[2] in ["gedenken","annehmen","bemächtigen","erinnern","bedienen","erfreuen","entledigen","rühmen","schämen","bedürfen","entbehren"]:
                self.search_genitive_pronoun(pos)
            if word_parse[3] == "V" and word_parse[2] == "nehmen":
                # Check if "an" appears as a separated verb particle in the sentence:
                an = False
                for word_parse in self.parse_list:
                    if word_parse[1] == "an" and word_parse[3] == "PTKVZ":
                        an = True
                        break
                if an:
                    self.search_genitive_pronoun(pos)

        # Finde Doppelnennungen wie "Bürgerinnen und Bürger":
        noun_pair_positions = []
        noun_pair_indices = {}
        noun_pair_types = {}
        noun_pair_prefixes = {}
        noun_pair_ends = {}
        for pos, word_parse in enumerate(self.parse_list):
            if word_parse[1] == "und" or word_parse[1] == "oder" or word_parse[1] == "/" or word_parse[1] == "bzw." or word_parse[1] == "bzw" or word_parse[1] == "+":
                second = self.second_noun_position(pos)
                if second is None:
                    continue
                second_noun = self.parse_list[second]
                # Zwei Einzelpersonen als Subjekt eines pluralischen Verbs werden nicht zusammengezogen.
                if self.is_plural_subject_pair(pos, second):
                    continue
                # Schaue, ob das Wort davor ein feminines Personensubstantiv ist:
                for j, line in enumerate(Lexicon.FEMALE_NOUNS):
                    if self.parse_list[pos-1][2] == line:
                        # Schaue, ob das Wort danach das entsprechende maskuline Personensubstantiv ist:
                        if second_noun[2] == Lexicon.MALE_NOUNS[j]:
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "standard"
                            noun_pair_prefixes[pos-1] = ""
                            noun_pair_ends[pos-1] = second
                            # Wenn das maskuline Substantiv auf "ern" endet und nicht "Bauern" ist, dann steht die Konjunktion (und damit das feminine Substantiv) im Dativ:
                            if second_noun[1].endswith("ern") and not second_noun[1] == "Bauern":
                                feats = self.parse_list[pos-1][5].split("|")
                                feats[1] = "Dat"
                                self.parse_list[pos-1][5] = "|".join(feats)
                            break
                # Schaue, ob das Wort davor ein maskulines Personensubstantiv ist:
                for j, line in enumerate(Lexicon.MALE_NOUNS):
                    if self.parse_list[pos-1][2] == line:
                        # Schaue, ob das Wort danach das entsprechende feminine Personensubstantiv ist:
                        if second_noun[2] == Lexicon.FEMALE_NOUNS[j]:
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "standard"
                            noun_pair_prefixes[pos-1] = ""
                            noun_pair_ends[pos-1] = second
                            # Wenn das maskuline Substantiv auf "ern" endet und nicht "Bauern" ist, dann steht die Konjunktion (und damit das feminine Substantiv) im Dativ:
                            if self.parse_list[pos-1][1].endswith("ern") and not self.parse_list[pos-1][1] == "Bauern":
                                feats = second_noun[5].split("|")
                                feats[1] = "Dat"
                                second_noun[5] = "|".join(feats)
                            break
                # Schaue, ob das Wort davor ein Wort ist, das durch ein Neologismus ersetzt werden kann:
                for j, neologism in enumerate(Lexicon.NEOLOGISMS):
                    neologism = "(" + neologism + ")$"
                    if re.match(neologism.lower(), self.parse_list[pos-1][2].lower()):
                        # Schaue, ob das Wort danach das entsprechende Wort ist:
                        if re.match(neologism.lower(), second_noun[2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "neologism"
                            noun_pair_prefixes[pos-1] = ""
                            noun_pair_ends[pos-1] = second
                            break
                # Schaue, ob das Wort davor ein Wort ist, das auf "mann", "frau", "herr" oder "dame" endet:
                person_pattern = r"(.*)((m(a|ä)nn(er)?)|(frau(en)?)|herr|dame)$"
                match = re.match(person_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_person_pattern = match.group(1) + r"((m(a|ä)nn(er)?)|(frau(en)?)|herr|dame)$"
                    if re.match(same_person_pattern, second_noun[2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = 0
                        noun_pair_types[pos-1] = "person"
                        noun_pair_prefixes[pos-1] = match.group(1).capitalize()
                        noun_pair_ends[pos-1] = second
                # Schaue, ob das Wort davor auf "sohn" oder "tochter" endet:
                kind_pattern = r"(.*)(s(o|ö)hne?|t(o|ö)chter)$"
                match = re.match(kind_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_kind_pattern = match.group(1) + r"(s(o|ö)hne?|t(o|ö)chter)$"
                    if re.match(same_kind_pattern, second_noun[2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = 0
                        noun_pair_types[pos-1] = "kind"
                        noun_pair_prefixes[pos-1] = match.group(1).capitalize()
                        noun_pair_ends[pos-1] = second
                # Schaue, ob das Wort davor auf "beamt..." endet:
                beamt_pattern = r"(.*)(beamt(in(nen)?|e(r|n|m)?))$"
                match = re.match(beamt_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_beamt_pattern = match.group(1) + r"(beamt(in(nen)?|e(r|n|m)?))$"
                    if re.match(same_beamt_pattern, second_noun[2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = 0
                        noun_pair_types[pos-1] = "beamtey"
                        noun_pair_prefixes[pos-1] = match.group(1).capitalize()
                        noun_pair_ends[pos-1] = second
                # Schaue, ob das Wort davor ein Romanismus ist:
                for j, romanism in enumerate(Lexicon.ROMAN_NOUNS):
                    romanism = "(" + romanism + ")$"
                    if re.match(romanism.lower(), self.parse_list[pos-1][2].lower()):
                        # Schaue, ob das Wort danach der entsprechende Romanismus ist:
                        if re.match(romanism.lower(), second_noun[2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "romanism"
                            noun_pair_prefixes[pos-1] = ""
                            noun_pair_ends[pos-1] = second
                            break
                # Schaue, ob das Wort davor ein irreguläres Substantiv ist:
                for j, irregular_noun in enumerate(Lexicon.IRREGULAR_NOUNS):
                    irregular_noun = "(" + irregular_noun + ")$"
                    if re.match(irregular_noun.lower(), self.parse_list[pos-1][2].lower()):
                        # Schaue, ob das Wort danach das entsprechende irreguläre Substantiv ist:
                        if re.match(irregular_noun.lower(), second_noun[2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "irregular"
                            noun_pair_prefixes[pos-1] = ""
                            noun_pair_ends[pos-1] = second
                            break
                # Schaue, ob das Wort davor ein substantiviertes Adjektiv ist:
                for j, subadj in enumerate(Lexicon.SUBST_ADJ):
                    subadj = "(" + subadj + ")(r|n)?$"
                    match = re.match(subadj.lower(), self.parse_list[pos-1][2].lower())
                    if match:
                        # Schaue, ob das Wort danach das entsprechende Wort ist:
                        same_subadj = match.group(1) + r"(r|n)?$"
                        if re.match(same_subadj.lower(), second_noun[2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = match.group(1).capitalize()
                            noun_pair_types[pos-1] = "substantivized adjective"
                            noun_pair_prefixes[pos-1] = ""
                            noun_pair_ends[pos-1] = second
                            break
                # Schaue, ob das Wort davor ein auf "sprachige" endendes substantiviertes Adjektiv ist:
                sprachige_pattern = r"(..+sprachige)(r|n|m|s)?$"
                match = re.match(sprachige_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_sprachige_pattern = match.group(1) + r"(r|n|m|s)?$"
                    if re.match(same_sprachige_pattern, second_noun[2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = match.group(1).capitalize()
                        noun_pair_types[pos-1] = "substantivized adjective"
                        noun_pair_prefixes[pos-1] = ""
                        noun_pair_ends[pos-1] = second

        # Alle Positionen, die von einer Doppelnennung verschluckt werden: von der Konjunktion bis
        # zum zweiten Substantiv einschliesslich seines Artikels und seiner Attribute.
        covered_by_pair = set()
        for first in noun_pair_positions:
            covered_by_pair.update(range(first + 1, noun_pair_ends[first] + 1))

        nouns = ""
        for pos, word_parse in enumerate(self.parse_list):
            # split_prepositions hat "im", "am", "zur" und dergleichen in Präposition und Artikel
            # zerlegt; vom Artikel steht im Eingabetext nur das "m" oder "r". Ein solcher Rest ist
            # kein eigenständiges Wort und darf nicht markierbar sein -- er wird als Teil der
            # Nominalphrase mitneutralisiert. ParZu taggt ihn sonst gelegentlich als
            # Relativpronomen, woraus dann "iderm Anschluss" statt "im Anschluss" würde.
            if word_parse[3] in ("ART", "PRO") and word_parse[-2] in ("m", "r"):
                nouns += escape(word_parse[-2])
                nouns += escape(word_parse[-1])
            # Wörter mit einer eigenen Form im Inklusivum ("kaufmännisch" wird zu
            # "kaufleutisch", "jungfräulich" zu "jungferlich"). Sie bekommen ein eigenes Kästchen,
            # weil sie an keiner Personenbezeichnung hängen müssen. Die Prüfung steht vorn, weil
            # "Jungfräulichkeit" ein Substantiv ist und sonst im Substantiv-Zweig hängenbliebe.
            elif Lexicon.neutralize_irregular_word(word_parse[-2]) is not None:
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                nouns += input_form
            # Wenn pos die Position einer Doppelnennung ist, dann mache die gesamte Doppelnennung markierbar:
            elif pos in noun_pair_positions:
                self.find_nounphrase(word_parse)
                # Die Doppelnennung reicht vom ersten Substantiv bis zum zweiten. Dazwischen steht
                # die Konjunktion und gegebenenfalls ein eigener Artikel des zweiten Substantivs
                # ("der Lehrer oder die Lehrerin"); all das kommt in dasselbe Kästchen.
                end = noun_pair_ends[pos]
                marked_text = escape(word_parse[-2]) + escape(word_parse[-1])
                for other in range(pos+1, end):
                    marked_text += escape(self.parse_list[other][-2]) + escape(self.parse_list[other][-1])
                marked_text += escape(self.parse_list[end][-2])
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{1}" name="{sentence_number}|{word_parse[0]}|{1}" value="select"><label for="{sentence_number}|{word_parse[0]}|{1}">{'<span class="markable">' + marked_text + '</span>'}</label></div>{escape(self.parse_list[end][-1])}"""
                nouns += input_form
                self.noun_pair_spans[int(word_parse[0])] = list(range(pos+1, end+1))
                prefix = noun_pair_prefixes[pos]
                if prefix == "":
                    is_capitalized = True
                else:
                    is_capitalized = False
                self.nounlist.extend([[int(word_parse[0]), 0, "", "", prefix, "prefix", True, False], [int(word_parse[0]), 0, word_parse[1], noun_pair_indices[pos], "", noun_pair_types[pos], is_capitalized, True]])
            elif pos in covered_by_pair:
                continue
            else:
                # Determine whether pos depends on some noun phrase:
                dependent = False
                for key in self.nounphrases:
                    if pos+1 in self.nounphrases[key]:
                        dependent = True
                        break
                # Case: Possessive pronoun
                match = re.match(r"((S|s)ein)|((I|i)hr)", word_parse[1])
                if word_parse[4] == "PPOSAT" and word_parse[6] == "0" and match:
                    self.find_nounphrase(word_parse)
                    sonderzeichen_match = re.match(r"((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)([/*_:])((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)$", word_parse[-2])
                    # The following case distinction is needed to ensure that when only the base is markes,
                    # "ihrer*seiner" becomes "enser" and not "enser*enser", while "ihre(r)" becomes "ense(r)" and not "ense".
                    if sonderzeichen_match:
                        base = sonderzeichen_match.group(1)
                        marking_form_base = sonderzeichen_match.group(1) + sonderzeichen_match.group(4) + sonderzeichen_match.group(7) + sonderzeichen_match.group(8)
                        ending = sonderzeichen_match.group(11)
                        #grammatical_ending = word_parse[1][len(base):]
                        print("base:",base)
                        print("marking_form_base:",marking_form_base)
                        print("ending:",ending)
                    else:
                        base = match.group(0)
                        marking_form_base = match.group(0)
                        ending = word_parse[-2][len(base):]
                    capitalized = word_parse[1][0].isupper()
                    # Since ParZu does not identify the neuter form of possessive pronouns as such, we identify them by the ending "es":
                    if word_parse[1].endswith("es"):
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-3}" name="{sentence_number}|{word_parse[0]}|{-3}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-3}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                        nouns += input_form
                        self.nounlist.extend([[int(word_parse[0]), 0, base, "ens", "", "possessive_pronoun_base", capitalized, False], [int(word_parse[0]), len(base), ending, ending, "", "possessive_pronoun_ending", False, False]])
                    else:
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-3}" name="{sentence_number}|{word_parse[0]}|{-3}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-3}">{'<span class="markable">' + marking_form_base + '</span>'}</label></div>"""
                        nouns += input_form
                        if len(ending) > 0:
                            input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-4}" name="{sentence_number}|{word_parse[0]}|{-4}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-4}">{'<span class="markable">' + ending + '</span>'}</label></div>"""
                            nouns += input_form
                        nouns += escape(word_parse[-1])
                        self.nounlist.extend([[int(word_parse[0]), 0, base, "ens", "", "possessive_pronoun_base", capitalized, False], [int(word_parse[0]), len(base), ending, "", "", "possessive_pronoun_ending", False, False]])
                elif word_parse[4] == "PPOSAT" and word_parse[6] == "0":
                    # Since ParZu does not identify the neuter form of possessive pronouns as such, we identify them by the ending "es":
                    if word_parse[1].endswith("es"):
                        nouns += escape(word_parse[-2])
                        nouns += escape(word_parse[-1])
                    else:
                        self.find_nounphrase(word_parse)
                        match = re.match(r"(M|m|D|d)ein|(U|u)nse?r|(E|e)ue?r", word_parse[1])
                        if match:
                            base = match.group(0)
                            ending = word_parse[1][len(base):]
                        else:
                            base = word_parse[1][:len(word_parse[2]-1)]
                            ending = word_parse[1][len(word_parse[2]-1):]
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-5}" name="{sentence_number}|{word_parse[0]}|{-5}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-5}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                        nouns += input_form
                        self.nounlist.extend([[int(word_parse[0]), 0, base, base, "", "possessive_pronoun_base", False, False], [int(word_parse[0]), len(base), ending, "", "", "possessive_pronoun_ending", False, False]])
                # Case: "sein" as a single word in the input
                elif word_parse[1] == "sein" and len(self.parse_list) == 1:
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-3}" name="{sentence_number}|{word_parse[0]}|{-3}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-3}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                    self.parse_list[pos] = ['1', 'sein', 'seine', 'ART', 'PPOSAT', 'Neut|Nom|Sg', '0', 'det', '_', '_', 'sein', '']
                    print("modified word_parse for sein")
                    self.nounlist.extend([[int(word_parse[0]), 0, "sein", "sein", "", "possessive_pronoun_base", False, False], [int(word_parse[0]), 4, "", "", "", "possessive_pronoun_ending", False, False]])

                # Case: Possessive article
                elif word_parse[4] == "PPOSAT" and not re.match(r"(M|m|D|d)ein|(U|u)nse?r|(E|e)ue?r", word_parse[1]):
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-2}" name="{sentence_number}|{word_parse[0]}|{-2}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-2}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form

                # Case: Noun
                # Here we also need to consider capitalized adjectives that do not depend on a noun.
                # Hängt ein grossgeschriebenes Adjektiv als Genitivattribut ("gmod") an einem Nomen,
                # ist es ebenfalls substantiviert ("das Buch meiner Lieben"); ein attributives
                # Adjektiv trägt dort "attr".
                elif word_parse[3] == "N" or self.is_name_epithet(pos) or (word_parse[3] == "ADJA" and Lexicon.starts_uppercase(word_parse[1]) and (not self.parse_list[int(word_parse[6])-1][3] == "N" or word_parse[7] == "gmod")):
                    # Ein grossgeschriebenes Adjektiv ohne Nomen darüber ist substantiviert. ParZu
                    # gibt es aber nicht immer als Nomen aus -- "liebe Kim" wird beim Reparse zu
                    # einem Nomen, "liebe Juli" wegen des Monatsnamens nicht. Die Zeile wird deshalb
                    # auf ein Nomen umgeschrieben, so wie unten allein stehende Artikel zu Pronomen
                    # werden; sonst greift bei der Neutralisierung der Zweig für Substantive nicht.
                    is_epithet = self.is_name_epithet(pos)
                    if word_parse[3] == "ADJA":
                        # ParZu liefert für solche Wörter oft ein falsches Lemma. Die
                        # Grossschreibung der Wortform kann dabei künstlich sein:
                        # search_lonely_adjectives schreibt allein stehende Adjektive vor dem
                        # Reparse gross, damit ParZu sie als substantiviert erkennt. Ob sie echt
                        # ist, verrät die Realisierung aus dem Eingabetext. Ohne diese Prüfung
                        # wandert die künstliche Grossschreibung ins Lemma und von dort in die
                        # Ausgabe: "und die einzige, für die es sich zu kämpfen lohnt" ergäbe
                        # "die Einzige".
                        lemma = word_parse[1]
                        if word_parse[-2][:1].islower():
                            lemma = lemma[:1].lower() + lemma[1:]
                        word_parse[2] = lemma
                        # Merkmalsliste von "Pos|Genus|Kasus|Numerus|Flexion|" auf "Genus|Kasus|Numerus".
                        # Beim Beinamen sind die Merkmale des Adjektivs leer, die des Artikels aber
                        # gesetzt ("dem" ist "Def|_|Dat|Sg"), deshalb werden sie von dort übernommen.
                        source_feats = self.parse_list[pos-1][5] if is_epithet else word_parse[5]
                        adjective_feats = source_feats.split("|")
                        if len(adjective_feats) >= 4:
                            self.parse_list[pos][5] = "|".join(adjective_feats[1:4])
                        self.parse_list[pos][3] = "N"
                    self.find_nounphrase(word_parse)
                    if is_epithet:
                        # Der vorangehende Artikel wird der Nominalphrase zugeschlagen, damit er
                        # mitneutralisiert wird ("Peter dem Großen" ergibt "Peter derm Großen").
                        if pos not in self.nounphrases[int(word_parse[0])]:
                            self.nounphrases[int(word_parse[0])].append(pos)
                    feats = self.parse_list[pos][5].split("|")
                    if len(feats) == 1:
                        feats = ["_","_","_"]
                    if feats[2] == "_":
                        self.determine_number(pos,feats)
                    # The following hack is needed, because ParZu often misinterprets "Pole" as "Pol":
                    if word_parse[2] == "Pol" and (word_parse[1] == "Pole" or word_parse[1] == "Polen"):
                        word_parse[2] = "Pole"
                        word_parse[4] = "N"
                        feats[0] = "Masc"
                    # The following is needed, because ParZu often misinterprets plural "Ungarn" as the country, not the people:
                    if word_parse[1] == "Ungarn" and feats[2] == "Pl":
                        word_parse[2] = "Ungar"
                        word_parse[4] = "N"
                    # The following looks for articles that are relevant for proper nouns, i.e. masculine and feminine article in the singular:
                    has_article = False
                    for other_word_parse in self.parse_list:
                        if other_word_parse[6] == word_parse[0] and other_word_parse[3] == "ART":
                            article_feats = other_word_parse[5].split("|")
                            # ParZu lässt die Merkmale eines Artikels manchmal ganz offen und
                            # liefert nur "_" statt "Bestimmtheit|Genus|Kasus|Numerus". Ein
                            # solcher Artikel sagt nichts über Genus und Numerus aus und zählt
                            # deshalb wie kein Artikel.
                            if (len(article_feats) >= 3 and article_feats[-1] != "Pl"
                                    and (article_feats[-3] == "Masc" or article_feats[-3] == "Fem")):
                                has_article = True
                    # The following checks whether some possessive form ("sein", "ihr", "mein", "dein", "unser", "euer", "dessen", "deren") is dependent on the noun:
                    has_possessive = False
                    for other_word_parse in self.parse_list:
                        if other_word_parse[6] == word_parse[0] and (other_word_parse[4] == "PPOSAT" or other_word_parse[1] in ["dessen","deren"]):
                            has_possessive = True
                    print("about to check noun:", word_parse)
                    print("has_article:",has_article)
                    # Ein Eigenname ohne Artikel wird markierbar, wenn ein Adjektiv an ihm hängt,
                    # das neutralisiert werden muss ("liebe Sonja" wird zu "liebey Sonja"). Wie bei
                    # der Artikelprüfung bleiben Neutra aussen vor, damit Ortsnamen wie "das schöne
                    # Berlin" oder "das alte Europa" unberührt bleiben.
                    has_adjective = False
                    has_person_adjective = False
                    for other_word_parse in self.parse_list:
                        if other_word_parse[6] == word_parse[0] and other_word_parse[3] == "ADJA":
                            adjective_feats = other_word_parse[5].split("|")
                            if len(adjective_feats) > 1 and adjective_feats[1] != "Neut":
                                has_adjective = True
                            # Ein Anrede-Adjektiv zeigt an, dass ein mehrdeutiger Name hier eine
                            # Person bezeichnet ("liebe Juli", aber nicht "im Juli").
                            if other_word_parse[2] in Lexicon.PERSON_ADJECTIVES:
                                has_person_adjective = True
                    # Namen aus MASCULINE_NAMES erkennt man am maskulinen Artikel oder Adjektiv;
                    # bei beiden Wortarten steht das Genus an derselben Stelle der Merkmalsliste.
                    # ParZu überträgt allerdings das Genus des Substantivs auf das Adjektiv, sodass
                    # "Lieber Mark!" als Femininum erscheint ("die Mark"). Ohne Artikel zählt daher
                    # zusätzlich die Oberflächenform: die starke Endung "-er" ist im Nominativ
                    # maskulin, während sie im Genitiv und Dativ feminin sein könnte.
                    has_masculine_modifier = False
                    for other_word_parse in self.parse_list:
                        if other_word_parse[6] != word_parse[0] or other_word_parse[3] not in ("ART", "ADJA"):
                            continue
                        modifier_feats = other_word_parse[5].split("|")
                        if len(modifier_feats) > 1 and modifier_feats[1] == "Masc":
                            has_masculine_modifier = True
                        elif (not has_article and other_word_parse[3] == "ADJA"
                                and other_word_parse[1].lower().endswith("er")
                                and feats[1] in ("Nom", "_")):
                            has_masculine_modifier = True
                    # Bleibt das Genus in ParZus Analyse offen, lässt es sich oft an der Form des
                    # Determinierers ablesen: "jede" ist feminin, "jeden" maskulin. Nur eindeutige
                    # Endungen zählen -- "der" wäre maskuliner Nominativ oder femininer
                    # Genitiv/Dativ, "dem" maskulin oder neutrum, "das" neutrum.
                    # Hängt das Substantiv als Apposition an "ich" oder "du", bezeichnet es
                    # sicher eine Person. ParZu wählt dort manchmal die falsche Grundform, wenn
                    # die Wortform zugleich ein gewöhnliches Substantiv sein kann: Zu "Du Arme!"
                    # liefert es "Arm" (die Gliedmasse) statt "Arme". Ist die Wortform selbst
                    # eine bekannte Substantivierung, wird sie deshalb als Grundform genommen.
                    if (word_parse[7] == "app" and int(word_parse[6]) != 0
                            and self.parse_list[int(word_parse[6])-1][4] == "PPER"
                            and self.parse_list[int(word_parse[6])-1][2] in ("ich", "du")
                            and word_parse[2] not in Lexicon.SUBSTANTIVIZABLE_ADJ
                            and word_parse[1] in Lexicon.SUBSTANTIVIZABLE_ADJ):
                        word_parse[2] = word_parse[1]

                    inferred_gender = "_"
                    if feats[0] == "_" and feats[2] != "Pl":
                        article_form = ""
                        for other_word_parse in self.parse_list:
                            if other_word_parse[6] == word_parse[0] and other_word_parse[3] == "ART":
                                form = other_word_parse[1].lower()
                                article_form = form
                                if form.endswith("en"):
                                    inferred_gender = "Masc"
                                    break
                                if form.endswith("e"):
                                    inferred_gender = "Fem"
                                    break
                        # Gibt der Determinierer das Genus nicht her, verrät es die Endung des
                        # Wortes selbst -- aber nur in der starken Deklination, also nach einem
                        # endungslosen Determinierer ("ein Anderer") oder ganz ohne einen
                        # ("Du Armer"). Nach "der", "die" oder "das" steht die schwache Form, die
                        # im Maskulinum und im Femininum gleich lautet ("der Alte", "die Alte").
                        if inferred_gender == "_" and (article_form == ""
                                                       or article_form in Marking_Tool.ENDINGLESS_DETERMINERS):
                            if word_parse[1].endswith("er"):
                                inferred_gender = "Masc"
                            elif word_parse[1].endswith("e"):
                                inferred_gender = "Fem"

                    # Ein bestimmter Artikel unterscheidet sich vom unbestimmten und vom
                    # Possessivum; "Die Linke" ist die Partei, "eine Linke" eine Person.
                    has_definite_article = False
                    for other_word_parse in self.parse_list:
                        if (other_word_parse[6] == word_parse[0] and other_word_parse[4] == "ART"
                                and other_word_parse[5].startswith("Def")):
                            has_definite_article = True
                    head_identified, prefix, components = Lexicon.check_noun(word_parse,feats,has_article,has_possessive,has_adjective,has_person_adjective,has_masculine_modifier,is_epithet,has_definite_article,inferred_gender)
                    print(components)
                    if components == []:
                        nouns += escape(word_parse[-2])
                        nouns += escape(word_parse[-1])
                    elif len(components) == 1 and components[0][3] == "":
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{1}" name="{sentence_number}|{word_parse[0]}|{1}" value="select"><label for="{sentence_number}|{word_parse[0]}|{1}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                        nouns += input_form
                    else:
                        input_form = Marking_Tool.create_input_form(self, sentence_number, word_parse, components)
                        nouns += escape(prefix) + input_form + escape(word_parse[-1])
                    if components != []:
                        self.marked_nouns.append(int(word_parse[0]))
                    for i in range(len(components)):
                        components[i].insert(0, int(word_parse[0]))
                        components[i].append(False)
                    if components != []:
                        components[-1][-1] = head_identified
                    components.insert(0, [int(word_parse[0]), 0, "", "", prefix, "prefix", False, False])
                    self.nounlist.extend(components)
                # Case: Pronoun
                elif word_parse[3] == "PRO" and (word_parse[5][0] == "3" or (word_parse[4] == "PPER" and word_parse[5][0] == "_" and word_parse[2] != "du") or word_parse[4] == "PIS" or word_parse[4] == "PDS") and not word_parse[4] == "PRF" and ("Neut" not in word_parse[5])  and ("Pl" not in word_parse[5]) and not word_parse[2] == "viel" and not word_parse[2] == "viele" and not word_parse[2] == "mehr" and not word_parse[2] == "wenig" and not word_parse[2] == "wenige" and not word_parse[2] == "alle" and not word_parse[2] == "etwas" and not word_parse[2] == "was" and not word_parse[2] == "sowas" and not word_parse[2] == "nichts" and not word_parse[1].startswith("das") and not word_parse[1] == "d." and not word_parse[1] == "s" and not (word_parse[1] == "Sie" and not word_parse[0] == "1") and not word_parse[2] == "einige" and not (word_parse[2].startswith("andere") and self.parse_list[pos-1][2] == "alle") and not (word_parse[1] == "anderem" and self.parse_list[pos-1][2] == "unter") and not word_parse[2] == "a."  and not (word_parse[2].startswith("andere") and self.parse_list[pos-1][2] == "alle") and not self.plural_by_verb(pos): # The last three cases are there to avoid the second part of "alles andere", "unter anderem" and "u. a." from being markable.
                    print("found pronoun:",word_parse)
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                # Case: Relative pronoun dependent on a proper noun
                elif word_parse[4] == "PRELS" and pos > 1 and ((self.parse_list[pos-1][1] == "," and self.parse_list[pos-2][4] == "NE") or (pos != 2 and self.parse_list[pos-2][1] == "," and self.parse_list[pos-3][4] == "NE")) and not word_parse[5].startswith("Neut") and not word_parse[5].endswith("Pl") and not self.covered_by_marked_nounphrase(word_parse):
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                # Case: welche
                elif word_parse[3] == "PRO" and word_parse[4] == "PWS" and word_parse[2] == "welche":
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                # case: jemand (sometimes marked as adjective, should still be neutralizable in that case)
                elif re.match(r"(J|j)emand(e?)s" , word_parse[1]):
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                elif word_parse[3] == "PREP" and word_parse[4] == "APPRART":
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                elif word_parse[4] == "PRELAT" or word_parse[1].lower() in ["dessen","deren"]:
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                # Ein Relativpronomen, das ParZu an keine Nominalphrase angebunden hat, bleibt
                # markierbar -- im Neutrum und im Plural aber nicht: "was" und "das" bezeichnen
                # keine Person ("wenig zu hören, was man kennt"), und Pluralformen sind im
                # Inklusivum ohnehin unverändert. Dieselben Bedingungen gelten im Zweig für
                # Relativpronomen an einem Eigennamen.
                elif (word_parse[4] == "PRELS" and not dependent
                        and not word_parse[5].startswith("Neut")
                        and not word_parse[5].endswith("Pl")):
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                    nouns += input_form
                # Ein Artikel an der Satzwurzel wird pronominal verwendet ("Nur eine von hundert
                # kennt ..."). Dann kennt ParZu sein Genus. Bleibt es unbestimmt, handelt es sich
                # um einen Artikel, den ParZu nur nicht an sein Substantiv anbinden konnte -- so
                # in "Die von Peter dem Großen gegründete Akademie ...".
                elif word_parse[3] == "ART" and word_parse[6] == "0" and word_parse[5].split("|")[1:2] in (["Masc"], ["Fem"]) and ("Pl" not in word_parse[5]) and not word_parse[1].startswith("das") and not word_parse[2] == "wenige":
                    # Search if the article is part of a noun phrase:
                    article_dependent = False
                    for key in self.nounphrases:
                        if pos+1 in self.nounphrases[key]:
                            article_dependent = True
                            break
                    if not article_dependent:
                        print("found article:",word_parse)
                        self.find_nounphrase(word_parse)
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{'<span class="markable">' + escape(word_parse[-2]) + '</span>'}</label></div>{escape(word_parse[-1])}"""
                        nouns += input_form
                        # The following is needed so that the "article" is treated as a pronoun during the neutralization process:
                        self.parse_list[pos][3] = "PRO"
                        self.parse_list[pos][4] = "PIS"
                        if word_parse[5].startswith("Indef|"):
                            self.parse_list[pos][5] = word_parse[5][6:]
                        if word_parse[5].startswith("Def|"):
                            self.parse_list[pos][5] = word_parse[5][4:]
                    else:
                        nouns += escape(word_parse[-2])
                        nouns += escape(word_parse[-1])
                else:
                    nouns += escape(word_parse[-2])
                    nouns += escape(word_parse[-1])
        print(self.nounphrases)
        return nouns
    
    # Generates the html form for a single (possibly compund) noun, with checkboxes next to the components.
    def create_input_form(self, sentence_number, word_parse, components):
        print("components")
        print(components)
        input_form = ""
        for i in range(len(components)):
            input_form += f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{i+1}" name="{sentence_number}|{word_parse[0]}|{i+1}" value="select"><label for="{sentence_number}|{word_parse[0]}|{i+1}">{'<span class="markable">' + escape(components[i][1]) + '</span>'}</label></div>{escape(components[i][3])}"""
            if i == len(components)-1 and components[i][3] == "":
                input_form += escape(word_parse[-1])
        return input_form

    # This function takes the parse list and the original input text and finds the realizations of the words in the input text.
    def find_realizations(self, input_text: str):
        position_after_preposition = False
        for word in self.parse_list:
            print("word:",word)
            if position_after_preposition == True and word[1].startswith("d") and len(word[1]) == 3:
                pattern = "(" + re.escape(word[1]) + "|" + re.escape(word[1][2]) + ")"
            elif word[1].lower() == "in":
                pattern = "(in|i(?!n))"
            elif word[1].lower() == "an":
                pattern = "(an|a(?!n))"
            elif word[1].lower() == "von":
                pattern = "(von|vo(?!n))"
            elif word[1] == '"':
                pattern = '("|„|“|”)'
            elif word[1] == "seines" or word[1] == "ihres" or word[1] == "Ihres":
                pattern = "(sein|ihr|Ihr)e?s([*_:/](sein|ihr|Ihr)e?s)?"
            elif re.match(r"^.*[a-zA-ZäöüßÄÖÜẞ]{3}in(nen)?.*$",word[1]):
                match = re.match(r"^(.*[a-zA-ZäöüßÄÖÜẞ]{3})in((nen)?)(.*)$",word[1])
                pattern = match.group(1) + "(\(in" + match.group(2) + "\)|([*_:/]|/-)?in"  + match.group(2) + "|\(inn\)en)" + match.group(4)
            elif word[1] in ["sie","Sie"]:
                pattern = "[Ss]ie([*_:/][Ee]r|[*_:/][Ih]hn)?|[Ee]r[*_:/][Ss]ie|[Ii]hn[*_:/][Ss]ie"
            elif word[1] in ["ihr","Ihr"]:
                pattern = "[Ii]hr([*_:/][Ii]hm|[*_:/][Ss]ein)?|[Ii]hm[*_:/][Ii]hr|[Ss]ein[*_:/][Ii]hr"
            elif word[1] in ["ihre","Ihre"]:
                pattern = "[Ss]ein([*_:/]e|\(e\)|e[*_:/][rn]|e\([rn]\)|e)?[*_:/][Ii]hr([*_:/]e|\(e\)|e[*_:/][rn]|e\([rn]\)|e)|[Ii]hr([*_:/]e|\(e\)|e[*_:/][rn]|e\([rn]\)|e)?([*_:/][Ss]ein([*_:/]e|\(e\)|e[*_:/][rn]|e\([rn]\)|e))?"
            elif word[1] in ["ihrer","Ihrer"]:
                pattern = "[Ss]ein(e([*_:/]r|\(r\)|[ms][*_:/]r|r([*_:/][ms])?))?[*_:/][Ii]hre([*_:/]r|\(r\)|[ms][*_:/]r|r([*_:/][ms])?)|[Ii]hrer[*_:/][Ss]eine([*_:/]r|\(r\)|[ms][*_:/]r|r([*_:/][ms])?)|[Ii]hr(e([*_:/]r|\(r\)|[ms][*_:/]r|r([*_:/][ms])?))?([*_:/][Ss]eine([*_:/]r|\(r\)|[ms][*_:/]r|r([*_:/][ms])?))?"
            elif word[1].lower().startswith("ihr"):
                pattern = re.escape(word[1])[:3] + "(" + re.escape(word[1][3:]) + ")?([*_:/][Ss]ein(" + re.escape(word[1][3:]) + ")?)?|[Ss]ein" + re.escape(word[1][3:]) + "[*_:/][Ii]hr" + re.escape(word[1][3:])
            elif word[1] in ["die","Die"]:
                pattern = "[Dd]ie([*_:/][Dd]e[rn]|[*_:/][rn])?|[Dd]e[rn][*_:/][Dd]ie"
            elif word[1] in ["der","Der"]:
                pattern = "([Dd]er([*_:/][Dd]e[ms]|[*_:/][ms])?|[Dd]e[ms][*_:/][Dd]er)"
            elif re.match(re.compile(r"[mdks]?eine$", re.IGNORECASE),word[1]):
                # "([mdks]?)" statt "([mdks])?": Ein Rueckverweis auf eine Gruppe, die gar nicht
                # mitgespielt hat, scheitert immer. Die praefixlosen Doppelformen ("ein*eine")
                # liessen sich deshalb nicht auf den Eingabetext zurueckfuehren.
                pattern = r"([mdks]?)eine([*_:/][rn]|[*_:/]\1ein(er|en)?)?|([mdks]?)ein(er|en)?[*_:/]\4eine|ein[*_:/]e"
            elif re.match(re.compile(r"[mdks]?einer$", re.IGNORECASE),word[1]):
                pattern = r"([mdks]?)eine(r[*_:/][ms]|[ms][*_:/]r|r[*_:/]\1eine[ms]|r)|([mdks]?)eine[ms][*_:/]\3einer"
            elif word[1].endswith("e"):
                pattern = re.escape(word[1]) + "([*_:/][rn]|\([rn]\))?(?=($|" + Marking_Tool.WORD_DELIMITERS + "))|" + re.escape(word[1][:-1]) + "\(e\)(?=($|" + Marking_Tool.WORD_DELIMITERS + "))"
            elif word[1].endswith("er"):
                pattern = re.escape(word[1]) + "([*_:/][ms])?(?=($|" + Marking_Tool.WORD_DELIMITERS + "))|" + re.escape(word[1][:-1]) + "([ms])[*_:/]r(?=($|" + Marking_Tool.WORD_DELIMITERS + "))"
            # elif re.match(r"(.*[a-zA-ZäöüßÄÖÜẞ])in(.*)" , word[1]):
            #     match = re.match(r"(.*[a-zA-ZäöüßÄÖÜẞ])in(.*)" , word[1])
            #     pattern = re.escape(word[1]) + "|" + match.group(1) + "In" + match.group(2)
            else:
                pattern = re.escape(word[1])
            match = re.search("^" + pattern, input_text, re.IGNORECASE)
            if match:
                realization = match.group(0)
                remaining_text = input_text[match.end():]
                # \s erfasst alle Unicode-Leerzeichen. ParZus Tokenizer trennt auch an schmalen und
                # typografischen Leerzeichen (U+2000 bis U+200A, U+202F, U+3000 ...); ohne sie
                # hier liefe die Zuordnung der Wörter auf den Eingabetext aus dem Tritt.
                whitespace_pattern = "^\\s*"
                whitespace_match = re.search(whitespace_pattern,remaining_text)
                input_text = remaining_text[whitespace_match.end():]
                white_realization = whitespace_match.group(0)
            else:
                print(input_text)
                raise Exception("The word \"" + pattern + "\" could not be found in the input text, even though it was expected according to the parse list")
            #realization, input_text = self.find_prefix_regex(pattern,input_text)
            word.append(realization)
            word.append(white_realization)
            if word[1] in ["bei","Bei","zu","Zu","in","In","von","Von","vor","Vor","an","An","auf","Auf","für","Für"]:
                position_after_preposition = True
            else:
                position_after_preposition = False
        return input_text


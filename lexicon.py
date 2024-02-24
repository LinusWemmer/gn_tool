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

    ALREADY_NEUTRAL_NOUNS = ["Gast", "Vormund", "Anarcho", "Hetero", "Homo", "Normalo", "Realo", "Waise", "Geisel", "Koryphäe", "Abkömmling", "Ankömmling", "Eindringling", "Erdling", "Flüchtling", "Fremdling", "Günstling", "Häftling", "Häuptling", "Jüngling", "Lehrling", "Liebling", "Neuling", "Pflegling", "Prüfling", "Säugling", "Schützling", "Sträfling", "Täufling", "Zögling", "Zwilling", "Flüchtling", "Charakter", "Wache", "Profi", "Studi", "Nazi", "Admin", "Fan", "Star", "Boss", "Clown", "Punk", "Hippie", "Freak", "Nerd", "Yuppie", "Hooligan", "Judoka", "Aikidoka", "Karateka", "Barista", "Jedi", "Sith", "Engel"]

    # NEOLOGISMS lists singular forms as well as forms that occur in compounds
    NEOLOGISMS = [r"(Br(u|ü)der)|(Schwester)", r"(V(a|ä)ter)|(M(u|ü)tter)", r"O(p|m)a", r"Uro(p|m)a", r"Ururo(p|m)a", r"(Onkel)|(Tanten?)", r"Cousin(e|en)?|Vetter|Base", r"Tochter|Sohn(es)?", r"Jungfrau(en)?", r"Mädchen|Jung(e|en|s)", r"Neffen?|Nichten?"]  
    NEOLOGISMS_NEUTRAL = ["Geschwister", "Elter", "Ota", "Urota", "Ururota", "Tonke", "Couse", "Spross", "Jungfere", "Kid", "Nefte"]
    NEOLOGISMS_PLURAL = ["Geschwister", "Eltern", "Otas", "Urotas", "Ururotas", "Tonken", "Couserne", "Sprosse", "Jungferne", "Kids", "Neften"]
    NEOLOGISMS_COMPOUND = ["Geschwister", "Elter", "Ota", "Urota", "Ururota", "Tonken", "Couserne", "Spross", "Jungferne", "Kid", "Neften"]

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

    # Neutralizes words where a neologism is the neutral form 
    def neutralize_neologism(feats, index) -> str:
        if feats[2] == "Pl":
            noun = Lexicon.NEOLOGISMS_PLURAL[index]
            if index in [0,5,6] and feats[1] == "Dat":
                return noun + "n"
            else:
                return noun
        else:
            noun = Lexicon.NEOLOGISMS_NEUTRAL[index]
            if feats[1] == ("Gen") and index == 7:
                return noun + "es"
            elif feats[1] == ("Gen"):
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
            ending = Lexicon.ARTIKEL_JEDER.get(feats[1])
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
            ending = Lexicon.ARTIKEL_JEDER.get(feats[1])
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
            article =  Lexicon.ARTIKEL_DER.get(feats[2])
            return article.capitalize() if is_capitalized else article
        # Case Indifinitive Artikels, only ein
        elif feats[0] == "Indef":
            if feats[2] == "_":
                feats[2] = "Nom"
            article = "ein" +  Lexicon.ARTIKEL_EIN.get(feats[2])
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
                    article =  Lexicon.ARTIKEL_DER.get(feats[1]) + "selben"
                    return article.capitalize() if is_capitalized else article
            # derjenige/diejenige:
            if re.match(r"d..jenige.?$", word):
                if feats[1] == "Nom" or feats[1] == "Acc":
                    return "Dejenige" if is_capitalized else "dejenige"
                else:
                    article =  Lexicon.ARTIKEL_DER.get(feats[1]) + "jenigen"
                    return article.capitalize() if is_capitalized else article
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon.JEDER_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon.ARTIKEL_JEDER.get(feats[1])
                    return article.capitalize() if is_capitalized else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon.EIN_PARADIGM:
                if word.startswith(start):
                    sonderzeichen_match = re.match(r"((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)([/*_:])((S|s)ein|(I|i)hr)(([/*_:]?e|\(e\)|s|es|em|en|er)?([/*_:][smnr]|\([rn]\))?)$", word_parse[-2])
                    if sonderzeichen_match:
                        article = sonderzeichen_match.group(1) + Lexicon.ARTIKEL_EIN.get(feats[1]) + sonderzeichen_match.group(7) + sonderzeichen_match.group(8) + Lexicon.ARTIKEL_EIN.get(feats[1])
                    else:
                        article = start + Lexicon.ARTIKEL_EIN.get(feats[1])
                    return article.capitalize() if is_capitalized else article
            if re.match(r"unse?re?.?$", word):
                article = Lexicon.ARTIKEL_UNSER.get(feats[1])
                return article.capitalize() if is_capitalized else article
            elif re.match(r"eue?re?.?$", word):
                article = Lexicon.ARTIKEL_EUER.get(feats[1])
                return article.capitalize() if is_capitalized else article
            # Some articles don't have to be neutralized, just return them.
            else:
                return word_parse[1]

    def neutralize_adjectives(word_parse, has_article) -> str:
        print("neutralize adjective:", word_parse, has_article)
        feats = word_parse[5].split("|")
        # Plural adjectives don't need to be changed.
        # Undeclined adjectives don't need to be changed.
        if feats[3] == "Pl" or (word_parse[1] == word_parse[2] and word_parse[1] != "andere" and not word_parse[1].endswith("er")):
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
        adjective =  adjective + Lexicon.ARTIKEL_JEDER.get(feats[2])
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
                pronoun = Lexicon.PRONOUNS.get(feats[3])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PIS":
            pronoun = word_parse[1]
            if feats[1] == "_":
                feats[1] = "Nom"
            if word_parse[2] == "man":
                pronoun = "mensch"
            elif word_parse[2].endswith("mand"):
                if feats[1] == "Dat" or feats[1] == "Gen":
                    pronoun = word_parse[2] + Lexicon.ARTIKEL_JEDER.get(feats[1])
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
                        pronoun = word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" and word_parse[1].startswith("d"):
            if feats[1] == "_":
                feats[1] = "Nom"
            pronoun = Lexicon.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" or word_parse[4] == "PDS" or word_parse[4] == "PWS":
            if feats[1] == "_":
                feats[1] = "Nom"
            for start in Lexicon.JEDER_PARADIGM:
                if re.match(start + "e.?$", word_parse[2]):
                    pronoun = word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1]) 
                    return pronoun.capitalize() if is_capitalized else pronoun
            pronoun = Lexicon.ARTIKEL_DER.get(feats[1])
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
    # "substantivized adjective" for nouns from Lexicon.SUBST_ADJ or ending in "sprachige"), "person" for "Mann", "Frau",
    # "Herr", "Dame", and capitalized is a Boolean indicating whether the head of the nounphrase is capitalized.
    def check_noun(word_parse,feats,has_article,has_possessive):
        print("check_noun")
        print("word_parse:", word_parse)
        noun = word_parse[2]

        noun_base = noun[0:-1]
        noun_suffix_length = len(word_parse[1]) - word_parse[1].rfind(noun_base) - len(noun)

        if feats[0] == "Masc" or feats[0] == "_":
            for j, line in enumerate(Lexicon.MALE_NOUNS):
                if noun.lower().endswith(line.lower()):
                    prenoun = noun[:-len(line)]
                    if len(prenoun) != 1 and not (prenoun.endswith("c") and line.lower().startswith("h")) and not (len(prenoun) != 0 and (line == "Tor" or line == "Rat" or line == "Ire" or line == "Ahn" or line == "Erbe" or line == "Same" or line == "Ober" or line == "Elfe")) and not (prenoun.endswith("h") and line.lower().startswith("enkel")): # The last case is to avoid false positives with "Henkel" and "Schenkel"
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

        person_pattern = r"((m(a|ä)nn(er)?)|(frau(en)?)|herr|dame)$"
        match = re.search(person_pattern, noun.lower())
        if match:
            match_position = match.start()
            prenoun = noun[:match_position]
            if len(prenoun) != 1:
                prefix, list = Lexicon.check_composite_noun(prenoun,False)
                original = word_parse[1][match_position:]
                capitalized = noun[match_position].isupper()
                list.append([match_position, original, 0, "", "person", capitalized])
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
                
            for j, subadj in enumerate(Lexicon.SUBST_ADJ):
                subadj = "(" + subadj + ")(r|n)?$"
                match = re.search(subadj.lower(), noun.lower())
                if match:
                    match_position = match.start()
                    prenoun = noun[:match_position]
                    if len(prenoun) != 1 and not (prenoun.endswith("c") and noun[match_position:].lower().startswith("h")):
                        prefix, list = Lexicon.check_composite_noun(prenoun,False)
                        original = word_parse[1][match_position:]
                        capitalized = noun[match_position].isupper()
                        list.append([match_position, original, match.group(1).capitalize(), "", "substantivized adjective", capitalized])
                        return True, prefix, list
            
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
        
        # The following case covers lonely adjectives that were artificially capitalized before reparsing:
        if word_parse[1][0].isupper() and word_parse[-2][0].islower():
            if noun.endswith("er") or noun.endswith("en") or noun.endswith("em") or noun.endswith("es"):
                neutral_base = noun[:-1]
            else:
                neutral_base = noun
            return True, "", [[0, noun, neutral_base, "", "substantivized adjective", False]]
        
        if word_parse[4] == "NE" and has_article:
            capitalized = noun[0].isupper()
            return True, "", [[0, noun, noun, "", "proper noun", capitalized]]

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
                    if j-len(line) != 1 and noun[:j].lower().endswith(line.lower()) and noun[j:] != "in" and not (noun[j:].lower().startswith("ch") and line.endswith("s")) and not (noun[:j-len(line)].endswith("c") and line.lower().startswith("h")) and not noun[j:j+8] == "lichkeit" and not noun[j:j+3] == "iat" and not noun[j:j+3] == "ium" and not noun[j:j+3] == "ien" and not (noun[j:j+3] == "ung" and (line.lower().endswith("arzt") or line.lower().endswith("bürger") or line.lower().endswith("partner") or line.lower().endswith("inder") or line.lower().endswith("könig"))) and not (noun[:j-len(line)].endswith("h") and line.lower().startswith("enkel")): # The last case is to avoid false positives with "Henkel" and "Schenkel"
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
                        if match_position != 1 and not (noun[:match_position].endswith("c") and found_neologism.lower().startswith("h")) and not (noun[j:].lower().startswith("ch") and found_neologism.endswith("s")) and not found_neologism.lower() == "base" and not found_neologism.lower() == "opa" and not found_neologism.lower() == "oma":
                            neutral_core = Lexicon.NEOLOGISMS_COMPOUND[i]
                            later_part = noun[j:]
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
    def make_neutralized_noun(pos,selected_components,nounlist,feats,has_article):
        head_selected = False
        person = False
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
                    elif component[-3] == "beamtey":
                        if feats[2] == "Pl":
                            head = "Beamternen" if feats[1] == "Dat" else "Beamterne"
                        else:
                            if feats[1] == "_":
                                feats[1] = "Nom"
                            if has_article:
                                if feats[1] == "Nom" or feats[1] == "Acc": 
                                    head = "Beamte"
                                else:
                                    head = "Beamten"
                            else:
                                head = "Beamt" + Lexicon.ARTIKEL_JEDER.get(feats[1])
                    elif component[-3] == "neutral":
                        head = j
                    elif component[-3] == "substantivized adjective":
                        if j.endswith("e"):
                            head_base = j
                        else:
                            head_base = j + "e"
                        if feats[1] == "_":
                            feats[1] = "Nom"
                        # Weak Flexion, after article
                        if has_article:
                            if feats[1] == "Nom" or feats[1] == "Acc": 
                                head = head_base
                            else:
                                head = head_base + "n"
                        # Strong Flexion, on it's own
                        else:
                            head = head_base[:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1])
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
        return noun, head_selected, person
    
    def __init__(self):
        pass
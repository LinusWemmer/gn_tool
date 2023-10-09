import re


 # This class holds all the necessary information to construct the inclusivum form.
 # It is designed as a "static" class, so no lexicon object should be created, instead functions
 # are called by calling Lexicon.function()
class Lexicon:
    PRONOUNS = {"Nom": "en",
                "Gen": "ens",
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
    
    JEDER_PARADIGM = ["jedwed", "jed", "jen", "dies", "welch", "solch", "manch"]

    EIN_PARADIGM = ["ein", "kein", "mein", "dein", "sein", "ihr", "ens"]

    ROMAN_NOUNS = [r"Alumn(a|us|i)", r"Ballerin(o|a)s?", r"Emerit(a|us|i)", r"Filipin(o|a)s?", r"Gueriller(o|a)s?", r"Latin(o|a)s?", r"Liber(o|a)s?", r"Mafios(o|a)s?", r"Torer(o|a)s?"]
    ROMAN_NOUN_STARTS = ["Alumn", "Ballerin", "Emerit", "Filipin", "Gueriller", "Latin", "Liber", "Mafios", "Torer"]

    IRREGULAR_NOUNS = [r"Prinz(essin)?", r"Hexer?", r"Witwer?", r"Br(a|ä)ut(igam)?", r"Hebamme", r"Amme"]
    IRREGULAR_NOUNS_NEUTRAL = ["Prinze", "Hexere", "Witwere", "Braute", "Hebammere", "Ammere"]

    GRAMM_MAlE_NEUTRAL_NOUNS = ["Gast", "Vormund", "Flüchtling", "Charakter", "Waise", "Geisel", "Profi", "Studi", "Admin"]

    ENGLISH_NOUNS = ["Fan", "Star", "Boss", "Clown", "Punk", "Hippie", "Freak", "Nerd", "Yuppie"]

    NEOLOGISMS = [r"(Bruder)|(Schwester)", r"(Vater)|(Mutter)", r"O(p|m)a", r"(Onkel)|(Tante)", r"Cousine?", r"Tochter|Sohn", r"Jungfrau", r"Mädchen|Jung(e|s)", r"Neffe|Nichte"]  
    NEOLOGISMS_NEUTRAL = ["Geschwister", "Elter", "Ota", "Tonke", "Couse", "Spross", "Jungfere", "Kid", "Nefte"]
    NEOLOGSIMS_PLURAL = ["Geschwister", "Eltern", "Otas", "Tonken", "Cousernen", "Sprosse", "Jungferne", "Kids", "Neften"]

    # The next section generates List of Male/Female role nouns an their corresponding neutral forms
    # from the corresponding text files (also for substanivized adjectives, e.g. "Jugendliche")
    MALE_NOUNS = []
    FEMALE_NOUNS = []
    NEUTRAL_NOUNS = []
    PART_NOUNS = []
    with open("static/movierbare_Substantive.txt") as f_male_nouns:
        for line in f_male_nouns:
            MALE_NOUNS.append(line.rstrip())

    with open("static/movierbare_Substantive_feminin.txt") as f_female_nouns:
        for line in f_female_nouns:
            FEMALE_NOUNS.append(line.rstrip())

    with open("static/movierbare_Substantive_inklusivum.txt") as f_inclusive_nouns:
        for line in f_inclusive_nouns:
            NEUTRAL_NOUNS.append(line.rstrip())

    with open("static/substantivierte_adjektive.txt") as f_sub_adj:
        for line in f_sub_adj:
            PART_NOUNS.append(line.rstrip())

    def neutralize_noun(feats:list, index:int) -> str:
        # Case: Noun is in Singular
        if feats[2] == "Sg":
            noun = Lexicon.NEUTRAL_NOUNS[index]
            if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc" or feats[1] == "_":
                return noun
            elif feats[1] == ("Gen"):
                return noun + "s"
            else:
                raise Exception(f"Somehow the word doesn't have a case: {feats}")
        # Case: Noun is Plural
        elif feats[2] == "Pl":
            noun = Lexicon.NEUTRAL_NOUNS[index]
            if feats[1] == "Nom" or feats[1] == "Acc" or feats[1] == ("Gen") or feats[1] == "_":
                if noun.endswith("re"):
                    return noun[:-2] + "rne"
                else:
                    return noun + "rne"
            if feats[1] ==  "Dat":
                if noun.endswith("re"):
                    return noun[:-2] + "rnen"
                else:
                    return noun + "rnen"
            else:
                raise Exception(f"Somehow the word doesn't have a case: {feats}")
        else:
            #If somehow a word is neither Plural/Singular, we pretend it is singular.
            noun = Lexicon.NEUTRAL_NOUNS[index]
            return noun
            #raise Exception(f"Somehow the word is neither singular nor plural:{feats}")

    # Neutralizes substantivized adjective
    def neutralize_sub_adj(word_parse, article_parse) -> str:
        feats = word_parse[5].split("|")
        # Test for now: If we don't mark singular or plural, be conservative and leave as is, as plural often isn't marked correctly
        if feats[2] != "Sg":
            if not word_parse[1].endswith("er"):
                return word_parse[1]
        article = article_parse[1]
        # If we for some reason don't get a case, pretend it is nominative.
        if feats[1] == "_":
            feats[1] = "Nom"
        # Weak Flexion, after article
        if article_parse[3] == "ART" or article_parse[4] == "APPRART":
            if feats[1] == "Nom" or feats[1] == "Acc": 
                return word_parse[2]
            else:
                return word_parse[2] + "n"
        # Strong Flexion, on it's own
        if word_parse[1].endswith("e"):
            noun =  word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1])
        else:
            noun =  word_parse[1][:-2] + Lexicon.ARTIKEL_JEDER.get(feats[1])
        return noun.capitalize()
    
    def neutralize_beamter(word_parse, article_parse) -> str:
        feats = word_parse[5].split("|")
        # Test for now: If we don't mark singular or plural, be conservative and leave as is, as plural often isn't marked correctly
        if feats[2] == "Pl":
            return "Beamternen" if feats[1] == "Dat" else "Beamterne"
        article = article_parse[1]
        if feats[1] == "_":
            feats[1] = "Nom"
        # Weak Flexion, after article
        if article_parse[3] == "ART" or article_parse[4] == "APPRART":
            if feats[1] == "Nom" or feats[1] == "Acc": 
                return "Beamte"
            else:
                return "Beamten"
        # Strong Flexion, on it's own
        # If we for some reason don't get a case, pretend it is nominative.
        if word_parse[2].endswith("er"):
            noun =  "Beamt" + Lexicon.ARTIKEL_JEDER.get(feats[1])
        else:
            noun =  "Beamt" + Lexicon.ARTIKEL_JEDER.get(feats[1])
        return noun.capitalize()
    
    def neutralize_gendered_suffix(word_parse) -> str:
        feats = word_parse[5].split("|")
        if feats[2] == "Sg" or feats[2] == "_":
            return word_parse[2][:-4] + "person"
        elif feats[2] == "Pl": 
            return word_parse[2][:-4] + "leute"
        
    def neutralize_mann_frau(word_parse) -> str:
        feats = word_parse[5].split("|")
        if feats[2] == "Sg" or feats[2] == "_":
            return "Person"
        elif feats[2] == "Pl": 
            return "Leute"

    # Neutralizes words where a neologism is the neutral form 
    def neutralize_neologism(word_parse) -> str:
        line = 0
        noun = word_parse[2]
        feats = word_parse[5].split("|")
        for index, neologism in enumerate(Lexicon.NEOLOGISMS):
            if re.match(neologism, noun):
                line = index
                break
        if feats[2] == "Pl":
            noun = Lexicon.NEOLOGSIMS_PLURAL[line]
            if line == 0 and feats[1] == "Dat":
                return "Geschwistern"
            else:
                return noun
        else:
            noun = Lexicon.NEOLOGISMS_NEUTRAL[line]
            if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc" or feats[1] == "_":
                return noun
            elif feats[1] == ("Gen"):
                return noun + "s"
        
    def neutralize_possesive_pronoun(word_parse) -> str:
        feats = word_parse[5].split("|")
        pronoun = word_parse[1][0].lower() + word_parse[1][1:] 
        pronoun = pronoun.replace("ihr", "ens")
        pronoun = pronoun.replace("sein", "ens")
        return pronoun.capitalize() if word_parse[0] == "1" else pronoun
    
    def neutralize_attributing_relative_pronoun(word_parse) -> str:
        article = "dersen"
        return article.capitalize() if word_parse[0] == "1" else article
    
    def neutralize_article(word_parse) -> str:
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
            article = "ein" +  Lexicon.ARTIKEL_EIN.get(feats[2])
            return article.capitalize() if is_capitalized else article
        # All other types of article
        else:
            word = word_parse[1][0].lower() + word_parse[1][1:] 
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon.JEDER_PARADIGM:
                if word.startswith(start):
                    #incase no grammatical case is found, treat as nominative, even if wrong.
                    if feats[1] == "_":
                        feats[1] = "Nom"
                    article = start + Lexicon.ARTIKEL_JEDER.get(feats[1])
                    return article.capitalize() if is_capitalized else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon.EIN_PARADIGM:
                if word.startswith(start):
                    if feats[1] == "_":
                        feats[1] = "Nom"
                    article = start + Lexicon.ARTIKEL_EIN.get(feats[1])
                    return article.capitalize() if is_capitalized else article
            if re.match(r"(U|u)(nser|nsre|nsere)", word):
                article = Lexicon.ARTIKEL_UNSER.get(feats[1])
                return article.capitalize() if is_capitalized else article
            elif re.match(r"(E|e)(uer|ure)", word):
                article = Lexicon.ARTIKEL_EUER.get(feats[1])
                return article.capitalize() if is_capitalized else article
            # Some articles don't have to be neutralized, just return them.
            else:
                return word_parse[1]

    def neutralize_adjectives(word_parse, article_parse) -> str:
        feats = word_parse[5].split("|")
        article = article_parse[1]
        # This is a weird hack to make sure "anders" works correctly
        if word_parse[2].startswith("ander"):
            word_parse[2] = "ander"
        # Differentiate Superlative/Comparative/Normal adjectives
        adjective = ""
        if "Sup" in word_parse[5]:
            match = re.search(r".+st", word_parse[1])
            adjective = match.group(0)
        elif "Comp" in word_parse[5]:
            match1 = re.search(r".+er", word_parse[1])
            adjective = match1.group(0)
        else:
            adjective = word_parse[2]
        # Weak Flexion, after article der/die/das (de), also "Jeder"-list
        if article_parse[3] == "ART" or article_parse[4] == "APPRART":
            if feats[3] == "Pl":
                return word_parse[1]
            else:
                # Differentiate case
                if feats[2] == "Acc" or feats[2] == "Nom":
                    adjective = adjective + "e"
                    return adjective.capitalize() if word_parse[0] == "1" else adjective
                else:
                    adjective = adjective + "en"
                    return adjective.capitalize() if word_parse[0] == "1" else adjective
                return word_parse[1]
        # Strong Flexion, on it's own
        # If we for some reason don't get a case, pretend it is nominative.
        if feats[2] == "_":
            feats[2] = "Nom"
        adjective =  adjective + Lexicon.ARTIKEL_JEDER.get(feats[2])
        return adjective.capitalize() if word_parse[0] == "1" else adjective
    
    # Neutralize possesive jemand, this often doesn't get parsed correctly
    def neutralize_pos_jemand(word_parse) -> str:
        word = "jemanders"
        return word.capitalize() if word_parse[0] == "1" else word
    
    # Neutralize Prepostions if they are compound articles with prepositions, e.g. zur/im/beim
    def neutralize_preposition(word_parse) -> str:
        feats = word_parse[5]
        # The different shortforms have to be hardcoded, boring
        if word_parse[1]== "beim" or word_parse[1]== "Beim":
            preposition = "bei derm"
            return preposition.capitalize() if word_parse[0] == "1" else preposition
        if word_parse[1]== "am" or word_parse[1]=="Am":
            preposition = "an derm"
            return preposition.capitalize() if word_parse[0] == "1" else preposition
        if word_parse[1]== "zum" or word_parse[1]=="zur" or word_parse[1]=="Zum" or word_parse[1]=="Zur":
            preposition = "zurm"
            return preposition.capitalize() if word_parse[0] == "1" else preposition
        if word_parse[1]=="im" or word_parse[1]=="Im":
            preposition = "in derm"
            return preposition.capitalize() if word_parse[0] == "1" else preposition
        if word_parse[1] == "vom" or word_parse[1] == "Vom":
            preposition = "von derm"
            return preposition.capitalize() if word_parse[0] == "1" else preposition
        return word_parse[1]
    
    def neutralize_pronoun(word_parse) -> str:
        feats = word_parse[5].split("|")
        is_capitalized = word_parse[1][0].isupper()
        if feats[0] == "Neut":
            return word_parse[1]
        if word_parse[4] == "PPER":
            pronoun = word_parse[1]
            if feats[0] == "3":
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
                if word_parse[2].endswith("er"):
                    word_parse[2] = word_parse[2][:-1]
                pronoun = word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS":
            if feats[1] == "_":
                feats[1] = "Nom"
            pronoun = Lexicon.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PDS":
            for start in Lexicon.JEDER_PARADIGM:
                if word_parse[1].startswith(start):
                    pronoun = word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1]) 
                    return pronoun.capitalize() if is_capitalized else pronoun
            pronoun = Lexicon.ARTIKEL_DER.get(feats[1])
            if word_parse[2].endswith("jenige"):
                pronoun += "jenige"
            return pronoun.capitalize() if is_capitalized else pronoun

    def neutralize_word(word_parse) -> str:
        # For Plural Cases, I think this doesn't have to be changed. Check with testing.
        if "Pl" in word_parse[5]:
            return word_parse[1]
        # neutralize Articles
        elif word_parse[3] == "ART":
            return Lexicon.neutralize_article(word_parse)
        # neutralize Pronouns
        elif word_parse[3] == "PRO":
            return Lexicon.neutralize_pronoun(word_parse)
        elif word_parse[3] == "PREP" and word_parse[4] == "APPRART":
            return Lexicon.neutralize_preposition(word_parse)
        else:
            return word_parse[1]

    # Neutralize nouns that are romanisms
    def neutralize_romanism(word_parse) -> str:
        line = 0
        noun = word_parse[1]
        feats = word_parse[5].split("|")
        for index, start in enumerate(Lexicon.ROMAN_NOUN_STARTS):
            if noun.startswith(start):
                line = index
        noun = Lexicon.ROMAN_NOUN_STARTS[line] + "e"
        if not len(feats)<=1:
            if feats[2] == "Pl":
                if feats[1] == "Nom" or feats[1] == "Acc" or feats[1] == ("Gen") or feats[1] == "_":
                    return noun + "rne"
                if feats[1] ==  "Dat":
                    return noun + "rnen"
            else:
                if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc" or feats[1] == "_":
                    return noun
                elif feats[1] == ("Gen"):
                    return noun + "s"
                else:
                    raise Exception(f"Somehow the word doesn't have a case: {feats}")
        return noun
    
    def neutralize_irregular_noun(word_parse) -> str:
        line = 0
        noun = word_parse[1]
        feats = word_parse[5].split("|")
        for index, irregular_noun in enumerate(Lexicon.IRREGULAR_NOUNS):
            if re.match(irregular_noun, noun):
                line = index
        noun = Lexicon.IRREGULAR_NOUNS_NEUTRAL[line]
        if feats[2] == "Pl":
            if noun.endswith("ere"):
                noun = noun[:-2]
            if feats[1] == "Nom" or feats[1] == "Acc" or feats[1] == ("Gen") or feats[1] == "_":
                return noun + "rne"
            if feats[1] ==  "Dat":
                return noun + "rnen"
        else:
            if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc" or feats[1] == "_":
                return noun
            elif feats[1] == ("Gen"):
                return noun + "s"

    # This function checks if a certain noun is a role noun (refers to a person) that can be gendered
    # Returns line number in the list of role nouns if this is the case,
    # -1 if it is a substantivised adjective,
    # otherwise false
    def check_role_noun(word_parse):
        noun = word_parse[2]
        if "-" in word_parse[2]:
            word_split = word_parse[2].split("-")
            noun = word_split[-1]
        gender = word_parse[5][0]
        length = 4116
        i = 0
        # Checks the List of role Nouns to check if word is a role noun
        if gender == "M":
            for i, line in enumerate(Lexicon.MALE_NOUNS):
                if line == noun:
                    return i
                elif i >= length:
                    break
        elif gender == "F":
            for i, line in enumerate(Lexicon.FEMALE_NOUNS):
                if line == noun:
                    return i
                elif i >= length:
                    break
        else:    
            for i, line in enumerate(Lexicon.MALE_NOUNS):
                if line == noun:
                    return i
                elif i >= length:
                    i = 0
                    break
            for i, line in enumerate(Lexicon.FEMALE_NOUNS):
                if line == noun:
                    return i
                elif i >= length:
                    break
        # Neologisms:
        for neologism in Lexicon.NEOLOGISMS:
            if re.match(neologism, noun):
                return "-3"
        # Words ending on -mann or -frau:
        if re.match(r".+m(a|ä)nn(er)?", noun) or re.match(r".+frau", noun):
            return -2
        # The Word "Mann", "Frau", "Herr", "Dame":
        if noun == "Mann" or noun =="Frau" or noun == "Herr" or noun == "Dame":
            return -4
        #Romanisms:
        for romanism in Lexicon.ROMAN_NOUNS:
            if re.match(romanism, noun):
                return "-10"
        # Irregular role Nouns:
        for irregular_noun in Lexicon.IRREGULAR_NOUNS:
            if re.match(irregular_noun, noun):
                return "-11"
        # Noun is already neutral, but article should be declinated
        if noun in Lexicon.ENGLISH_NOUNS or noun in Lexicon.GRAMM_MAlE_NEUTRAL_NOUNS:
            return -12
        # Check substantivized adjectives
        if word_parse[5][-2:] == "Pl":
            return False
        for i, line in enumerate(Lexicon.PART_NOUNS):
            subadj = line
            if noun == subadj or noun == subadj + "r" or noun == subadj + "n":
                return -1
        if re.match(r".*sprachige", noun):
            return -1    
        return False
    
    def __init__(self):
        pass
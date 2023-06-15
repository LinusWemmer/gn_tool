import re

class Lexicon:
    # This class holds all the necessary information to construct the inclusivum
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
    
    MALE_NOUNS = open("movierbare_Substantive.txt", "r")

    FEMALE_NOUNS = open("movierbare_Substantive_feminin.txt", "r")

    NEUTRAL_NOUNS = open("movierbare_Substantive_inklusivum.txt", "r")

    PART_NOUNS = open("substantivierte_adjektive.txt", "r")

    def neutralize_noun(feats:list, index:int) -> str:
        if index == -1:
            pass
        # Case: Noun is in Singular
        if feats[2] == "Sg":
            noun = ""
            for i, line in enumerate(Lexicon.NEUTRAL_NOUNS):
                if i == index:
                    noun = line[:-1]
                    Lexicon.NEUTRAL_NOUNS.seek(0)
                    break
                elif i > index:
                    Lexicon.NEUTRAL_NOUNS.seek(0)
                    break
            if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc" :
                return noun
            elif feats[1] == ("Gen"):
                return noun + "s"
            else:
                raise Exception(f"Somehow the word doesn't have a case: {feats}")
        # Case: Noun is Plural
        elif feats[2] == "Pl":
            noun = ""
            for i, line in enumerate(Lexicon.NEUTRAL_NOUNS):
                if i == index:
                    noun = line[:-1]
                    Lexicon.NEUTRAL_NOUNS.seek(0)
                    break
                elif i > index:
                    Lexicon.NEUTRAL_NOUNS.seek(0)
                    break
            if feats[1] == "Nom" or feats[1] == "Acc" or feats[1] == ("Gen"):
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
            noun = ""
            for i, line in enumerate(Lexicon.NEUTRAL_NOUNS):
                if i == index:
                    noun = line[:-1]
                    Lexicon.NEUTRAL_NOUNS.seek(0)
                    break
                elif i > index:
                    Lexicon.NEUTRAL_NOUNS.seek(0)
                    break
            return noun
            #raise Exception(f"Somehow the word is neither singular nor plural:{feats}")

    def neutralize_sub_adj(word_parse, article_parse) -> str:
        feats = word_parse[5].split("|")
        article = article_parse[1]
        if feats[1] == "_":
            feats[1] = "Nom"
        # Weak Flexion, after article
        if article_parse[3] == "ART" or article_parse[4] == "APPRART":
            if feats[1] == "Nom" or feats[1] == "Acc": 
                return word_parse[2]
            else:
                return word_parse[2] + "n"
        # Strong Flexion, on it's own
        # If we for some reason don't get a case, pretend it is nominative.
        noun =  word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1])
        return noun.capitalize()
        
    def neutralize_possesive_pronoun(word_parse) -> str:
        feats = word_parse[5].split("|")
        pronoun = ""
        if feats[2] == "Pl":
            if feats[1] == "Acc":
                pronoun = "ense"
            if feats[1] == "Nom":
                pronoun = "ense" 
            if feats[1] == "Dat":
                pronoun = "ensen"
            if feats[1] == "Gen":
                pronoun = "enser"
        else:
            if feats[1] == "Acc":
                if feats[0] == "Fem":
                    pronoun = "ense"
                elif feats[0] == "Masc":
                    pronoun = "ensen"
                else:
                    pronoun = "ens"
            if feats[1] == "Nom":
                pronoun = "ense" if feats[0] == "Fem" else "ens"
            if feats[1] == "Dat":
                pronoun = "enser" if feats[0] == "Fem" else "ensem"
            if feats[1] == "Gen":
                pronoun = "enser" if feats[0] == "Fem" else "ensem"
        return pronoun.capitalize() if word_parse[0] == "1" else pronoun
    
    def neutralize_article(word_parse) -> str:
        feats = word_parse[5].split("|")
        # Case Definitive Articles
        if feats[0] == "Def":
            if feats[2] == "_":
                feats[2] = "Nom"
            article =  Lexicon.ARTIKEL_DER.get(feats[2])
            return article.capitalize() if word_parse[0] == "1" else article
        # Case Indifinitive Artikels, only ein
        elif feats[0] == "Indef":
            article = "ein" +  Lexicon.ARTIKEL_EIN.get(feats[2])
            return article.capitalize() if word_parse[0] == "1" else article
        # Attributing relative pronouns
        elif word_parse[4] == "PRELAT":
            article = "dersen"
            return article.capitalize() if word_parse[0] == "1" else article
        else:
            word = word_parse[1][0].lower() + word_parse[1][1:] 
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon.JEDER_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon.ARTIKEL_JEDER.get(feats[1])
                    return article.capitalize() if word_parse[0] == "1" else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon.EIN_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon.ARTIKEL_EIN.get(feats[1])
                    return article.capitalize() if word_parse[0] == "1" else article
            if re.match(r"(U|u)(nser|nsre|nsere)", word):
                article = Lexicon.ARTIKEL_UNSER.get(feats[1])
                return article.capitalize() if word_parse[0] == "1" else article
            elif re.match(r"(E|e)(uer|ure)", word):
                article = Lexicon.ARTIKEL_EUER.get(feats[1])
                return article.capitalize() if word_parse[0] == "1" else article
            # Some articles don't have to be neutralized, just return them.
            else:
                return word_parse[1]
            raise Exception(f"The Article seems to be not convertable:{word_parse[1]}")

    def neutralize_adjectives(word_parse, article_parse) -> str:
        feats = word_parse[5].split("|")
        article = article_parse[1]
        # This is a weird hack to make sure "anders" works correctly
        if word_parse[2].startswith("ander"):
            word_parse[2] = "ander"
        # Weak Flexion, after article der/die/das (de), also "Jeder"-list
        if article_parse[3] == "ART" or article_parse[4] == "APPRART":
            if feats[2] == "Acc" or feats[2] == "Nom":
                adjective = word_parse[2] + "e"
                return adjective.capitalize() if word_parse[0] == "1" else adjective
            else:
                adjective = word_parse[2] + "en"
                return adjective.capitalize() if word_parse[0] == "1" else adjective
            return word_parse[1]
        # Strong Flexion, on it's own
        # If we for some reason don't get a case, pretend it is nominative.
        if feats[2] == "_":
            feats[2] = "Nom"
        adjective =  word_parse[2] + Lexicon.ARTIKEL_JEDER.get(feats[2])
        return adjective.capitalize() if word_parse[0] == "1" else adjective
    
    # Neutralize Prepostions if they are compound articles with prepositions, e.g. zur/im/beim
    def neutralize_preposition(word_parse) -> str:
        feats = word_parse[5]
        # The different shortforms have to be hardcoded, boring
        if word_parse[1]=="beim" or word_parse[1]== "Beim":
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
        if feats[0] == "Neut":
            return word_parse[1]
        if word_parse[4] == "PPER":
            pronoun = word_parse[1]
            if feats[0] == "3":
                pronoun = Lexicon.PRONOUNS.get(feats[3])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun
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
                pronoun = word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun
        elif word_parse[4] == "PRELS":
            pronoun = Lexicon.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun
        elif word_parse[4] == "PDS":
            for start in Lexicon.JEDER_PARADIGM:
                if word_parse[1].startswith(start):
                    pronoun = word_parse[2][:-1] + Lexicon.ARTIKEL_JEDER.get(feats[1]) 
                    return pronoun.capitalize() if word_parse[0] == "1" else pronoun
            pronoun = Lexicon.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun

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
        Lexicon.PART_NOUNS.seek(0)
        Lexicon.MALE_NOUNS.seek(0)
        Lexicon.FEMALE_NOUNS.seek(0)
        length = 800
        i = 0
        if gender == "M":
            for i, line in enumerate(Lexicon.MALE_NOUNS):
                if line[:-1] == noun:
                    Lexicon.MALE_NOUNS.seek(0)
                    return i
                elif i >= length:
                    Lexicon.MALE_NOUNS.seek(0)
                    break
        if gender == "F":
            for i, line in enumerate(Lexicon.FEMALE_NOUNS):
                if line[:-1] == noun:
                    Lexicon.FEMALE_NOUNS.seek(0)
                    return i
                elif i >= length:
                    Lexicon.FEMALE_NOUNS.seek(0)
                    break   
        else:
            # Plural cases can be disregarded, as these are already neutral.
            if word_parse[5][-2:] == "Pl":
                return False
            for i, line in enumerate(Lexicon.PART_NOUNS):
                if noun.startswith(line[:-1]):
                    Lexicon.PART_NOUNS.seek(0)
                    return -1
            if re.match(r".*sprachige", noun):
                Lexicon.PART_NOUNS.seek(0)
                return -1    
            Lexicon.PART_NOUNS.seek(0)
        return False
    
    def __init__(self):
        pass
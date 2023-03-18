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
    
    # ein einers einerm ein
    ARTIKEL_EIN = {"Nom": "",
                "Gen": "ers",
                "Dat": "erm",
                "Acc": ""}
    
    # jedey jeders jederm jedey
    ARTIKEL_JEDER = {"Nom": "ey",
                "Gen": "ers",
                "Dat": "erm",
                "Ac": "ey"} 
    
    JEDER_PARADIGM = ["jedwed", "jed", "jen", "dies", "welch", "solch", "manch"]

    EIN_PARADIGM = ["ein", "kein", "mein", "dein", "sein", "ihr", "ens"]
    
    MALE_NOUNS = open("movierbare_Substantive.txt", "r")

    FEMALE_NOUNS = open("movierbare_Substantive_feminin.txt", "r")

    NEUTRAL_NOUNS = open("movierbare_Substantive_inklusivum.txt", "r")

    def neutralize_noun(feats:list, index:int) -> str:
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
            if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc":
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
            raise Exception(f"Somehow the word is neither singular nor plural:{feats}")

    # TODO: probaply the different cases should be put into their own methods for readability.
    def neutralize_word(parse_list) -> str:
        # For Plural Cases, I think this doesn't have to be changed. Check with testing.
        if parse_list[5].endswith("Pl"):
            return parse_list[1]
        # neutralize Adjectives
        if parse_list[3] == "ADJA":
            return parse_list[1]
        # neutralize Articles
        elif parse_list[3] == "ART":
            feats = parse_list[5].split("|")
            # Case Definitive Articles
            if feats[0] == "Def":
                article =  Lexicon.ARTIKEL_DER.get(feats[2])
                return article.capitalize() if parse_list[0] == "1" else article
            # Case Indifinitive Artikels, only ein
            elif feats[0] == "Indef":
                article = "ein" +  Lexicon.ARTIKEL_EIN.get(feats[2])
                return article.capitalize() if parse_list[0] == "1" else article
            # Case Jeder Paradigm
            else:
                #case = Lexicon.getCase(parse_list)
                word = parse_list[1][0].lower() + parse_list[1][1:] 
                for start in Lexicon.JEDER_PARADIGM:
                    if word.startswith(start):
                        article = start + Lexicon.ARTIKEL_JEDER.get(feats[1])
                        return article.capitalize() if parse_list[0] == "1" else article
                for start in Lexicon.EIN_PARADIGM:
                    if word.startswith(start):
                        article = start + Lexicon.ARTIKEL_EIN.get(feats[1])
                        return article.capitalize() if parse_list[0] == "1" else article
                raise Exception(f"The Article seems to be not convertable:{parse_list[1]}")
        # neutralize Pronouns
        elif parse_list[3] == "PRO":
            feats = parse_list[5].split("|")
            pronoun = Lexicon.PRONOUNS.get(feats[3])
            return pronoun.capitalize() if parse_list[0] == "1" else pronoun

    def check_role_noun(noun:str, gender:str) -> bool:
        length = 800
        i = 0
        if gender == "M":
            for i, line in enumerate(Lexicon.MALE_NOUNS):
                if line[:-1] == noun:
                    Lexicon.MALE_NOUNS.seek(0)
                    return i
                elif i > length:
                    Lexicon.MALE_NOUNS.seek(0)
                    return False
        if gender == "F":
            for i, line in enumerate(Lexicon.FEMALE_NOUNS):
                if line[:-1] == noun:
                    Lexicon.FEMALE_NOUNS.seek(0)
                    return i
                elif i > length:
                    Lexicon.FEMALE_NOUNS.seek(0)
                    return False    
        return False
    
    def __init__(self):
        pass
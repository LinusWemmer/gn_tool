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
    
    ARTIKEL_EIN = {"Nom": "ein",
                "Gen": "einers",
                "Dat": "einerm",
                "Acc": "ein"}
    ARTIKEL_JEDER = {"Nom": "ey",
                "Gen": "ers",
                "Dat": "erm",
                "Ac": "ey"} # jedey jeders jederm jedey
    
    JEDER_PARADIGM = ["jedwed", "jed", "jen", "dies", "welch", "solch", "manch"]
    
    MALE_NOUNS = open("movierbare_Substantive.txt", "r")

    FEMALE_NOUNS = open("movierbare_Substantive_feminin.txt", "r")

    NEUTRAL_NOUNS = open("movierbare_Substantive_inklusivum.txt", "r")

    def neutralize_noun(feats:list, index:int) -> str:
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
                #something went wrong
                pass
        elif feats[3] == "Pl":
            pass
        else:
            #something went wrong
            pass

    def neutralize_word(parse_list) -> str:
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
            # Case Indifinitive Artikels
            elif feats[0] == "Indef":
                article = ""
                if parse_list[1][0] == "e" or parse_list[1][0] == "E":
                    article = Lexicon.ARTIKEL_EIN.get(feats[2])
                else:
                    article = parse_list[1][0] + Lexicon.ARTIKEL_EIN.get(feats[2])
                return article.capitalize() if parse_list[0] == "1" else article
            # Case Jeder Paradigm
            else: 
                for start in Lexicon.JEDER_PARADIGM:
                    if parse_list[1].startswith(start):
                        article = start + Lexicon.ARTIKEL_JEDER.get(feats[1])
                        return article.capitalize() if parse_list[0] == "1" else article
        # neutralize Pronouns
        elif parse_list[3] == "PRO":
            feats = parse_list[5].split("|")
            pronoun = Lexicon.PRONOUNS.get(feats[3])
            return pronoun.capitalize() if parse_list[0] == "1" else pronoun


    # A faster algorithm would probably give a List of nouns to check,
    # and return a list of nouns that are personal designations.
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
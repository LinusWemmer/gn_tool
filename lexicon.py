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

    def neutralize_noun(noun_root:str, feats:list) -> str:
        if feats[2] == "Sg":
            print(feats[1])
            if feats[1] == "Nom" or feats[1] ==  "Dat" or feats[1] == "Acc":
                return noun_root + "re" if noun_root[-1] == "e" else noun_root + "e"
            elif feats[1] == ("Gen"):
                return noun_root + "es"
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
            lines = Lexicon.MALE_NOUNS.readlines()
            for line in lines:
                if i > 800:
                    return False
                if line[:-1] == noun:
                    Lexicon.MALE_NOUNS.seek(0)
                    return True
                i +=1
            Lexicon.MALE_NOUNS.seek(0)
        if gender == "F":
            lines = Lexicon.FEMALE_NOUNS.readlines()
            for line in lines:
                if i > 800:
                    return False
                if line[:-1] == noun:
                    Lexicon.FEMALE_NOUNS.seek(0)
                    return True
                i +=1
            Lexicon.FEMALE_NOUNS.seek(0)    
        return False
    
    def __init__(self):
        pass

#print(Lexicon.check_role_noun("Schüler", "M"))
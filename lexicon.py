class Lexicon:
    # This class holds all the necessary information to construct the inclusivum
    PRONOUNS = {"NOM": "en",
                "POS": "ens",
                "DAT": "em",
                "ACC": "en"}
    
    ARTIKEL_DER = {"NOM": "de",
                "POS": "ders",
                "DAT": "derm",
                "ACC": "de"}
    ARTIKEL_EIN = {"NOM": "ein",
                "POS": "einers",
                "DAT": "einerm",
                "ACC": "ein"}
    ARTIKEL_JEDER = {"NOM": "jedey",
                "POS": "jeders",
                "DAT": "jederm",
                "ACC": "jedey"}
    
    MALE_NOUNS = open("movierbare_Substantive.txt", "r")

    FEMALE_NOUNS = open("movierbare_Substantive_feminin.txt", "r")

    NEUTRAL_NOUNS = open("movierbare_Substantive_inklusivum.txt", "r")

    def neutralize_noun(noun_root:str, feats:list) -> str:
        if feats[2] == "Sg":
            if feats[1] == ("Nom" or "Dat" or "Acc"):
                return noun_root + "e"
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


    # A faster algorithm would probably give a List of nouns to check,
    # and return a list of nouns that are personal designations.
    def check_role_noun(noun:str, gender:str) -> bool:
        length = 800
        if gender == "M":
            lines = Lexicon.MALE_NOUNS.readlines(length)
            for line in lines:
                if line[:-1] == noun:
                    Lexicon.MALE_NOUNS.seek(0)
                    return True
            Lexicon.MALE_NOUNS.seek(0)
        if gender == "F":
            lines = Lexicon.FEMALE_NOUNS.readlines(length)
            for line in lines:
                if line[:-1] == noun:
                    Lexicon.FEMALE_NOUNS.seek(0)
                    return True
            Lexicon.FEMALE_NOUNS.seek(0)    
        return False
    
    def __init__(self):
        pass

#print(Lexicon.check_role_noun("Schüler", "M"))
class Lexicon:
    # This class holds all the necessary information to construct the inclusivum
    PRONOUNS = {"NOM": "en",
                "POS": "ens",
                "DAT": "em",
                "AKK": "en"}
    
    ARTIKEL_DER = {"NOM": "de",
                "POS": "ders",
                "DAT": "derm",
                "AKK": "de"}
    ARTIKEL_EIN = {"NOM": "ein",
                "POS": "einers",
                "DAT": "einerm",
                "AKK": "ein"}
    ARTIKEL_JEDER = {"NOM": "jedey",
                "POS": "jeders",
                "DAT": "jederm",
                "AKK": "jedey"}
    
    MALE_NOUNS = open("movierbare_Substantive.txt", "r")

    FEMALE_NOUNS = open("movierbare_Substantive_feminin.txt", "r")

    NEUTRAL_NOUNS = open("movierbare_Substantive_inklusivum.txt", "r")


    # A faster algorithm would probably give a List of nouns to check,
    # and return a list of nouns that are personal designations.
    def check_role_noun(noun:str, gender:str) -> bool:
        length = 800
        if gender == "m":
            lines = Lexicon.MALE_NOUNS.readlines(length)
            for line in lines:
                if line[:-1] == noun:
                    return True
        if gender == "f":
            lines = Lexicon.FEMALE_NOUNS.readlines(length)
            for line in lines:
                if line[:-1] == noun:
                    return True    
        return False
    
    def __init__(self):
        pass

print(Lexicon.check_role_noun("Autorin", "f"))
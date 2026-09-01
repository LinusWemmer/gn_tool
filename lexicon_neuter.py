import re

class Lexicon_Neuter:
    # This class holds all the necessary information to construct the neuter (for words that modify "Kind")
    PRONOUNS = {"Nom": "es",
                "Gen": "seines",
                "Dat": "ihm",
                "Acc": "es"}
    
    ARTIKEL_DER = {"Nom": "das",
                "Gen": "des",
                "Dat": "dem",
                "Acc": "das"}
    
    ARTIKEL_UNSER = {"Nom": "unser",
                "Gen": "unseres",
                "Dat": "unserem",
                "Acc": "unser"}
    
    ARTIKEL_EUER = {"Nom": "euer",
                "Gen": "eures",
                "Dat": "eurem",
                "Acc": "euer"}
    
    # ein eines einem ein
    ARTIKEL_EIN = {"Nom": "",
                "Gen": "es",
                "Dat": "em",
                "Acc": ""}
    
    # jedey jedes jedem jedey
    ARTIKEL_JEDER = {"Nom": "es",
                "Gen": "es",
                "Dat": "em",
                "Acc": "es"}
    
    JEDER_PARADIGM = ["jedwed", "jed", "jen", "dies", "welch", "solch", "manch"]

    EIN_PARADIGM = ["ein", "kein", "mein", "dein", "sein", "ihr", "ens"]

    def neuterize_possesive_pronoun(word_parse) -> str:
        feats = word_parse[5].split("|")
        pronoun = ""
        if feats[1] == "Acc":
            if feats[0] == "Neut":
                pronoun = "ens"
            elif feats[0] == "Masc":
                pronoun = "ensen"
            else:
                pronoun = "ense"
        if feats[1] == "Nom":
            pronoun = "ens" if feats[0] == "Neut" else "ense"
        if feats[1] == "Dat":
            pronoun = "ensem" if feats[0] == "Neut" else "enser"
        if feats[1] == "Gen":
            pronoun = "ensem" if feats[0] == "Neut" else "enser"
        return pronoun.capitalize() if word_parse[1][0].isupper() else pronoun
    
    def neuterize_attributing_relative_pronoun(word_parse) -> str:
        article = "dessen"
        return article.capitalize() if word_parse[1][0].isupper() else article
    
    def neuterize_article(word_parse) -> str:
        feats = word_parse[5].split("|")
        # Case Definitive Articles
        if feats[0] == "Def":
            if feats[2] == "_":
                feats[2] = "Nom"
            article = Lexicon_Neuter.ARTIKEL_DER.get(feats[2])
            return article.capitalize() if word_parse[1][0].isupper() else article
        # Case Indefinitive Articles, only ein
        elif feats[0] == "Indef":
            article = "ein" + Lexicon_Neuter.ARTIKEL_EIN.get(feats[2])
            return article.capitalize() if word_parse[1][0].isupper() else article
        else:
            word = word_parse[1][0].lower() + word_parse[1][1:] 
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon_Neuter.JEDER_PARADIGM:
                if word.startswith(start):
                    #incase no grammatical case is found, treat as nominative, even if wrong.
                    if feats[1] == "_":
                        feats[1] = "Nom"
                    article = start + Lexicon_Neuter.ARTIKEL_JEDER.get(feats[1])
                    return article.capitalize() if word_parse[1][0].isupper() else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon_Neuter.EIN_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon_Neuter.ARTIKEL_EIN.get(feats[1])
                    return article.capitalize() if word_parse[1][0].isupper() else article
            if re.match(r"(U|u)(nser|nsre|nsere)", word):
                article = Lexicon_Neuter.ARTIKEL_UNSER.get(feats[1])
                return article.capitalize() if word_parse[1][0].isupper() else article
            elif re.match(r"(E|e)(uer|ure)", word):
                article = Lexicon_Neuter.ARTIKEL_EUER.get(feats[1])
                return article.capitalize() if word_parse[1][0].isupper() else article
            # Some articles don't have to be neuterized, just return them.
            else:
                return word_parse[1]
            raise Exception(f"The Article seems to be not convertable:{word_parse[1]}")

    def neuterize_adjectives(word_parse, has_article) -> str:
        feats = word_parse[5].split("|")
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
        if has_article:
            if feats[3] == "Pl":
                return word_parse[1]
            else:
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
        adjective =  adjective + Lexicon_Neuter.ARTIKEL_JEDER.get(feats[2])
        return adjective.capitalize() if word_parse[1][0].isupper() else adjective
    
    # Neutralize possesive jemand, this often doesn't get parsed correctly
    def neuterize_pos_jemand(word_parse) -> str:
        word = "jemanders"
        return word.capitalize() if word_parse[1][0].isupper() else word
    
    def neuterize_pronoun(word_parse,has_article) -> str:
        feats = word_parse[5].split("|")
        is_capitalized = word_parse[1][0].isupper()
        if feats[0] == "Neut":
            return word_parse[1]
        if word_parse[4] == "PPER":
            if feats[3] == "_":
                feats[3] = "Nom"
            pronoun = word_parse[1]
            if feats[0] == "3":
                pronoun = Lexicon_Neuter.PRONOUNS.get(feats[3])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PIS":
            pronoun = word_parse[1]
            if feats[1] == "_":
                feats[1] = "Nom"
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
                        adjective = adjective + "n"
                        return pronoun.capitalize() if is_capitalized else pronoun
                else:
                    pronoun = word_parse[2][:-1] + Lexicon_Neuter.ARTIKEL_JEDER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" and word_parse[1].startswith("d"):
            if feats[1] == "_":
                feats[1] = "Nom"
            pronoun = Lexicon_Neuter.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" or word_parse[4] == "PDS":
            if feats[1] == "_":
                feats[1] = "Nom"
            for start in Lexicon_Neuter.JEDER_PARADIGM:
                if re.match(start + "e.?$", word_parse[2]):
                    pronoun = word_parse[2][:-1] + Lexicon_Neuter.ARTIKEL_JEDER.get(feats[1]) 
                    return pronoun.capitalize() if is_capitalized else pronoun
            pronoun = Lexicon_Neuter.ARTIKEL_DER.get(feats[1])
            if re.match(r"d..jenige$", word_parse[2]):
                pronoun += "jenige"
                if feats[1] == "Gen" or feats[1] == "Dat":
                    pronoun += "n"
            if re.match(r"d..selbe$", word_parse[2]):
                pronoun += "selbe"
                if feats[1] == "Gen" or feats[1] == "Dat":
                    pronoun += "n"
            return pronoun.capitalize() if is_capitalized else pronoun

    def neuterize_word(word_parse,has_article) -> str:
        # For Plural Cases, it doesn't have to be changed. 
        if "Pl" in word_parse[5]:
            return word_parse[1]
        # neuterize Articles
        elif word_parse[3] == "ART":
            return Lexicon_Neuter.neuterize_article(word_parse)
        # neuterize Pronouns
        elif word_parse[3] == "PRO":
            return Lexicon_Neuter.neuterize_pronoun(word_parse,has_article)
        else:
            return word_parse[-2]
    
    def __init__(self):
        pass
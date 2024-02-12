import re

class Lexicon_Fem:
    # This class holds all the necessary information to construct the inclusivum
    PRONOUNS = {"Nom": "sie",
                "Gen": "ihr",
                "Dat": "ihr",
                "Acc": "sie"}
    
    ARTIKEL_DER = {"Nom": "die",
                "Gen": "der",
                "Dat": "der",
                "Acc": "die"}
    
    ARTIKEL_UNSER = {"Nom": "unsere",
                "Gen": "unserer",
                "Dat": "unserer",
                "Acc": "unsere"}
    
    ARTIKEL_EUER = {"Nom": "eure",
                "Gen": "eurer",
                "Dat": "eurer",
                "Acc": "eure"}
    
    # ein einers einerm ein
    ARTIKEL_EIN = {"Nom": "e",
                "Gen": "er",
                "Dat": "er",
                "Acc": "e"}
    
    # jedey jeders jederm jedey
    ARTIKEL_JEDER = {"Nom": "e",
                "Gen": "er",
                "Dat": "er",
                "Acc": "e"} 
    
    JEDER_PARADIGM = ["jedwed", "jed", "jen", "dies", "welch", "solch", "manch"]

    EIN_PARADIGM = ["ein", "kein", "mein", "dein", "sein", "ihr", "ens"]
    
        
    def feminize_possesive_pronoun(word_parse) -> str:
        feats = word_parse[5].split("|")
        pronoun = ""
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
        return pronoun.capitalize() if word_parse[1][0].isupper() else pronoun
    
    def feminize_attributing_relative_pronoun(word_parse) -> str:
        article = "deren"
        return article.capitalize() if word_parse[1][0].isupper() else article
    
    def feminize_article(word_parse) -> str:
        feats = word_parse[5].split("|")
        # Case Definitive Articles
        if feats[0] == "Def":
            if feats[2] == "_":
                feats[2] = "Nom"
            article =  Lexicon_Fem.ARTIKEL_DER.get(feats[2])
            return article.capitalize() if word_parse[1][0].isupper() else article
        # Case Indifinitive Artikels, only ein
        elif feats[0] == "Indef":
            article = "ein" +  Lexicon_Fem.ARTIKEL_EIN.get(feats[2])
            return article.capitalize() if word_parse[1][0].isupper() else article
        else:
            word = word_parse[1][0].lower() + word_parse[1][1:] 
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon_Fem.JEDER_PARADIGM:
                if word.startswith(start):
                    #incase no grammatical case is found, treat as nominative, even if wrong.
                    if feats[1] == "_":
                        feats[1] = "Nom"
                    article = start + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1])
                    return article.capitalize() if word_parse[1][0].isupper() else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon_Fem.EIN_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon_Fem.ARTIKEL_EIN.get(feats[1])
                    return article.capitalize() if word_parse[1][0].isupper() else article
            if re.match(r"(U|u)(nser|nsre|nsere)", word):
                article = Lexicon_Fem.ARTIKEL_UNSER.get(feats[1])
                return article.capitalize() if word_parse[1][0].isupper() else article
            elif re.match(r"(E|e)(uer|ure)", word):
                article = Lexicon_Fem.ARTIKEL_EUER.get(feats[1])
                return article.capitalize() if word_parse[1][0].isupper() else article
            # Some articles don't have to be feminized, just return them.
            else:
                return word_parse[1]
            raise Exception(f"The Article seems to be not convertable:{word_parse[1]}")

    def feminize_adjectives(word_parse, has_article) -> str:
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
        adjective =  adjective + Lexicon_Fem.ARTIKEL_JEDER.get(feats[2])
        return adjective.capitalize() if word_parse[1][0].isupper() else adjective
    
    # Neutralize possesive jemand, this often doesn't get parsed correctly
    def feminize_pos_jemand(word_parse) -> str:
        word = "jemanders"
        return word.capitalize() if word_parse[1][0].isupper() else word
    
    def feminize_pronoun(word_parse,has_article) -> str:
        feats = word_parse[5].split("|")
        is_capitalized = word_parse[1][0].isupper()
        if feats[0] == "Neut":
            return word_parse[1]
        if word_parse[4] == "PPER":
            if feats[3] == "_":
                feats[3] = "Nom"
            pronoun = word_parse[1]
            if feats[0] == "3":
                pronoun = Lexicon_Fem.PRONOUNS.get(feats[3])
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
                    pronoun = word_parse[2][:-1] + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" and word_parse[1].startswith("d"):
            if feats[1] == "_":
                feats[1] = "Nom"
            pronoun = Lexicon_Fem.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if is_capitalized else pronoun
        elif word_parse[4] == "PRELS" or word_parse[4] == "PDS":
            if feats[1] == "_":
                feats[1] = "Nom"
            for start in Lexicon_Fem.JEDER_PARADIGM:
                if re.match(start + "e.?$", word_parse[2]):
                    pronoun = word_parse[2][:-1] + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1]) 
                    return pronoun.capitalize() if is_capitalized else pronoun
            pronoun = Lexicon_Fem.ARTIKEL_DER.get(feats[1])
            if re.match(r"d..jenige$", word_parse[2]):
                pronoun += "jenige"
                if feats[1] == "Gen" or feats[1] == "Dat":
                    pronoun += "n"
            if re.match(r"d..selbe$", word_parse[2]):
                pronoun += "selbe"
                if feats[1] == "Gen" or feats[1] == "Dat":
                    pronoun += "n"
            return pronoun.capitalize() if is_capitalized else pronoun

    def feminize_word(word_parse,has_article) -> str:
        # For Plural Cases, I think this doesn't have to be changed. Check with testing.
        if "Pl" in word_parse[5]:
            return word_parse[1]
        # feminize Articles
        elif word_parse[3] == "ART":
            return Lexicon_Fem.feminize_article(word_parse)
        # feminize Pronouns
        elif word_parse[3] == "PRO":
            return Lexicon_Fem.feminize_pronoun(word_parse,has_article)
        else:
            return word_parse[1]
    
    def __init__(self):
        pass
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
        return pronoun.capitalize() if word_parse[0] == "1" else pronoun
    
    def feminize_attributing_relative_pronoun(word_parse) -> str:
        article = "deren"
        return article.capitalize() if word_parse[0] == "1" else article
    
    def feminize_article(word_parse) -> str:
        feats = word_parse[5].split("|")
        # Case Definitive Articles
        if feats[0] == "Def":
            if feats[2] == "_":
                feats[2] = "Nom"
            article =  Lexicon_Fem.ARTIKEL_DER.get(feats[2])
            return article.capitalize() if word_parse[0] == "1" else article
        # Case Indifinitive Artikels, only ein
        elif feats[0] == "Indef":
            article = "ein" +  Lexicon_Fem.ARTIKEL_EIN.get(feats[2])
            return article.capitalize() if word_parse[0] == "1" else article
        else:
            word = word_parse[1][0].lower() + word_parse[1][1:] 
            # Jeder-Paradigm: jeder, jener, dieser, welcher, solcher, mancher, jedweder
            for start in Lexicon_Fem.JEDER_PARADIGM:
                if word.startswith(start):
                    #incase no grammatical case is found, treat as nominative, even if wrong.
                    if feats[1] == "_":
                        feats[1] = "Nom"
                    article = start + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1])
                    return article.capitalize() if word_parse[0] == "1" else article
            # Ein-Paradigm: einer, keiner, meiner, deiner, seiner, ihrer, enser 
            for start in Lexicon_Fem.EIN_PARADIGM:
                if word.startswith(start):
                    article = start + Lexicon_Fem.ARTIKEL_EIN.get(feats[1])
                    return article.capitalize() if word_parse[0] == "1" else article
            if re.match(r"(U|u)(nser|nsre|nsere)", word):
                article = Lexicon_Fem.ARTIKEL_UNSER.get(feats[1])
                return article.capitalize() if word_parse[0] == "1" else article
            elif re.match(r"(E|e)(uer|ure)", word):
                article = Lexicon_Fem.ARTIKEL_EUER.get(feats[1])
                return article.capitalize() if word_parse[0] == "1" else article
            # Some articles don't have to be feminized, just return them.
            else:
                return word_parse[1]
            raise Exception(f"The Article seems to be not convertable:{word_parse[1]}")

    def feminize_adjectives(word_parse, article_parse) -> str:
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
        adjective =  adjective + Lexicon_Fem.ARTIKEL_JEDER.get(feats[2])
        return adjective.capitalize() if word_parse[0] == "1" else adjective
    
    # Neutralize possesive jemand, this often doesn't get parsed correctly
    def feminize_pos_jemand(word_parse) -> str:
        word = "jemanders"
        return word.capitalize() if word_parse[0] == "1" else word
    
    # Neutralize Prepostions if they are compound articles with prepositions, e.g. zur/im/beim
    def feminize_preposition(word_parse) -> str:
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
    
    def feminize_pronoun(word_parse) -> str:
        feats = word_parse[5].split("|")
        if feats[0] == "Neut":
            return word_parse[1]
        if word_parse[4] == "PPER":
            pronoun = word_parse[1]
            if feats[0] == "3":
                pronoun = Lexicon_Fem.PRONOUNS.get(feats[3])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun
        elif word_parse[4] == "PIS":
            pronoun = word_parse[1]
            if feats[1] == "_":
                feats[1] = "Nom"
            if word_parse[2] == "man":
                pronoun = "mensch"
            elif word_parse[2].endswith("mand"):
                if feats[1] == "Dat" or feats[1] == "Gen":
                    pronoun = word_parse[2] + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1])
            else: 
                pronoun = word_parse[2][:-1] + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun
        elif word_parse[4] == "PRELS":
            pronoun = Lexicon_Fem.ARTIKEL_DER.get(feats[1])
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun
        elif word_parse[4] == "PDS":
            for start in Lexicon_Fem.JEDER_PARADIGM:
                if word_parse[1].startswith(start):
                    pronoun = word_parse[2][:-1] + Lexicon_Fem.ARTIKEL_JEDER.get(feats[1]) 
                    return pronoun.capitalize() if word_parse[0] == "1" else pronoun
            pronoun = Lexicon_Fem.ARTIKEL_DER.get(feats[1])
            if word_parse[2].endswith("jenige"):
                pronoun += "jenige"
            return pronoun.capitalize() if word_parse[0] == "1" else pronoun

    def feminize_word(word_parse) -> str:
        # For Plural Cases, I think this doesn't have to be changed. Check with testing.
        if "Pl" in word_parse[5]:
            return word_parse[1]
        # feminize Articles
        elif word_parse[3] == "ART":
            return Lexicon_Fem.feminize_article(word_parse)
        # feminize Pronouns
        elif word_parse[3] == "PRO":
            return Lexicon_Fem.feminize_pronoun(word_parse)
        elif word_parse[3] == "PREP" and word_parse[4] == "APPRART":
            return Lexicon_Fem.feminize_preposition(word_parse)
        else:
            return word_parse[1]
    
    def __init__(self):
        pass
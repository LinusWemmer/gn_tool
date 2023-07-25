from lexicon import Lexicon
from lexicon_fem import Lexicon_Fem
import re

# The Marking_tool class is a class that stores the parsing data for a sentence.
# It also has functionality to work with the data:
#   - finding nounphrases
#   - getting the sentence from the parse
#   - converting a nounphrase into the inklusive form based on the de-e System.

class Marking_Tool:
    def __init__(self, words):
        # List of the 
        self.words = words
        # List of the conll parse strings split into a list 
        # The format of the list is as follows (conll format):
        # 0:POSTION 1:FORM 2:STEM 3:CPOSTAG 4:POSTAG 5:FEATS 6:HEAD 7:DEPREL 8:PHEAD
        self.parse_list = []
        for word in words:
            self.parse_list.append(word.split("\t"))
        self.nounphrases = {}

    # Returns the sentence underlying the parse.
    def get_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            if word_parse[3]== ("$.") or word_parse[3]== ("$,"):
                sentence = sentence[:-1] + word_parse[1] + " "
            elif word_parse[3] == ("$("):
                sentence += word_parse[1]
            else:
                sentence += word_parse[1] + " "
        return sentence

    # Finds all "nounphrases" of the sentence and stores them in a dict.
    # Returns True if the word is a role noun, otherwise false.
    def find_nounphrase(self, word_parse):
        self.nounphrases[int(word_parse[0])] = self.find_children(word_parse[0])
        print(self.nounphrases)
    
    # Finds all nounphrases of the sentence that come role nouns
    def find_nounphrases(self):
        for word_parse in self.parse_list:
            if word_parse[3] == "N":
                self.find_nounphrase(word_parse)


    def find_children(self, pos: int):
        children = []
        for word_parse in self.parse_list:
            if word_parse[6] == pos and word_parse[3] != "N":
                children.append(int(word_parse[0]))
                children.extend(self.find_children(word_parse[0]))
            #else:
            #    children.extend(self.find_dessen(word_parse[0]))
        return children

    def get_nounphrase(self, pos:int):
        return self.nounphrases.get(pos)
    
    def neutralize_word(self, pos:int, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to included when neutralizing the word.
            self.parse_list[pos][1] = Lexicon.neutralize_adjectives(self.parse_list[pos], self.parse_list[article_pos-1])
        else:
            self.parse_list[pos][1] = Lexicon.neutralize_word(self.parse_list[pos])

    def feminize_word(self, pos:int, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to included when neutralizing the word.
            self.parse_list[pos][1] = Lexicon_Fem.feminize_adjectives(word_parse, self.parse_list[article_pos-1])
        else:
            self.parse_list[pos][1] = Lexicon_Fem.feminize_word(word_parse)
    
    def neutralize_nounphrase(self, pos:int, line:int):
        feats = self.parse_list[pos][5].split("|")
        # Neutralize a Noun
        if self.parse_list[pos][3] == "N":
            # Noun is a substantivized adjective
            if line == -1:
                article_pos = pos+1
                nounphrase = self.nounphrases.get(pos+1)
                if nounphrase:
                    for child_pos in nounphrase: 
                        if self.parse_list[child_pos-1][3] == "ART":
                            article_pos = child_pos
                    #article_pos = min(nounphrase)
                self.parse_list[pos][1] = Lexicon.neutralize_sub_adj(self.parse_list[pos], self.parse_list[article_pos-1])
            # words ending on -mann or -frau:
            elif line == -2:
                self.parse_list[pos][1] = Lexicon.neutralize_special_nouns(self.parse_list[pos], line)
                feats = self.parse_list[pos][5].split("|")
                if feats[0] == "Masc" and feats[2] == "Sg":
                    for child in self.nounphrases.get(pos+1):
                        article_pos = min(self.nounphrases.get(pos+1))
                        self.feminize_word(child-1, article_pos)
                return
            # Special neologisms    
            elif line <= -3:
                self.parse_list[pos][1] = Lexicon.neutralize_special_nouns(self.parse_list[pos], line)
            # Noun is a classical role noun
            else:
                # Parzu sometimes doesn't correctly mark singular/plural, so we check these cases and mark them ourselves
                if feats[2] == "_":
                    if self.parse_list[pos][1].endswith("ern") and not self.parse_list[pos][1] == "Bauern":
                        feats[1] = "Dat"
                        feats[2] = "Pl"
                    else:
                        feats[2] = "Sg"
                #Special handling if the role noun is a split word with "-"
                if "-" in self.parse_list[pos][1]:
                    word_split = self.parse_list[pos][1].split("-")
                    self.parse_list[pos][1] = word_split[0] + "-" + Lexicon.neutralize_noun(feats, line)
                else:
                    self.parse_list[pos][1] = Lexicon.neutralize_noun(feats, line)
        # Neutralize Personal Pronouns
        elif self.parse_list[pos][4] == "PPOSAT":
            self.parse_list[pos][1] = Lexicon.neutralize_possesive_pronoun(self.parse_list[pos])
        # Neutralized attributing relative pronoun
        elif self.parse_list[pos][4] == "PRELAT":
            self.parse_list[pos][1] = Lexicon.neutralize_attributing_relative_pronoun(self.parse_list[pos])
        elif re.match(r"(J|j)emand(e?)s" , self.parse_list[pos][1]):
                print("here")
                self.parse_list[pos][1] = Lexicon.neutralize_pos_jemand(self.parse_list[pos])
        #Neutralize everything else
        else:
            self.parse_list[pos][1] = Lexicon.neutralize_word(self.parse_list[pos])
        for child in self.nounphrases.get(pos+1):
            article_pos = min(self.nounphrases.get(pos+1))
            self.neutralize_word(child-1, article_pos)

    # Generates the html form, with noun phrases marked 
    def get_marking_form(self, sentence_number) -> str:
        #self.find_nounphrases()
        nouns = ""
        for word_parse in self.parse_list:
            # Case: Possesive Pronoun
            if word_parse[4] == "PPOSAT" and not re.match(r"((M|m|D|d)ein)|((U|u)ns)|((E|e)u(re|er))", word_parse[1]):
                # A possesive pronoun should only be selectable to be neutralized if it is in third person
                # Parzu doesn't tag this, so we have to filter out the other cases manually.
                self.find_nounphrase(word_parse)
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select">
                <label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            # Case: Noun
            elif word_parse[3] == "N":
                line = Lexicon.check_role_noun(word_parse)
                if line:
                    self.find_nounphrase(word_parse)
                    input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{line}" name="{sentence_number}|{word_parse[0]}|{line}" value="select">
                    <label for="{sentence_number}|{word_parse[0]}|{line}">{"<u>" + word_parse[1] + "</u>"}</label> """
                    nouns += input_form
                else: 
                    nouns += word_parse[1] + " "
            # Case: Pronoun
            elif word_parse[3] == "PRO" and (word_parse[5][0] == "3" or word_parse[4] == "PIS" or word_parse[4] == "PDS") and not word_parse[4] == "PRF" and ("Neut" not in word_parse[5])  and ("Pl" not in word_parse[5]) and not word_parse[2] == "viel" and not word_parse[2] == "alle":
                self.find_nounphrase(word_parse)
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select">
                <label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            # case: jemand (sometimes marked as adjective, should still be neutralizable in that case)
            elif re.match(r"(J|j)emand(e?)s" , word_parse[1]):
                self.find_nounphrase(word_parse)
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select">
                <label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            elif word_parse[3] == "PREP" and word_parse[4] == "APPRART":
                self.find_nounphrase(word_parse)
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select">
                <label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            elif word_parse[4] == "PRELAT":
                self.find_nounphrase(word_parse)
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select">
                <label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            elif word_parse[3] == "ART" and word_parse[6] == "0":
                self.find_nounphrase(word_parse)
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select">
                <label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            elif word_parse[3] == "$." or word_parse[3] == "$,":
                nouns = nouns[:-1] + word_parse[1] + " "
            elif word_parse[3] == "$(":
                nouns += word_parse[1]
            else:
               nouns += word_parse[1] + " "
        print(self.nounphrases)
        return nouns
from lexicon import Lexicon
from lexicon_fem import Lexicon_Fem
import re

# The Marking_tool class is a class that stores the parsing data for a sentence.
# It also has functionality to work with the data:
#   - finding nounphrases
#   - getting the sentence from the parse
#   - converting a nounphrase into the inklusive form based on the de-e System.

class Marking_Tool:
    def __init__(self, parse_list, nounphrases = {}):
    
        # List of the conll parse strings split into a list 
        # The format of the list is as follows (conll format):
        # 0:POSTION 1:FORM 2:STEM 3:CPOSTAG 4:POSTAG 5:FEATS 6:HEAD 7:DEPREL 8:PHEAD
        self.parse_list = parse_list
        self.nounphrases = nounphrases

    def serialize(self):
        return {"parse_list": self.parse_list,
                "nounphrases": self.nounphrases}

    # Returns the sentence underlying the parse.
    #def get_sentence(self, split_list = []) -> str:
    def get_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            #if word_parse[3]== ("$.") or word_parse[3]== ("$,"):
            #    sentence = sentence[:-1] + word_parse[1] + " "
            #elif word_parse[3] == ("$("):
            #    if word_parse[1] == "(":
            #        sentence += word_parse[1]
            #    else:
            #        sentence = sentence[:-1] + word_parse[1] + " "
            #else:
            #    if int(word_parse[0]) in split_list:
            #        preposition = word_parse[1] + " " + self.parse_list[int(word_parse[0])][1]
            #        sentence += self.get_prepositions(preposition) + " "
            #    elif int(word_parse[0]) - 1 in split_list:
            #        pass
            #    else:
            #        sentence += word_parse[1] + " "
            sentence += word_parse[-2]
            sentence += word_parse[-1]
        return sentence
    

    def get_internal_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            #if word_parse[3]== ("$.") or word_parse[3]== ("$,"):
            #    sentence = sentence[:-1] + word_parse[1] + " "
            #elif word_parse[3] == ("$("):
            #    if word_parse[1] == "(":
            #        sentence += word_parse[1]
            #    else:
            #        sentence = sentence[:-1] + word_parse[1] + " "
            #else:
            #    if int(word_parse[0]) in split_list:
            #        preposition = word_parse[1] + " " + self.parse_list[int(word_parse[0])][1]
            #        sentence += self.get_prepositions(preposition) + " "
            #    elif int(word_parse[0]) - 1 in split_list:
            #        pass
            #    else:
            #        sentence += word_parse[1] + " "
            sentence += word_parse[1]
            sentence += word_parse[-1]
        return sentence

    # Adds a single nounphrase to the dictionary "nounphrases". The key is
    # the index of the head of the nounphrase, while the value is the list of
    # all indices of its children.
    def find_nounphrase(self, word_parse):
        self.nounphrases[int(word_parse[0])] = self.find_children(word_parse[0])
        print(self.nounphrases)
    
    # Apparently the following is not used in the code:
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
            self.parse_list[pos][-2] = Lexicon.neutralize_adjectives(word_parse, self.parse_list[article_pos-1])
        elif word_parse[4] == "PIDAT" and pos != article_pos-1:
            # This case covers morphologically adjectival determiners like the word "jeden" in "eines jeden Bürgers".
            # Since the feature list of a PIDAT determiner has a differnt structure than that of an
            # adjective, we need to first adapt its structure:
            word_parse[5] = "POS|" + word_parse[5] + "|_|"
            self.parse_list[pos][-2] = Lexicon.neutralize_adjectives(word_parse, self.parse_list[article_pos-1])
        else:
            neutralized_word = Lexicon.neutralize_word(self.parse_list[pos])
            if neutralized_word == "derm" and (self.parse_list[pos-1][1] == "Zu" or self.parse_list[pos-1][1] == "zu"):
                self.parse_list[pos-1][-1] = ""
                self.parse_list[pos][-2] = "rm"
            elif neutralized_word == "derm" and (self.parse_list[pos][-2] == "r" or self.parse_list[pos][-2] == "m"):
                self.parse_list[pos-1][-1] = " "
                self.parse_list[pos][-2] = "derm"
            else:
                self.parse_list[pos][-2] = neutralized_word

    def feminize_word(self, pos:int, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to included when neutralizing the word.
            self.parse_list[pos][-2] = Lexicon_Fem.feminize_adjectives(word_parse, self.parse_list[article_pos-1])
        else:
            feminized_word = Lexicon_Fem.feminize_word(self.parse_list[pos])
            if feminized_word == "der" and (self.parse_list[pos-1][1] == "Zu" or self.parse_list[pos-1][1] == "zu"):
                self.parse_list[pos-1][-1] = ""
                self.parse_list[pos][-2] = "r"
            elif feminized_word == "der" and (self.parse_list[pos][-2] == "r" or self.parse_list[pos][-2] == "m"):
                self.parse_list[pos-1][-1] = " "
                self.parse_list[pos][-2] = "der"
            else:
                self.parse_list[pos][-2] = feminized_word

    def determine_number(self, pos:int, feats:list, plural:bool):
        if self.parse_list[pos][1].endswith("ern") and not self.parse_list[pos][1] == "Bauern":
            feats[1] = "Dat"
            feats[2] = "Pl"
        # Wenn bei "Ahnen"/"Vorfahren"/"Nachfahren" erkannt wird, dass es Nominativ ist, aber kein Numerus erkannt wird, dann ist es ein Plural.
        elif (self.parse_list[pos][1] == "Ahnen" or self.parse_list[pos][1] == "Vorfahren" or self.parse_list[pos][1] == "Nachfahren") and feats[1] == "Nom":
                feats[2] = "Pl"
        else:
            article = False
            for child in self.nounphrases.get(pos+1):
                if self.parse_list[child-1][3] == "ART":
                    article = True
                    article_position = child-1
                    break
            if article:
                # Wenn ein Substantiv einen Artikel hat und im Parzu-Parse kein Numerus hat, im Dativ steht und sich ein auf "-en" endender Artikel drauf bezieht, dann ist das Substantiv im Plural.
                if feats[1] == "Dat" and self.parse_list[article_position][1].endswith("en"):
                    feats[2] = "Pl"
                else:
                    feats[2] = "Sg"
            elif not re.match(r"(A|a)ls", self.parse_list[int(self.parse_list[pos][6])-1][1]):
                print(self.parse_list[pos][1])
                print("nicht von 'als' abhängig.")
                feats[2] = "Pl"
            else:
                index_of_last_np_before_als = self.find_last_np_before_index(int(self.parse_list[pos][6]))
                print("index_of_last_np_before_als")
                print(index_of_last_np_before_als)
                if index_of_last_np_before_als > 0:
                    otherfeats = self.parse_list[index_of_last_np_before_als-1][5].split("|")
                    if self.parse_list[index_of_last_np_before_als-1][3] == "N":
                        feats[1] = otherfeats[1]
                        feats[2] = otherfeats[2]
                    elif self.parse_list[index_of_last_np_before_als-1][3] == "PRO":
                        feats[1] = otherfeats[3]
                        feats[2] = otherfeats[1]
                        print("feats:")
                        print(feats)
                    # Hier oben und unten werden wahrscheinlich noch mehr Fälle als "N" und "PRO" benötigt, zum Beispiel für den Fall, dass "jemand" als Adjektiv geparst wird.
                else:
                    index_of_first_np_after_als_construct = self.find_first_np_after_index(pos+1)
                    print("index_of_first_np_after_als")
                    print(index_of_first_np_after_als_construct)
                    if index_of_first_np_after_als_construct > 0:
                        otherfeats = self.parse_list[index_of_first_np_after_als_construct-1][5].split("|")
                        if self.parse_list[index_of_first_np_after_als_construct-1][3] == "N":
                            feats[2] = otherfeats[2]
                        elif self.parse_list[index_of_first_np_after_als_construct-1][3] == "PRO":
                            feats[2] = otherfeats[1]
                    else:
                        feats[2] = "Sg"
    
    def find_last_np_before_index(self, als_index:int):
        for i in range(als_index-1,0,-1):
            if i in self.nounphrases:
                return i
        return 0
    
    def find_first_np_after_index(self, als_index:int):
        print("als_index")
        print(als_index)
        for i in range(als_index+1,len(self.parse_list)+1):
            if i in self.nounphrases:
                return i
        return 0


    # This function neutralizes the word that has been selected. Then, all dependent words in the sentence are neutralized.
    def neutralize_nounphrase(self, pos:int, line:int):
        feats = self.parse_list[pos][5].split("|")
        if len(feats) == 1:
            feats.append("_")
            feats.append("_")
        plural = True

        # Neutralize a Noun
        if self.parse_list[pos][3] == "N":
            if feats[2] == "_":
                print("Noun without number:")
                print(self.parse_list[pos][1])
                self.determine_number(pos,feats,plural)
            if feats[1] == "_" and self.parse_list[pos][1].endswith("ern") and not self.parse_list[pos][1] == "Bauern":
                feats[1] = "Dat"
            # Nach "zwischen", "unter", "vor", "hinter", "neben" nicht erkanntes Kasus zu Dativ machen.
            if feats[1] == "_":
                if int(self.parse_list[pos][6]) != 0:
                    if self.parse_list[int(self.parse_list[pos][6])-1][2] in ["zwischen","unter","vor","hinter","neben"]:
                        feats[1] = "Dat"
                    elif int(self.parse_list[int(self.parse_list[pos][6])-1][6]) != 0:
                        if int(self.parse_list[int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1][6]) != 0:
                            if self.parse_list[int(self.parse_list[int(self.parse_list[int(self.parse_list[pos][6])-1][6])-1][6])-1][2] in ["zwischen","unter","vor","hinter","neben"]:
                                feats[1] = "Dat"
            if feats[2] == "Sg" or feats[2] == "_":
                plural = False
            # Noun is a substantivized adjective 
            if line == -1:
                article_pos = pos
                print("article_pos:")
                print(article_pos)
                nounphrase = self.nounphrases.get(pos+1)
                print("nounphrase:")
                print(nounphrase)
                if nounphrase:
                    for child_pos in nounphrase: 
                        if self.parse_list[child_pos-1][3] == "ART":
                            article_pos = child_pos
                    #article_pos = min(nounphrase)
                # If self.parse_list[pos][-2] starts with a small letter, it should stay that way.
                if self.parse_list[pos][-2][0].islower():
                    self.parse_list[pos][-2] = Lexicon.neutralize_sub_adj(self.parse_list[pos], self.parse_list[article_pos-1], feats).lower()
                else:
                    self.parse_list[pos][-2] = Lexicon.neutralize_sub_adj(self.parse_list[pos], self.parse_list[article_pos-1], feats)
            # words ending on -mann or -frau:
            elif line == -2:
                self.parse_list[pos][-2] = Lexicon.neutralize_gendered_suffix(self.parse_list[pos])
                feats = self.parse_list[pos][5].split("|")
                if feats[0] == "Masc" and feats[2] != "Pl":
                    for child in self.nounphrases.get(pos+1):
                        article_pos = min(self.nounphrases.get(pos+1))
                        self.feminize_word(child-1, article_pos)
                return
            # The Word "Mann", "Frau", "Herr", "Dame":
            elif line == -4:
                self.parse_list[pos][-2] = Lexicon.neutralize_mann_frau(self.parse_list[pos])
                feats = self.parse_list[pos][5].split("|")
                if feats[0] == "Masc" and feats[2] == "Sg":
                    for child in self.nounphrases.get(pos+1):
                        article_pos = min(self.nounphrases.get(pos+1))
                        self.feminize_word(child-1, article_pos)
                return
            # Noun is a romanism
            elif line == -10:
                self.parse_list[pos][-2] = Lexicon.neutralize_romanism(self.parse_list[pos])
            # Noun is irregular
            elif line == -11:
                self.parse_list[pos][-2] = Lexicon.neutralize_irregular_noun(self.parse_list[pos])
            # Noun is already neutral:
            elif line == -12:
                pass
            # Special neologisms    
            elif line <= -3:
                self.parse_list[pos][-2] = Lexicon.neutralize_neologism(self.parse_list[pos])
            # Noun is the Special case "Beamter" (line 88)
            elif line == 88:
                article_pos = pos+1
                nounphrase = self.nounphrases.get(pos+1)
                if nounphrase:
                    for child_pos in nounphrase: 
                        if self.parse_list[child_pos-1][3] == "ART":
                            article_pos = child_pos
                self.parse_list[pos][-2] = Lexicon.neutralize_beamter(self.parse_list[pos], self.parse_list[article_pos-1])
            # Noun is a classical role noun
            else:
                #Special handling if the role noun is a split word with "-"
                if "-" in self.parse_list[pos][1]:
                    word_split = self.parse_list[pos][1].split("-")
                    self.parse_list[pos][-2] = word_split[0] + "-" + Lexicon.neutralize_noun(feats, line)
                # Noun is a normal word in our List of movierbare Substantive
                elif self.parse_list[pos][2].startswith(Lexicon.MALE_NOUNS[line][:-1]) or self.parse_list[pos][2].startswith(Lexicon.FEMALE_NOUNS[line][:-1]): # Weird check to see if our noun is split or not, this should work most of the time
                    self.parse_list[pos][-2] = Lexicon.neutralize_noun(feats, line) 
                # Noun is zusammengesetzt ohne Bindestrich
                else:
                    self.parse_list[pos][-2] = Lexicon.neutralize_split_noun(feats, line, self.parse_list[pos][2])
        # Neutralize Personal Pronouns
        elif self.parse_list[pos][4] == "PPOSAT":
            self.parse_list[pos][-2] = Lexicon.neutralize_possesive_pronoun(self.parse_list[pos])
            # Here we additionally need to modify the input possessive pronoun, so that the output is correct when this pronoun needs to be modified further due to the noun it modifies being put into the inklusivum.
            self.parse_list[pos][1] = Lexicon.neutralize_possesive_pronoun(self.parse_list[pos])
        # Neutralized attributing relative pronoun
        elif self.parse_list[pos][4] == "PRELAT":
            self.parse_list[pos][-2] = Lexicon.neutralize_attributing_relative_pronoun(self.parse_list[pos])
        elif re.match(r"(J|j)emand(e?)s" , self.parse_list[pos][1]):
                print("here")
                self.parse_list[pos][-2] = Lexicon.neutralize_pos_jemand(self.parse_list[pos])
        #Neutralize everything else
        else:
            self.parse_list[pos][-2] = Lexicon.neutralize_word(self.parse_list[pos])
        # Neutralize the remaining words in the nounphrase:
        if not plural:
            for child in self.nounphrases.get(pos+1):
                article_pos = min(self.nounphrases.get(pos+1))
                self.neutralize_word(child-1, article_pos)


    # Generates the html form, with noun phrases marked 
    def get_marking_form(self, sentence_number) -> str:
        nouns = ""
        for word_parse in self.parse_list:
            # Case: Possesive Pronoun
            if word_parse[4] == "PPOSAT" and not re.match(r"((M|m|D|d)ein)|((U|u)ns)|((E|e)u(re|er))", word_parse[1]):
                # A possesive pronoun should only be selectable to be neutralized if it is in third person
                # Parzu doesn't tag this, so we have to filter out the other cases manually.
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            # Case: Noun
            elif word_parse[3] == "N":
                self.find_nounphrase(word_parse)
                line = Lexicon.check_role_noun(word_parse)
                if line:
                    #self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{line}" name="{sentence_number}|{word_parse[0]}|{line}" value="select"><label for="{sentence_number}|{word_parse[0]}|{line}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                    nouns += input_form
                else: 
                    nouns += word_parse[-2]
                    nouns += word_parse[-1]
            # Case: Pronoun
            elif word_parse[3] == "PRO" and (word_parse[5][0] == "3" or word_parse[4] == "PIS" or word_parse[4] == "PDS") and not word_parse[4] == "PRF" and ("Neut" not in word_parse[5])  and ("Pl" not in word_parse[5]) and not word_parse[2] == "viel" and not word_parse[2] == "alle" and not word_parse[2] == "etwas":
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            # case: jemand (sometimes marked as adjective, should still be neutralizable in that case)
            elif re.match(r"(J|j)emand(e?)s" , word_parse[1]):
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            elif word_parse[3] == "PREP" and word_parse[4] == "APPRART":
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            elif word_parse[4] == "PRELAT":
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            elif word_parse[4] == "PRELS" and word_parse[6] == "0":
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            elif word_parse[3] == "ART" and word_parse[6] == "0":
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                nouns += input_form
            #elif word_parse[3] == "$." or word_parse[3] == "$,":
            #    nouns = nouns[:-1] + word_parse[1] + " "
            #elif word_parse[3] == "$(":
            #    if word_parse[1] == "(":
            #        nouns += word_parse[1]
            #    elif word_parse[1] == ")":
            #        nouns = nouns[:-1] + word_parse[1] + " "
            #    else:
            #        nouns += word_parse[1]
            else:
               nouns += word_parse[-2]
               nouns += word_parse[-1]
        print(self.nounphrases)
        return nouns
    
    def final_whitespace(self, S):
        # Initialize an empty string to store the final whitespace
        whitespace = ""
        
        # Loop through each character in the string
        for char in reversed(S):
            # Check if the character is whitespace
            if char == " " or char == "\n" or char == "\r" or char == "\t":
                # Add the whitespace character to the result
                whitespace = char + whitespace
            else:
                # Break the loop if a non-whitespace character is found
                break
        
        return whitespace

    def find_realizations(self, input_text: str):
        position_after_preposition = False
        for word in self.parse_list:
            print("word:")
            print(word)
            if position_after_preposition == True and word[1].startswith("d") and len(word[1]) == 3:
                pattern = re.escape(word[1]) + "|" + re.escape(word[1][2])
            elif word[1] == "in":
                pattern = "in|i(?!n)"
            elif word[1] == "an":
                pattern = "an|a(?!n)"
            elif word[1] == "von":
                pattern = "von|vo(?!n)"
            else:
                pattern = re.escape(word[1])
            match = re.search("^" + pattern, input_text, re.IGNORECASE)
            if match:
                realization = match.group(0)
                remaining_text = input_text[match.end():]
                whitespace_pattern = "^( |\n|\r|\t)*"
                whitespace_match = re.search(whitespace_pattern,remaining_text)
                input_text = remaining_text[whitespace_match.end():]
                white_realization = whitespace_match.group(0)
            else:
                print(input_text)
                raise Exception("The word \"" + pattern + "\" could not be found in the input text, even though it was expected according to the parse list")
            #realization, input_text = self.find_prefix_regex(pattern,input_text)
            word.append(realization)
            word.append(white_realization)
            if word[1] in ["bei","Bei","zu","zu","in","In","von","Von","vor","Vor","an","An","auf","Auf","für","Für"]:
                position_after_preposition = True
            else:
                position_after_preposition = False
        return input_text


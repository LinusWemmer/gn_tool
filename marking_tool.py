from lexicon import Lexicon
from lexicon_fem import Lexicon_Fem
import re

# The Marking_tool class is a class that stores the parsing data for a sentence.
# It also has functionality to work with the data:
#   - finding nounphrases
#   - getting the sentence from the parse
#   - converting a nounphrase into the inklusive form based on the de-e System.

class Marking_Tool:
    def __init__(self, parse_list, nounphrases = {}, nounlist = []):
    
        # List of the conll parse strings split into a list 
        # The format of the list is as follows (conll format):
        # 0:POSTION 1:FORM 2:STEM 3:CPOSTAG 4:POSTAG 5:FEATS 6:HEAD 7:DEPREL 8:PHEAD
        self.parse_list = parse_list
        self.nounphrases = nounphrases
        # nounlist is a list of lists, where each list contains the following information about a noun:
        # [word_index_from_1, position_of_noun_in_composite_noun, original, neutralized, suffix, noun_type, capitalized, head_identified_as_person_noun]
        self.nounlist = nounlist
        self.find_nounphrases()

    def serialize(self):
        return {"parse_list": self.parse_list,
                "nounphrases": self.nounphrases}

    # Returns the output sentence.
    def get_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            sentence += word_parse[-2]
            sentence += word_parse[-1]
        return sentence
    
    # Returns the input sentence with slight modifications for reparsing.
    def get_internal_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            if (len(word_parse[-2]) != len(word_parse[1]) and not word_parse[2] == "glauben") or word_parse[1] == '"':
                sentence = sentence + word_parse[-2]
            else:
                sentence += word_parse[1]
            sentence += word_parse[-1]
        return sentence

    # Adds all nounphrases to the dictionary "nounphrases". 
    def find_nounphrases(self):
        for word_parse in self.parse_list:
            if word_parse[3] == "N" or word_parse[3] == "PRO":
                self.find_nounphrase(word_parse)

    # Adds a single nounphrase to the dictionary "nounphrases". The key is
    # the index of the head of the nounphrase, while the value is the list of
    # all indices of its children.
    def find_nounphrase(self, word_parse):
        # If the word isn't yet in the dictionary, we add it.
        if int(word_parse[0]) not in self.nounphrases:
            self.nounphrases[int(word_parse[0])] = self.find_children(word_parse[0],False)
        print(self.nounphrases)

    # The last argument keeps track of whether we have traversed a preposition in the parse tree.
    def find_children(self, pos: int, preposition: bool):
        children = []
        for word_parse in self.parse_list:
            if word_parse[6] == pos and word_parse[3] != "N":
                # Once we have traversed a preposition, we only include relative pronouns:
                if not preposition or word_parse[4] == "PRELS":
                    children.append(int(word_parse[0]))
                if word_parse[3] == "PREP":
                    children.extend(self.find_children(word_parse[0],True))
                else:
                    children.extend(self.find_children(word_parse[0],preposition))
                # In relative sentences that depend on the noun phrase, we want to indlude the relative pronoun, but nothing else.
                if word_parse[4] == "PRELS":
                    break
            #else:
            #    children.extend(self.find_dessen(word_parse[0]))
        return children
    
    # This function neutralizes the word that has been selected.
    def neutralize_word(self, pos:int, has_article:bool, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            self.parse_list[pos][-2] = Lexicon.neutralize_adjectives(word_parse, has_article)
        elif word_parse[4] == "PIDAT" and pos != article_pos-1:
            # This case covers morphologically adjectival determiners like the word "jeden" in "eines jeden Bürgers".
            # Since the feature list of a PIDAT determiner has a differnt structure than that of an
            # adjective, we need to first adapt its structure:
            word_parse[5] = "POS|" + word_parse[5] + "|_|"
            if word_parse[2] != "alle":
                self.parse_list[pos][-2] = Lexicon.neutralize_adjectives(word_parse, has_article)
        else:
            neutralized_word = Lexicon.neutralize_word(self.parse_list[pos],has_article)
            if neutralized_word == "derm" and (self.parse_list[pos-1][1] == "Zu" or self.parse_list[pos-1][1] == "zu"):
                self.parse_list[pos-1][-1] = ""
                self.parse_list[pos][-2] = "rm"
            elif neutralized_word == "derm" and (self.parse_list[pos][-2] == "r" or self.parse_list[pos][-2] == "m"):
                self.parse_list[pos-1][-1] = " "
                if self.parse_list[pos-1][-2] == "i":
                    self.parse_list[pos-1][-2] = "in"
                elif self.parse_list[pos-1][-2] == "vo":
                    self.parse_list[pos-1][-2] = "von"
                elif self.parse_list[pos-1][-2] == "a":
                    self.parse_list[pos-1][-2] = "an"
                self.parse_list[pos][-2] = "derm"
            else:
                self.parse_list[pos][-2] = neutralized_word

    # This function feminizes the word that has been selected.
    def feminize_word(self, pos:int, has_article:bool):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to included when neutralizing the word.
            self.parse_list[pos][-2] = Lexicon_Fem.feminize_adjectives(word_parse, has_article)
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

    # This function determines the number of a noun for which no number has been recognized by ParZu.
    def determine_number(self, pos:int, feats:list):
        # Wenn das Substantiv auf "mann", "frau", "herr" oder "dame" endet, dann ist es im Singular.
        if self.parse_list[pos][1].endswith("mann") or self.parse_list[pos][1].endswith("frau") or self.parse_list[pos][1].endswith("herr") or self.parse_list[pos][1].endswith("dame"):
           feats[2] = "Sg"
        # Wenn das Substantiv auf "ern" endet und nicht auf "bauern", dann ist es im Plural.
        elif self.parse_list[pos][1].endswith("ern") and not self.parse_list[pos][1].lower().endswith("bauern"):
            feats[1] = "Dat"
            feats[2] = "Pl"
        # Wenn das Substantiv ein Prädikativ eines singularischen Verbes ist, dann ist es im Singular:
        elif self.parse_list[pos][7] == "pred" and self.parse_list[int(self.parse_list[pos][6])-1][3] == "V" and self.parse_list[int(self.parse_list[pos][6])-1][5].split("|")[1] == "Sg":
            feats[2] = "Sg"
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
                # Wenn ein Substantiv einen Artikel hat und im Parzu-Parse kein Numerus hat, im Maskulinum steht (oder auf "-er" endet) und sich ein auf "-e" endender Artikel drauf bezieht, dann ist das Substantiv im Plural.
                if (feats[0] == "Masc" or self.parse_list[pos][1].endswith("er")) and self.parse_list[article_position][1].endswith("e"):
                    feats[2] = "Pl"
                # Wenn der Artikel "alle" lautet, setze den Numerus des Substantivs auf Plural.
                elif self.parse_list[article_position][2] == "alle":
                    feats[2] = "Pl"
                # Wenn ein Substantiv einen Artikel hat und im Parzu-Parse kein Numerus hat, im Dativ steht und sich ein auf "-en" endender Artikel drauf bezieht, dann ist das Substantiv im Plural.
                elif feats[1] == "Dat" and self.parse_list[article_position][1].endswith("en"):
                    feats[2] = "Pl"
                # Ansonsten ist ein Substantiv mit Artikel und einem nicht erkannten Numerus im Singular.
                else:
                    feats[2] = "Sg"
            # Wenn das Substantiv nicht von "als" abhängig ist (lässt sich im ParZu-Parsebaum überprüfen),
            # setze den Numerus des Substantivs auf "Pl":
            elif not re.match(r"(A|a)ls", self.parse_list[int(self.parse_list[pos][6])-1][1]):
                feats[2] = "Pl"
            else:
                # Wenn eine davorstehende Nominalphrase (oder eine Propositionalphrase mit einer Nominalphrase) im Syntaxbaum an "als" angebunden ist (manchmal erzeugt Parzu komische Anbindungen an danachstehende Nominalphrasen, sodass die Bedingung "davorstehende" wichtig ist),
                # kopiere den Numerus und Kasus von dieser Nominalphrase auf das Substantiv ohne Numerus:
                index_of_last_np_before_als = self.find_last_np_before_index(int(self.parse_list[pos][6]))
                if index_of_last_np_before_als > 0:
                    otherfeats = self.parse_list[index_of_last_np_before_als-1][5].split("|")
                    if self.parse_list[index_of_last_np_before_als-1][3] == "N":
                        feats[1] = otherfeats[1]
                        feats[2] = otherfeats[2]
                    elif self.parse_list[index_of_last_np_before_als-1][3] == "PRO":
                        feats[1] = otherfeats[3]
                        feats[2] = otherfeats[1]
                    # Hier oben und unten werden wahrscheinlich noch mehr Fälle als "N" und "PRO" benötigt, zum Beispiel für den Fall, dass "jemand" als Adjektiv geparst wird.
                else:
                    # Suche die erste Nominalphrase nach dem Substantiv ohne Numerus (da sich die als-Konstruktion jetzt höchstwahrscheinlich darauf bezieht) und
                    # kopiere den Numerus (aber nicht den Kasus) von dieser Nominalphrase auf das Substantiv ohne Numerus:
                    index_of_first_np_after_als_construct = self.find_first_np_after_index(pos+1)
                    print("index_of_first_np_after_als_construct:", index_of_first_np_after_als_construct)
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
        for i in range(als_index+1,len(self.parse_list)+1):
            if i in self.nounphrases:
                return i
        return 0


    # This function neutralizes the word that has been selected. Then, all dependent words in the sentence are neutralized.
    def neutralize_nounphrase(self, pos:int, selected_components):
        feats = self.parse_list[pos][5].split("|")
        if len(feats) == 1:
            feats.append("_")
            feats.append("_")
        plural = True

        # Determine whether the noun phrase has an article:
        has_article = False
        for child in self.nounphrases.get(pos+1):
            if self.parse_list[child-1][3] == "ART":
                has_article = True
                break

        # Neutralize a possessive pronoun
        if self.parse_list[pos][4] == "PPOSAT" and self.parse_list[pos][6] == "0":
            if feats[2] == "Sg" or feats[2] == "_":
                plural = False
            self.parse_list[pos][-2] = Lexicon.neutralize_possesive_pronoun(pos,selected_components,self.nounlist,feats)
        # Neutralize a possessive article
        elif self.parse_list[pos][4] == "PPOSAT":
            self.parse_list[pos][-2] = Lexicon.neutralize_possesive_article(self.parse_list[pos])
            # Here we additionally need to modify the input possessive pronoun, so that the output is correct when this pronoun needs to be modified further due to the noun it modifies being put into the inklusivum.
            self.parse_list[pos][1] = Lexicon.neutralize_possesive_article(self.parse_list[pos])
        # Neutralize a Noun
        elif self.parse_list[pos][3] == "N":
            if feats[2] == "_":
                print("Noun without number:")
                print(self.parse_list[pos][1])
                print(pos)
                print(feats)
                self.determine_number(pos,feats)
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
            print("about to neutralize noun")
            print(self.parse_list[pos])
            print(pos)
            print(selected_components)
            print(self.nounlist)
            self.parse_list[pos][-2], head_selected, person = Lexicon.make_neutralized_noun(pos,selected_components,self.nounlist,feats,has_article)
            print(self.parse_list[pos][-2])
            # The following line prevents articles of composite nouns with a person noun in non-final position from being neutralized.
            if not head_selected:
                plural = True
            # If word ends in -mann or -frau and is neutralized to -person, make dependent words feminine.
            if person:
                feats = self.parse_list[pos][5].split("|")
                if feats[0] == "Masc" and feats[2] != "Pl":
                    for child in self.nounphrases.get(pos+1):
                        self.feminize_word(child-1, has_article)
        # Neutralized attributing relative pronoun
        elif self.parse_list[pos][4] == "PRELAT":
            self.parse_list[pos][-2] = Lexicon.neutralize_attributing_relative_pronoun(self.parse_list[pos])
        elif re.match(r"(J|j)emand(e?)s" , self.parse_list[pos][1]):
                self.parse_list[pos][-2] = Lexicon.neutralize_pos_jemand(self.parse_list[pos])
        #Neutralize everything else
        else:
            if feats[2] == "Sg" or feats[2] == "_":
                plural = False
            self.parse_list[pos][-2] = Lexicon.neutralize_word(self.parse_list[pos],has_article)
        # Neutralize the remaining words in the nounphrase:
        if not plural or self.parse_list[pos][2].endswith("jenige"):
            print("about to neutralize dependent words")
            for child in self.nounphrases.get(pos+1):
                article_pos = min(self.nounphrases.get(pos+1))
                self.neutralize_word(child-1, has_article, article_pos)


    # Recognizes noun phrases that refer to people and generates the html form, with checkboxes next to recognized noun phrases. 
    # [word_index_from_1, position_of_noun_in_composite_noun, original, neutralized, suffix, noun_type, capitalized, head_identified_as_person_noun]
    def get_marking_form(self, sentence_number) -> str:
        noun_pair_positions = []
        noun_pair_indices = {}
        # Finde Doppelnennungen wie "Bürgerinnen und Bürger":
        for pos, word_parse in enumerate(self.parse_list):
            if word_parse[1] == "und" or word_parse[1] == "oder":
                # Schaue, ob das Wort davor ein feminines Personensubstantiv ist:
                for j, line in enumerate(Lexicon.FEMALE_NOUNS):
                    if line == self.parse_list[pos-1][2]:
                        # Schaue, ob das Wort danach das entsprechende maskuline Personensubstantiv ist:
                        if self.parse_list[pos+1][2] == Lexicon.MALE_NOUNS[j]:
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            # Wenn das maskuline Substantiv auf "ern" endet und nicht "Bauern" ist, dann steht die Konjunktion (und damit das feminine Substantiv) im Dativ:
                            if self.parse_list[pos+1][1].endswith("ern") and not self.parse_list[pos+1][1] == "Bauern":
                                feats = self.parse_list[pos-1][5].split("|")
                                feats[1] = "Dat"
                                self.parse_list[pos-1][5] = "|".join(feats)
                            break
                # Schaue, ob das Wort davor ein maskulines Personensubstantiv ist:
                for j, line in enumerate(Lexicon.MALE_NOUNS):
                    if line == self.parse_list[pos-1][2]:
                        # Schaue, ob das Wort danach das entsprechende feminine Personensubstantiv ist:
                        if self.parse_list[pos+1][2] == Lexicon.FEMALE_NOUNS[j]:
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            # Wenn das maskuline Substantiv auf "ern" endet und nicht "Bauern" ist, dann steht die Konjunktion (und damit das feminine Substantiv) im Dativ:
                            if self.parse_list[pos-1][1].endswith("ern") and not self.parse_list[pos-1][1] == "Bauern":
                                feats = self.parse_list[pos+1][5].split("|")
                                feats[1] = "Dat"
                                self.parse_list[pos+1][5] = "|".join(feats)
                            break
        nouns = ""
        for pos, word_parse in enumerate(self.parse_list):
            # Wenn pos die Position einer Doppelnennung ist, dann mache die gesamte Doppelnennung markierbar:
            if pos in noun_pair_positions:
                self.find_nounphrase(word_parse)
                input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{1}" name="{sentence_number}|{word_parse[0]}|{1}" value="select"><label for="{sentence_number}|{word_parse[0]}|{1}">{"<u>" + word_parse[-2] + word_parse[-1] + self.parse_list[pos+1][-2] + self.parse_list[pos+1][-1] + self.parse_list[pos+2][-2] + "</u>"}</label></div>{self.parse_list[pos+2][-1]}"""
                nouns += input_form
                self.parse_list[pos][-1] = ""
                self.parse_list[pos+1][-2] = ""
                self.parse_list[pos+1][-1] = ""
                self.parse_list[pos+2][-2] = ""
                self.nounlist.extend([[int(word_parse[0]), 0, "", "", "", "prefix", False, False], [int(word_parse[0]), 0, word_parse[1], noun_pair_indices[pos], "", "standard", True, True]])
            elif pos-1 in noun_pair_positions:
                continue
            elif pos-2 in noun_pair_positions:
                continue
            else:
                # Determine whether pos depends on some noun phrase:
                dependent = False
                for key in self.nounphrases:
                    if pos+1 in self.nounphrases[key]:
                        dependent = True
                        break
                # Case: Possessive pronoun
                match = re.match(r"((S|s)ein)|((I|i)hr)", word_parse[1])
                if word_parse[4] == "PPOSAT" and word_parse[6] == "0" and match:
                    self.find_nounphrase(word_parse)
                    base = match.group(0)
                    ending = word_parse[1][len(base):]
                    capitalized = word_parse[1][0].isupper()
                    # Since ParZu does not identify the neuter form of possessive pronouns as such, we identify them by the ending "es":
                    if word_parse[1].endswith("es"):
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-3}" name="{sentence_number}|{word_parse[0]}|{-3}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-3}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                        nouns += input_form
                        self.nounlist.extend([[int(word_parse[0]), 0, base, "ens", "", "possessive_pronoun_base", capitalized, False], [int(word_parse[0]), len(base), ending, ending, "", "possessive_pronoun_ending", False, False]])
                    else:
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-3}" name="{sentence_number}|{word_parse[0]}|{-3}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-3}">{"<u>" + base + "</u>"}</label></div>"""
                        nouns += input_form
                        if len(ending) > 0:
                            input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-4}" name="{sentence_number}|{word_parse[0]}|{-4}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-4}">{"<u>" + ending + "</u>"}</label></div>"""
                            nouns += input_form
                        nouns += word_parse[-1]
                        self.nounlist.extend([[int(word_parse[0]), 0, base, "ens", "", "possessive_pronoun_base", capitalized, False], [int(word_parse[0]), len(base), ending, "", "", "possessive_pronoun_ending", False, False]])
                elif word_parse[4] == "PPOSAT" and word_parse[6] == "0":
                    # Since ParZu does not identify the neuter form of possessive pronouns as such, we identify them by the ending "es":
                    if word_parse[1].endswith("es"):
                        nouns += word_parse[-2]
                        nouns += word_parse[-1]
                    else:
                        self.find_nounphrase(word_parse)
                        match = re.match(r"(M|m|D|d)ein|(U|u)nse?r|(E|e)ue?r", word_parse[1])
                        if match:
                            base = match.group(0)
                            ending = word_parse[1][len(base):]
                        else:
                            base = word_parse[1][:len(word_parse[2]-1)]
                            ending = word_parse[1][len(word_parse[2]-1):]
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-5}" name="{sentence_number}|{word_parse[0]}|{-5}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-5}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                        nouns += input_form
                        self.nounlist.extend([[int(word_parse[0]), 0, base, base, "", "possessive_pronoun_base", False, False], [int(word_parse[0]), len(base), ending, "", "", "possessive_pronoun_ending", False, False]])

                # Case: Possessive article
                elif word_parse[4] == "PPOSAT" and not re.match(r"(M|m|D|d)ein|(U|u)nse?r|(E|e)ue?r", word_parse[1]):
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{-2}" name="{sentence_number}|{word_parse[0]}|{-2}" value="select"><label for="{sentence_number}|{word_parse[0]}|{-2}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                    nouns += input_form

                # Case: Noun
                elif word_parse[3] == "N":
                    self.find_nounphrase(word_parse)
                    feats = self.parse_list[pos][5].split("|")
                    if len(feats) == 1:
                        feats = ["_","_","_"]
                    # The following hack is needed, because ParZu often misinterprets "Pole" as "Pol":
                    if word_parse[2] == "Pol" and (word_parse[1] == "Pole" or word_parse[1] == "Polen"):
                        word_parse[2] = "Pole"
                        feats[0] = "Masc"
                    if feats[2] == "_":
                        self.determine_number(pos,feats)
                    print("about to check noun")
                    head_identified, prefix, list = Lexicon.check_noun(word_parse,feats)
                    print(list)
                    if list == []:
                        nouns += word_parse[-2]
                        nouns += word_parse[-1]
                    elif len(list) == 1 and list[0][3] == "":
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{1}" name="{sentence_number}|{word_parse[0]}|{1}" value="select"><label for="{sentence_number}|{word_parse[0]}|{1}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                        nouns += input_form
                    else:
                        input_form = Marking_Tool.create_input_form(self, sentence_number, word_parse, list)
                        nouns += prefix + input_form + word_parse[-1]
                    for i in range(len(list)):
                        list[i].insert(0, int(word_parse[0]))
                        list[i].append(False)
                    if list != []:
                        list[-1][-1] = head_identified
                    list.insert(0, [int(word_parse[0]), 0, "", "", prefix, "prefix", False, False])
                    self.nounlist.extend(list)
                # Case: Pronoun
                elif word_parse[3] == "PRO" and (word_parse[5][0] == "3" or word_parse[4] == "PIS" or word_parse[4] == "PDS") and not word_parse[4] == "PRF" and ("Neut" not in word_parse[5])  and ("Pl" not in word_parse[5]) and not word_parse[2] == "viel" and not word_parse[2] == "alle" and not word_parse[2] == "etwas" and not word_parse[2] == "was" and not word_parse[2] == "sowas" and not word_parse[2] == "nichts" and not word_parse[2] == "einige" and not (word_parse[2].startswith("andere") and self.parse_list[pos-1][2] == "alle") and not (word_parse[1] == "anderem" and self.parse_list[pos-1][2] == "unter") and not word_parse[2] == "a."  and not (word_parse[2].startswith("andere") and self.parse_list[pos-1][2] == "alle"): # The last three cases are there to avoid the second part of "alles andere", "unter anderem" and "u. a." from being markable.
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                    nouns += input_form
                # Case: welche
                elif word_parse[3] == "PRO" and word_parse[4] == "PWS" and word_parse[2] == "welche":
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
                elif word_parse[4] == "PRELS" and not dependent:
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                    nouns += input_form
                elif word_parse[3] == "ART" and word_parse[6] == "0":
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                    nouns += input_form
                else:
                    nouns += word_parse[-2]
                    nouns += word_parse[-1]
        print(self.nounphrases)
        return nouns
    
    # Generates the html form for a single (possibly compund) noun, with checkboxes next to the components.
    def create_input_form(self, sentence_number, word_parse, list):
        print("list")
        print(list)
        input_form = ""
        for i in range(len(list)):
            input_form += f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{i+1}" name="{sentence_number}|{word_parse[0]}|{i+1}" value="select"><label for="{sentence_number}|{word_parse[0]}|{i+1}">{"<u>" + list[i][1] + "</u>"}</label></div>{list[i][3]}"""
            if i == len(list)-1 and list[i][3] == "":
                input_form += word_parse[-1]
        return input_form

    # This function takes the parse list and the original input text and finds the realizations of the words in the input text.
    def find_realizations(self, input_text: str):
        position_after_preposition = False
        for word in self.parse_list:
            if position_after_preposition == True and word[1].startswith("d") and len(word[1]) == 3:
                pattern = "(" + re.escape(word[1]) + "|" + re.escape(word[1][2]) + ")"
            elif word[1].lower() == "in":
                pattern = "(in|i(?!n))"
            elif word[1].lower() == "an":
                pattern = "(an|a(?!n))"
            elif word[1].lower() == "von":
                pattern = "(von|vo(?!n))"
            elif word[1] == '"':
                pattern = '("|„|“|”)'
            else:
                pattern = re.escape(word[1])
            match = re.search("^" + pattern, input_text, re.IGNORECASE)
            if match:
                realization = match.group(0)
                remaining_text = input_text[match.end():]
                whitespace_pattern = "^( |\n|\r|\t| )*"
                whitespace_match = re.search(whitespace_pattern,remaining_text)
                input_text = remaining_text[whitespace_match.end():]
                white_realization = whitespace_match.group(0)
            else:
                print(input_text)
                raise Exception("The word \"" + pattern + "\" could not be found in the input text, even though it was expected according to the parse list")
            #realization, input_text = self.find_prefix_regex(pattern,input_text)
            word.append(realization)
            word.append(white_realization)
            if word[1] in ["bei","Bei","zu","Zu","in","In","von","Von","vor","Vor","an","An","auf","Auf","für","Für"]:
                position_after_preposition = True
            else:
                position_after_preposition = False
        return input_text


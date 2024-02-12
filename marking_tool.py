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
    def find_children(self, pos: str, preposition: bool):
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
                # In relative sentences that depend on the noun phrase, we want to include the relative pronoun, but nothing else.
                if word_parse[4] == "PRELS":
                    break
            #else:
            #    children.extend(self.find_dessen(word_parse[0]))
        # If the word is a noun followed by a comma followed by an independent der/die/das, the independent der/die/das should be added to childen
        if len(self.parse_list) >= int(pos)+2 and self.parse_list[int(pos)-1][3] == "N" and self.parse_list[int(pos)][1] == "," and self.parse_list[int(pos)+1][2] in ["der","die","das"] and self.parse_list[int(pos)+1][6] == "0":
            children.append(int(self.parse_list[int(pos)+1][0]))
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
                if word_parse[2].endswith("e"):
                    word_parse[2] = word_parse[2][:-1]
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
    def feminize_word(self, pos:int, has_article:bool, article_pos:int):
        word_parse = self.parse_list[pos]
        if word_parse[3] == "ADJA":
            # For adjectives, as the inklusivum differs from standard grammar regarding weak/strong
            # flexion, the parent has to included when neutralizing the word.
            self.parse_list[pos][-2] = Lexicon_Fem.feminize_adjectives(word_parse, has_article)
        elif word_parse[4] == "PIDAT" and pos != article_pos-1:
            # This case covers morphologically adjectival determiners like the word "jeden" in "einem jeden Mann".
            # Since the feature list of a PIDAT determiner has a differnt structure than that of an
            # adjective, we need to first adapt its structure:
            word_parse[5] = "POS|" + word_parse[5] + "|_|"
            if word_parse[2] != "alle":
                if word_parse[2].endswith("e"):
                    word_parse[2] = word_parse[2][:-1]
                self.parse_list[pos][-2] = Lexicon_Fem.feminize_adjectives(word_parse, has_article)
        else:
            feminized_word = Lexicon_Fem.feminize_word(self.parse_list[pos],has_article)
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
            article = False
            for child in self.nounphrases.get(pos+1):
                if self.parse_list[child-1][3] == "ART":
                    article = True
                    article_position = child-1
                    break
            if article:
                if self.parse_list[article_position][2] == "alle":
                        feats[2] = "Pl"
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
                # In order not to neutralize the dependent words later, we set "plural" to True.
                plural = True
                feats = self.parse_list[pos][5].split("|")
                if (feats[0] == "Masc" or feats[0] == "_") and feats[2] != "Pl":
                    print("about to feminize dependent words", self.parse_list[pos][1], self.nounphrases.get(pos+1))
                    for child in self.nounphrases.get(pos+1):
                        article_pos = min(self.nounphrases.get(pos+1))
                        self.feminize_word(child-1, has_article, article_pos)
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
            print("about to neutralize dependent words", self.parse_list[pos][1], self.nounphrases.get(pos+1))
            for child in self.nounphrases.get(pos+1):
                article_pos = min(self.nounphrases.get(pos+1))
                self.neutralize_word(child-1, has_article, article_pos)


    def find_verb_dependencies(self, pos:int, recognized_verb_dependencies:list):
        verb_dependencies = []
        for word_parse in self.parse_list:
            if not int(word_parse[0]) in verb_dependencies and not int(word_parse[0]) in recognized_verb_dependencies and (int(word_parse[6]) == pos or word_parse[3] == "ADV" or word_parse[3] == "PREP"):
                verb_dependencies.append(int(word_parse[0]))
                recognized_verb_dependencies.append(int(word_parse[0]))
                children = self.find_verb_dependencies(int(word_parse[0]),recognized_verb_dependencies)
                verb_dependencies.extend(children)
                recognized_verb_dependencies.extend(children)
        return verb_dependencies

    def search_genitive_pronoun(self, pos:int):
        verb_dependencies = self.find_verb_dependencies(pos+1,[])
        print("verb_dependencies:",verb_dependencies)
        searching_before_verb = True
        searching_after_verb = True
        i = 1
        while searching_before_verb or searching_after_verb:
            print("i:",i)
            print("searching_before_verb:",searching_before_verb)
            print("searching_after_verb:",searching_after_verb)
            if searching_before_verb:
                if pos-i < 0:
                    print("reached beginning of sentence")
                    searching_before_verb = False
                elif self.parse_list[pos-i][1] == "seiner" and self.parse_list[pos-i][6] == "0":
                    print("found seiner before verb")
                    self.parse_list[pos-i][2] = "er"
                    self.parse_list[pos-i][3] = "PRO"
                    self.parse_list[pos-i][4] = "PPER"
                    self.parse_list[pos-i][5] = "3|Sg|Masc|Gen"
                    self.parse_list[pos-i][6] = str(pos+1)
                    self.parse_list[pos-i][7] = "objg"
                    break
                elif self.parse_list[pos-i][1] == "ihrer" and self.parse_list[pos-i][6] == "0":
                    print("found ihrer before verb")
                    self.parse_list[pos-i][2] = "sie"
                    self.parse_list[pos-i][3] = "PRO"
                    self.parse_list[pos-i][4] = "PPER"
                    self.parse_list[pos-i][5] = "3|Sg|Fem|Gen"
                    self.parse_list[pos-i][6] = str(pos+1)
                    self.parse_list[pos-i][7] = "objg"
                    break
                elif not pos-i+1 in verb_dependencies:
                    print("stopped searching before verb")
                    searching_before_verb = False
            if searching_after_verb:
                if len(self.parse_list) <= pos+i:
                    print("reached end of sentence")
                    searching_after_verb = False
                elif self.parse_list[pos+i][1] == "seiner" and self.parse_list[pos+i][6] == "0":
                    print("found seiner after verb")
                    self.parse_list[pos+i][2] = "er"
                    self.parse_list[pos+i][3] = "PRO"
                    self.parse_list[pos+i][4] = "PPER"
                    self.parse_list[pos+i][5] = "3|Sg|Masc|Gen"
                    self.parse_list[pos+i][6] = str(pos+1)
                    self.parse_list[pos+i][7] = "objg"
                    break
                elif self.parse_list[pos+i][1] == "ihrer" and self.parse_list[pos+i][6] == "0":
                    print("found ihrer after verb")
                    self.parse_list[pos+i][2] = "sie"
                    self.parse_list[pos+i][3] = "PRO"
                    self.parse_list[pos+i][4] = "PPER"
                    self.parse_list[pos+i][5] = "3|Sg|Fem|Gen"
                    self.parse_list[pos+i][6] = str(pos+1)
                    self.parse_list[pos+i][7] = "objg"
                    break
                elif not pos+i+1 in verb_dependencies:
                    print("stopped searching after verb")
                    searching_after_verb = False
            i += 1

    # Recognizes noun phrases that refer to people and generates the html form, with checkboxes next to recognized noun phrases. 
    # [word_index_from_1, position_of_noun_in_composite_noun, original, neutralized, suffix, noun_type, capitalized, head_identified_as_person_noun]
    def get_marking_form(self, sentence_number) -> str:
        # Suche pronominale Genitivobjekte:
        # Suche Verben, die sinnvollerweise eine Person als Genitivobjekt haben können:
        for pos, word_parse in enumerate(self.parse_list):
            if word_parse[3] == "V" and word_parse[2] in ["gedenken","annehmen","bemächtigen","erinnern","bedienen","erfreuen","entledigen","rühmen","schämen","bedürfen","entbehren"]:
                self.search_genitive_pronoun(pos)
            if word_parse[3] == "V" and word_parse[2] == "nehmen":
                # Check if "an" appears as a separated verb particle in the sentence:
                an = False
                for word_parse in self.parse_list:
                    if word_parse[1] == "an" and word_parse[3] == "PTKVZ":
                        an = True
                        break
                if an:
                    self.search_genitive_pronoun(pos)

        # Finde Doppelnennungen wie "Bürgerinnen und Bürger":
        noun_pair_positions = []
        noun_pair_indices = {}
        noun_pair_types = {}
        noun_pair_prefixes = {}
        for pos, word_parse in enumerate(self.parse_list):
            if word_parse[1] == "und" or word_parse[1] == "oder":
                # Schaue, ob das Wort davor ein feminines Personensubstantiv ist:
                for j, line in enumerate(Lexicon.FEMALE_NOUNS):
                    if self.parse_list[pos-1][2] == line:
                        # Schaue, ob das Wort danach das entsprechende maskuline Personensubstantiv ist:
                        if self.parse_list[pos+1][2] == Lexicon.MALE_NOUNS[j]:
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "standard"
                            noun_pair_prefixes[pos-1] = ""
                            # Wenn das maskuline Substantiv auf "ern" endet und nicht "Bauern" ist, dann steht die Konjunktion (und damit das feminine Substantiv) im Dativ:
                            if self.parse_list[pos+1][1].endswith("ern") and not self.parse_list[pos+1][1] == "Bauern":
                                feats = self.parse_list[pos-1][5].split("|")
                                feats[1] = "Dat"
                                self.parse_list[pos-1][5] = "|".join(feats)
                            break
                # Schaue, ob das Wort davor ein maskulines Personensubstantiv ist:
                for j, line in enumerate(Lexicon.MALE_NOUNS):
                    if self.parse_list[pos-1][2] == line:
                        # Schaue, ob das Wort danach das entsprechende feminine Personensubstantiv ist:
                        if self.parse_list[pos+1][2] == Lexicon.FEMALE_NOUNS[j]:
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "standard"
                            noun_pair_prefixes[pos-1] = ""
                            # Wenn das maskuline Substantiv auf "ern" endet und nicht "Bauern" ist, dann steht die Konjunktion (und damit das feminine Substantiv) im Dativ:
                            if self.parse_list[pos-1][1].endswith("ern") and not self.parse_list[pos-1][1] == "Bauern":
                                feats = self.parse_list[pos+1][5].split("|")
                                feats[1] = "Dat"
                                self.parse_list[pos+1][5] = "|".join(feats)
                            break
                # Schaue, ob das Wort davor ein Wort ist, das durch ein Neologismus ersetzt werden kann:
                for j, neologism in enumerate(Lexicon.NEOLOGISMS):
                    neologism = "(" + neologism + ")$"
                    if re.match(neologism.lower(), self.parse_list[pos-1][2].lower()):
                        # Schaue, ob das Wort danach das entsprechende Wort ist:
                        if re.match(neologism.lower(), self.parse_list[pos+1][2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "neologism"
                            noun_pair_prefixes[pos-1] = ""
                            break
                # Schaue, ob das Wort davor ein Wort ist, das auf "mann", "frau", "herr" oder "dame" endet:
                person_pattern = r"(.*)((m(a|ä)nn(er)?)|(frau(en)?)|herr|dame)$"
                match = re.match(person_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_person_pattern = match.group(1) + r"((m(a|ä)nn(er)?)|(frau(en)?)|herr|dame)$"
                    if re.match(same_person_pattern, self.parse_list[pos+1][2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = 0
                        noun_pair_types[pos-1] = "person"
                        noun_pair_prefixes[pos-1] = match.group(1).capitalize()
                        break
                # Schaue, ob das Wort davor auf "beamt..." endet:
                beamt_pattern = r"(.*)(beamt(in(nen)?|e(r|n|m)?))$"
                match = re.match(beamt_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_beamt_pattern = match.group(1) + r"(beamt(in(nen)?|e(r|n|m)?))$"
                    if re.match(same_beamt_pattern, self.parse_list[pos+1][2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = 0
                        noun_pair_types[pos-1] = "beamtey"
                        noun_pair_prefixes[pos-1] = match.group(1).capitalize()
                        break
                # Schaue, ob das Wort davor ein Romanismus ist:
                for j, romanism in enumerate(Lexicon.ROMAN_NOUNS):
                    romanism = "(" + romanism + ")$"
                    if re.match(romanism.lower(), self.parse_list[pos-1][2].lower()):
                        # Schaue, ob das Wort danach der entsprechende Romanismus ist:
                        if re.match(romanism.lower(), self.parse_list[pos+1][2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "romanism"
                            noun_pair_prefixes[pos-1] = ""
                            break
                # Schaue, ob das Wort davor ein irreguläres Substantiv ist:
                for j, irregular_noun in enumerate(Lexicon.IRREGULAR_NOUNS):
                    irregular_noun = "(" + irregular_noun + ")$"
                    if re.match(irregular_noun.lower(), self.parse_list[pos-1][2].lower()):
                        # Schaue, ob das Wort danach das entsprechende irreguläre Substantiv ist:
                        if re.match(irregular_noun.lower(), self.parse_list[pos+1][2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = j
                            noun_pair_types[pos-1] = "irregular"
                            noun_pair_prefixes[pos-1] = ""
                            break
                # Schaue, ob das Wort davor ein substantiviertes Adjektiv ist:
                for j, subadj in enumerate(Lexicon.SUBST_ADJ):
                    subadj = "(" + subadj + ")(r|n)?$"
                    match = re.match(subadj.lower(), self.parse_list[pos-1][2].lower())
                    if match:
                        # Schaue, ob das Wort danach das entsprechende Wort ist:
                        same_subadj = match.group(1) + r"(r|n)?$"
                        if re.match(same_subadj.lower(), self.parse_list[pos+1][2].lower()):
                            # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                            noun_pair_positions.append(pos-1)
                            noun_pair_indices[pos-1] = match.group(1).capitalize()
                            noun_pair_types[pos-1] = "substantivized adjective"
                            noun_pair_prefixes[pos-1] = ""
                            break
                # Schaue, ob das Wort davor ein auf "sprachige" endendes substantiviertes Adjektiv ist:
                sprachige_pattern = r"(..+sprachige)(r|n|m|s)?$"
                match = re.match(sprachige_pattern, self.parse_list[pos-1][2].lower())
                if match:
                    # Schaue, ob das Wort danach das entsprechende Wort ist:
                    same_sprachige_pattern = match.group(1) + r"(r|n|m|s)?$"
                    if re.match(same_sprachige_pattern, self.parse_list[pos+1][2].lower()):
                        # Wenn ja, dann füge die Position des erstens Wortes in die Liste der Doppelnennungen ein, und speichere den Index des ersten Wortes in einem Dictionary:
                        noun_pair_positions.append(pos-1)
                        noun_pair_indices[pos-1] = match.group(1).capitalize()
                        noun_pair_types[pos-1] = "substantivized adjective"
                        noun_pair_prefixes[pos-1] = ""
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
                prefix = noun_pair_prefixes[pos]
                if prefix == "":
                    is_capitalized = True
                else:
                    is_capitalized = False
                self.nounlist.extend([[int(word_parse[0]), 0, "", "", prefix, "prefix", True, False], [int(word_parse[0]), 0, word_parse[1], noun_pair_indices[pos], "", noun_pair_types[pos], is_capitalized, True]])
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
                # Here we also need to consider capitalized adjectives that do not depend on a noun:
                elif word_parse[3] == "N" or (word_parse[3] == "ADJA" and word_parse[1][0].isupper() and not self.parse_list[int(word_parse[6])-1][3] == "N"):
                    self.find_nounphrase(word_parse)
                    feats = self.parse_list[pos][5].split("|")
                    if len(feats) == 1:
                        feats = ["_","_","_"]
                    if feats[2] == "_":
                        self.determine_number(pos,feats)
                    # The following hack is needed, because ParZu often misinterprets "Pole" as "Pol":
                    if word_parse[2] == "Pol" and (word_parse[1] == "Pole" or word_parse[1] == "Polen"):
                        word_parse[2] = "Pole"
                        word_parse[4] = "N"
                        feats[0] = "Masc"
                    # The following is needed, because ParZu often misinterprets plural "Ungarn" as the country, not the people:
                    if word_parse[1] == "Ungarn" and feats[2] == "Pl":
                        word_parse[2] = "Ungar"
                        word_parse[4] = "N"
                    # Substantivized adjectives that ParZu recognized as adjectives often have a wrong word_parse[2], so we need to correct it:
                    if word_parse[3] == "ADJA":
                        word_parse[2] = word_parse[1]
                    # The following looks for articles that are relevant for proper nouns, i.e. masculine and feminine article in the singular:
                    has_article = False
                    for other_word_parse in self.parse_list:
                        if other_word_parse[6] == word_parse[0] and other_word_parse[3] == "ART":
                            article_feats = other_word_parse[5].split("|")
                            if article_feats[-1] != "Pl" and (article_feats[-3] == "Masc" or article_feats[-3] == "Fem"):
                                has_article = True
                    print("about to check noun:", word_parse)
                    head_identified, prefix, list = Lexicon.check_noun(word_parse,feats,has_article)
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
                elif word_parse[3] == "PRO" and (word_parse[5][0] == "3" or word_parse[4] == "PIS" or word_parse[4] == "PDS") and not word_parse[4] == "PRF" and ("Neut" not in word_parse[5])  and ("Pl" not in word_parse[5]) and not word_parse[2] == "viel" and not word_parse[2] == "mehr" and not word_parse[2] == "alle" and not word_parse[2] == "etwas" and not word_parse[2] == "was" and not word_parse[2] == "sowas" and not word_parse[2] == "nichts" and not word_parse[1].startswith("das") and not word_parse[2] == "einige" and not (word_parse[2].startswith("andere") and self.parse_list[pos-1][2] == "alle") and not (word_parse[1] == "anderem" and self.parse_list[pos-1][2] == "unter") and not word_parse[2] == "a."  and not (word_parse[2].startswith("andere") and self.parse_list[pos-1][2] == "alle"): # The last three cases are there to avoid the second part of "alles andere", "unter anderem" and "u. a." from being markable.
                    self.find_nounphrase(word_parse)
                    input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                    nouns += input_form
                # Case: Relative pronoun dependent on a proper noun
                elif word_parse[4] == "PRELS" and ((self.parse_list[pos-1][1] == "," and self.parse_list[pos-2][4] == "NE") or (self.parse_list[pos-2][1] == "," and self.parse_list[pos-3][4] == "NE")) and not word_parse[5].startswith("Neut") and not word_parse[5].endswith("Pl"):
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
                    # Search if the article is part of a noun phrase:
                    article_dependent = False
                    for key in self.nounphrases:
                        if pos+1 in self.nounphrases[key]:
                            article_dependent = True
                            break
                    if not article_dependent:
                        self.find_nounphrase(word_parse)
                        input_form = f"""<div class="checkbox-container"><input type="checkbox" id="{sentence_number}|{word_parse[0]}|{0}" name="{sentence_number}|{word_parse[0]}|{0}" value="select"><label for="{sentence_number}|{word_parse[0]}|{0}">{"<u>" + word_parse[-2] + "</u>"}</label></div>{word_parse[-1]}"""
                        nouns += input_form
                    else:
                        nouns += word_parse[-2]
                        nouns += word_parse[-1]
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


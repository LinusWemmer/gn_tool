from lexicon import Lexicon

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

    # Returns the sentence underlying the pars.
    def get_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            print(word_parse)
            sentence += word_parse[1] + " "
        return sentence

    # Finds all "nounphrases" of the sentence and stores them in a dict.
    # Returns True if the word is a role noun, otherwise false.
    def find_nounphrase(self, word_parse):
        if Lexicon.check_role_noun(word_parse[2], word_parse[5][0]):
            self.nounphrases[int(word_parse[0])] = self.find_children(word_parse[0])
            print(self.nounphrases)
            return True
        return False
    
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
        return children
    
    def get_nounphrase(self, pos):
        return self.nounphrases.get(pos)
    
    def neutralize_word(self, pos:int):
        print(self.parse_list[pos-1])
        self.parse_list[pos-1][1] = Lexicon.neutralize_word(self.parse_list[pos-1])
        
    
    def neutralize_nounphrase(self, pos:int):
        feats = self.parse_list[pos][5].split("|")
        print(feats)
        self.parse_list[pos][1] = Lexicon.neutralize_noun(self.parse_list[pos][2], feats)
        print(self.nounphrases)
        for child in self.nounphrases.get(pos+1):
            self.neutralize_word(child)

    # Generates the html form, with noun phrases marked 
    def get_marking_form(self, sentence_number) -> str:
        #self.find_nounphrases()
        nouns = ""
        for word_parse in self.parse_list:
            #TODO: PPOSAT; PRONOUNS
            if word_parse[3] == "N" and self.find_nounphrase(word_parse):
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}" name="{sentence_number}|{word_parse[0]}" value="select">
                <label for="noun{sentence_number }|{word_parse[0]}">{"<u>" + word_parse[1] + "</u>"}</label> """
                nouns += input_form
            elif word_parse[3] == "$.":
                nouns = nouns[:-1] + word_parse[1] + " "
            else:
               nouns += word_parse[1] + " "
        return nouns
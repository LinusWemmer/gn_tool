class Marking_tool:
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

    def get_sentence(self) -> str:
        sentence = ""
        for word_parse in self.parse_list:
            sentence += word_parse[1] + " "
        return sentence

    def find_nounphrase(self):
        for word_parse in self.parse_list:
            if word_parse[3] == "N":
                self.nounphrases[word_parse[0]] = self.find_children(word_parse[0])
                print(self.nounphrases)
    
    def get_nounphrase(self, pos):
        return self.nounphrases.get(pos)
    
    def neutralize_word(self, pos):
        self.parse_list[int(pos)-1][1] += "e"
    
    def neutralize_nounphrase(self, pos):
        #if self.parse_list[pos][5].... 
        self.parse_list[int(pos)-1][1] += "e"
        for child in self.nounphrases.get(pos):
            self.neutralize_word(child)


    def find_children(self, pos: int):
        children = []
        for word_parse in self.parse_list:
            if word_parse[6] == pos:
                #This is recursive, maybe to expensive.
                #Can it even happen in german that a noun phrase is that long/recursive?
                children.append(word_parse[0])
                children.extend(self.find_children(word_parse[0]))
        return children
    
    def get_marking_form(self, sentence_number) -> str:
        nouns = ""
        for word_parse in self.parse_list:
            if word_parse[3] == "N":
                input_form = f"""<input type="checkbox" id="{sentence_number}|{word_parse[0]}" name="{sentence_number}|{word_parse[0]}" value="select"> 
                <label for="noun{sentence_number }|{word_parse[0]}">{"<mark>" + word_parse[1] + "</mark>"}</label> """
                nouns += input_form
            elif word_parse[3] == "$.":
                nouns = nouns[:-1] + word_parse[1]
            else:
               nouns += word_parse[1] + " "
        return nouns

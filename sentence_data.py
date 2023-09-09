from marking_tool import Marking_Tool

class Sentence_Data:
    def __init__(self) -> None:
        self.marking_tools = {}
        self.split_words = {}

    def add_marking_tool(self, sentence_number: int, marking_tool: Marking_Tool):
        self.marking_tools[sentence_number] = marking_tool

    def get_marking_tool(self, sentence_number: int) -> Marking_Tool:
        return self.marking_tools.get(sentence_number)
    
    def get_text(self) -> str:
        text = ""
        print(self.split_words)
        for sentence_number, marking_tool in self.marking_tools.items():
            if sentence_number in self.split_words.keys():
                text += marking_tool.get_sentence(self.split_words[sentence_number])
            else:
                text += marking_tool.get_sentence()
        return text
    
    def get_marking_tools(self):
        return self.marking_tools

    def clear_marking_tools(self):
        self.marking_tools = {}
        self.split_words = {}

    def add_split(self, sentence_nr:int, word:int):
        print(self.split_words)
        if sentence_nr in self.split_words.keys():
            splits = self.split_words[sentence_nr]
            splits.append(word)
            print(splits)
            self.split_words[sentence_nr] = splits
            print(self.split_words)
        else:
            self.split_words[sentence_nr] = [word]
    
    def get_split_words(self):
        return self.split_words

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
        for sentence_number, marking_tool in self.marking_tools.items():
            text += marking_tool.get_sentence()
        return text
    
    def get_marking_tools(self):
        return self.marking_tools

    def clear_marking_tools(self):
        self.marking_tools = {}
        self.split_words = {}

    def add_split(self, sentence:int, word:int):
        if sentence in self.split_words.keys():
            self.split_words[sentence] = self.split_words[sentence].add(word)
        else:
            self.split_words[sentence] = [word]
    
    def get_split_words(self):
        return self.split_words

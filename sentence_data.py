from marking_tool import Marking_Tool

class Sentence_Data:
    def __init__(self) -> None:
        self.marking_tools = {}

    def add_marking_tool(self, sentence_number: int, marking_tool: Marking_Tool):
        self.marking_tools[sentence_number] = marking_tool

    def get_marking_tool(self, sentence_number: int) -> Marking_Tool:
        return self.marking_tools.get(sentence_number)
    
    def get_marking_tools(self):
        return self.marking_tools

    def clear_marking_tools(self):
        self.marking_tools = {}
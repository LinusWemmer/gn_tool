from lexicon import Lexicon
from marking_tool import Marking_Tool
import parzu_class as parzu
import unittest


class Sentence_Test(unittest.TestCase):
    def test_sentences(self):
        ParZu = parzu.Parser(parzu.process_arguments())
        test_sentence_1 = ("Der Lehrer gibt dem Schüler den Stift.", "De Lehrere gibt derm Schülere den Stift.")
        test_sentence_2 = ("Er gibt ihr den Stift.", "En gibt em den Stift.")
        test_sentence_3 = ("Das Buch meines Professors ist interessant.", "Das Buch meiners Professores ist interessant.")
        test_sentence_4 = ("Sein Buch ist interessant.", "Ens Buch ist interessant.")
        test_sentence_5 = ("Auch seine Vorlesungen sind spannend.", "Auch ense Vorlesungen sind spannend.")
        test_sentence_6 = ("Kennst du meine Verlobte Kim?", "Kennst du mein Verlobte Kim?")
        test_sentence_7 = ("Ja, ich kenne sie schon.", "Ja, ich kenne en schon.")
        test_sentence_8 = ("Und kennst du auch ihre Kollegin Andrea?", "Und kennst du auch ens Kollegere Andrea?")
        test_sentence_9 = ("Nein, ich glaub nicht, dass ich sie schon kennengelernt habe.", "Nein, ich glaub nicht, dass ich en schon kennengelernt habe.")
        test_sentence_10 = ("Ich kenne aber schon viele andere Kollegen von Kim.", "Ich kenne aber schon viele andere Kollegerne von Kim.")
        test_sentence_11 = ("Bei uns ist jeder willkommen!", "Bei uns ist jedey willkommen!")
        test_sentences = [test_sentence_1, test_sentence_2, test_sentence_3, test_sentence_4,test_sentence_5, test_sentence_6, test_sentence_7, test_sentence_8, test_sentence_9, test_sentence_10, test_sentence_11]
        test_nounphrases = [((2,34), (5,6)), ((1,0), (3,0)), ((4,43),), ((1,0),), ((2,0),), ((4, -1),), ((5,0),), ((5,0), (6,27)), ((9,0),), ((7,27),), ((4,0),)]
        for i,test in enumerate(test_sentences):
            parse = ParZu.main(test[0])
            words = parse[0].split("\n")
            words = words[:-2]
            marking_tool = Marking_Tool(words)
            for nounphrase in test_nounphrases[i]:
                marking_tool.find_nounphrase(marking_tool.parse_list[nounphrase[0] - 1])
            for nounphrase in test_nounphrases[i]:
                marking_tool.neutralize_nounphrase(nounphrase[0] - 1, nounphrase[1])
            self.assertEqual(marking_tool.get_sentence(), test[1] + " ",f"Text {i} doesn't have correct output.") 


if __name__ == "__main__":
    unittest.main()

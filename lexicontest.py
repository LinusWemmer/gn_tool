from lexicon import Lexicon
from marking_tool import Marking_Tool
import parzu_class as parzu
import unittest


class Sentence_Test(unittest.TestCase):
    def test_sentences(self):
        ParZu = parzu.Parser(parzu.process_arguments())
        test_sentence_1 = ("Der Lehrer gibt dem Schüler den Stift.", "De Lehrere gibt derm Schülere den Stift.", ((2,34), (5,6)))
        test_sentence_2 = ("Er gibt ihr den Stift.", "En gibt em den Stift.", ((1,0), (3,0)))
        test_sentence_3 = ("Das Buch meines Professors ist interessant.", "Das Buch meiners Professores ist interessant.", ((4,43),))
        test_sentence_4 = ("Sein Buch ist interessant.", "Ens Buch ist interessant.", ((1,0),))
        test_sentence_5 = ("Auch seine Vorlesungen sind spannend.", "Auch ense Vorlesungen sind spannend.", ((2,0),))
        test_sentence_6 = ("Kennst du meine Verlobte Kim?", "Kennst du mein Verlobte Kim?", ((4, -1),))
        test_sentence_7 = ("Ja, ich kenne sie schon.", "Ja, ich kenne en schon.", ((5,0),))
        test_sentence_8 = ("Und kennst du auch ihre Kollegin Andrea?", "Und kennst du auch ens Kollegere Andrea?", ((5,0), (6,27)))
        test_sentence_9 = ("Nein, ich glaub nicht, dass ich sie schon kennengelernt habe.", "Nein, ich glaub nicht, dass ich en schon kennengelernt habe.", ((9,0),))
        test_sentence_10 = ("Ich kenne aber schon viele andere Kollegen von Kim.", "Ich kenne aber schon viele andere Kollegerne von Kim.", ((7,27),))
        test_sentence_11 = ("Bei uns ist jeder willkommen!", "Bei uns ist jedey willkommen!", ((4,0),))
        test_sentence_12 = ("Als Vorsitzender hat Kim viel zu tun.", "Als Vorsitzendey hat Kim viel zu tun.", ((2,-1),))
        test_sentence_13 = ("Sein öffentliches Coming-Out als X-gender und asexuell hatte Kamatani in einem Tweet im Jahr 2012.", "Ens öffentliches Coming-Out als X-gender und asexuell hatte Kamatani in einem Tweet im Jahr 2012.",((1,0),))
        test_sentence_14 = ("Ich kenne viele andere Schüler.", "Ich kenne viele andere Schülerne.", ((5,6),))
        test_sentence_15 = ("Wo ist das Hauptgebäude seiner Schule?", "Wo ist das Hauptgebäude enser Schule?", ((5,0),))
        test_sentence_16 = ("Kennst Du seinen Namen?", "Kennst Du ensen Namen?", ((3,0),))
        test_sentence_17 = ("Als Vorsitzender hat Kim viel zu tun.", "Als Vorsitzendey hat Kim viel zu tun.", ((2,-1),))
        test_sentence_18 = ("Sicher kaum einer!", "Sicher kaum einey!", ((3,0),))
        test_sentence_19 = ("Der Schüler, der dort steht, ist nett.", "De Schülere, de dort steht, ist nett.", ((2,6), (4,0)))
        test_sentence_20 = ("Aufgrund ihrer Krankheit wird sie leider nicht dabei sein.", "Aufgrund enser Krankheit wird en leider nicht dabei sein.", ((2,0),(4,0)))
        test_sentence_21 = ("Mein Opa liegt im Krankenhaus.", "Mein Ota liegt im Krankenhaus.", ((1,-3),))
        test_sentences = [test_sentence_1, test_sentence_2, test_sentence_3, test_sentence_4,test_sentence_5, test_sentence_6, test_sentence_7, test_sentence_8, test_sentence_9, test_sentence_10,
                           test_sentence_11, test_sentence_12, test_sentence_13, test_sentence_14, test_sentence_15, test_sentence_16, test_sentence_17, test_sentence_18, test_sentence_19, test_sentence_20]
        for i,test in enumerate(test_sentences):
            print(f"Testing sentence {i + 1}.")
            parse = ParZu.main(test[0])
            words = parse[0].split("\n")
            words = words[:-2]
            marking_tool = Marking_Tool(words)
            for nounphrase in test[2]:
                marking_tool.find_nounphrase(marking_tool.parse_list[nounphrase[0] - 1])
            for nounphrase in test[2]:
                marking_tool.neutralize_nounphrase(nounphrase[0] - 1, nounphrase[1])
            self.assertEqual(marking_tool.get_sentence(), test[1] + " ",f"Text {i+1} doesn't have correct output.") 


if __name__ == "__main__":
    unittest.main()

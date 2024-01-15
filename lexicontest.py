from lexicon import Lexicon
from marking_tool import Marking_Tool
import parzu_class as parzu
import unittest
from __init__ import split_prepositions


class Sentence_Test(unittest.TestCase):
    def test_sentences(self):
        ParZu = parzu.Parser(parzu.process_arguments())
        test_sentences = []
        test_sentences.append(("Der Lehrer gibt dem Schüler den Stift.", "De Lehrere gibt derm Schülere den Stift.", ((2,34), (5,6))))
        test_sentences.append(("Er gibt ihr den Stift.", "En gibt em den Stift.", ((1,0), (3,0))))
        test_sentences.append(("Das Buch meines Professors ist interessant.", "Das Buch meiners Professores ist interessant.", ((4,43),)))
        test_sentences.append(("Sein Buch ist interessant.", "Ens Buch ist interessant.", ((1,0),)))
        test_sentences.append(("Auch seine Vorlesungen sind spannend.", "Auch ense Vorlesungen sind spannend.", ((2,0),)))
        test_sentences.append(("Kennst du meine Verlobte Kim?", "Kennst du mein Verlobte Kim?", ((4, -1),)))
        test_sentences.append(("Ja, ich kenne sie schon.", "Ja, ich kenne en schon.", ((5,0),)))
        test_sentences.append(("Und kennst du auch ihre Kollegin Andrea?", "Und kennst du auch ens Kollegere Andrea?", ((5,0), (6,27))))
        test_sentences.append(("Nein, ich glaub nicht, dass ich sie schon kennengelernt habe.", "Nein, ich glaub nicht, dass ich en schon kennengelernt habe.", ((9,0),)))
        test_sentences.append(("Ich kenne aber schon viele andere Kollegen von Kim.", "Ich kenne aber schon viele andere Kollegerne von Kim.", ((7,27),)))
        test_sentences.append(("Bei uns ist jeder willkommen!", "Bei uns ist jedey willkommen!", ((4,0),)))
        test_sentences.append(("Als Vorsitzender hat Kim viel zu tun.", "Als Vorsitzendey hat Kim viel zu tun.", ((2,-1),)))
        test_sentences.append(("Sein öffentliches Coming-Out als X-gender und asexuell hatte Kamatani in einem Tweet im Jahr 2012.", "Ens öffentliches Coming-Out als X-gender und asexuell hatte Kamatani in einem Tweet im Jahr 2012.",((1,0),)))
        test_sentences.append(("Ich kenne viele andere Schüler.", "Ich kenne viele andere Schülerne.", ((5,6),)))
        test_sentences.append(("Wo ist das Hauptgebäude seiner Schule?", "Wo ist das Hauptgebäude enser Schule?", ((5,0),)))
        test_sentences.append(("Kennst Du seinen Namen?", "Kennst Du ensen Namen?", ((3,0),)))
        test_sentences.append(("Als Vorsitzender hat Kim viel zu tun.", "Als Vorsitzendey hat Kim viel zu tun.", ((2,-1),)))
        test_sentences.append(("Sicher kaum einer!", "Sicher kaum einey!", ((3,0),)))
        test_sentences.append(("Der Schüler, der dort steht, ist nett.", "De Schülere, de dort steht, ist nett.", ((2,6), (4,0))))
        test_sentences.append(("Aufgrund ihrer Krankheit wird sie leider nicht dabei sein.", "Aufgrund enser Krankheit wird en leider nicht dabei sein.", ((2,0),(5,0))))
        test_sentences.append(("Mein Opa liegt im Krankenhaus.", "Mein Ota liegt im Krankenhaus.", ((2,-3),)))
        test_sentences.append(("Einer von den beiden wird kommen.", "Einey von den beiden wird kommen.", ((1,0),)))
        test_sentences.append(("Als guter Lehrer kann er das.", "Als gutey Lehrere kann en das.", ((3,34),(5,0))))
        test_sentences.append(("Die Mitglieder nehmen als gute Lehrer teil.", "Die Mitglieder nehmen als gute Lehrerne teil.", ((6,34),)))
        test_sentences.append(("Das Mitglied nimmt als guter Lehrer teil.", "Das Mitglied nimmt als gutey Lehrere teil.", ((6,34),)))
        test_sentences.append(("Er nimmt als guter Lehrer teil.", "En nimmt als gutey Lehrere teil.", ((1,0),(5,34))))
        test_sentences.append(("Als gute Lehrer nehmen die Mitglieder teil.", "Als gute Lehrerne nehmen die Mitglieder teil.", ((3,34),)))
        test_sentences.append(("Kim arbeitet mit anderen Aktivisten zusammen.", "Kim arbeitet mit anderen Aktivisternen zusammen.", ((5,473),)))
        test_sentences.append(("Ich kenne andere Schüler.", "Ich kenne andere Schülerne.", ((4,6),)))
        test_sentences.append(("Sie war als Jugendliche mit dem Studenten befreundet.", "En war als Jugendlichey mit derm Studente befreundet.", ((1,0),(4,-1),(7,50))))
        test_sentences.append(("Ich habe ihn schon als Jugendlichen kennengelernt.", "Ich habe en schon als Jugendlichey kennengelernt.", ((3,0),(6,-1))))
        test_sentences.append(("Das Brett steht zwischen den Spielern.", "Das Brett steht zwischen den Spielernen.", ((6,10),)))
        test_sentences.append(("Wir verteidigen die Rechte eines jeden Bürgers.", "Wir verteidigen die Rechte einers jeden Bürgeres.", ((7,12),)))
        test_sentences.append(("Jeder Lehrer kennt das.", "Jedey Lehrere kennt das.", ((2,34),)))
        test_sentences.append(("Ich war beim Bergmann und gehe zum Feuerwehrmann.", "Ich war bei der Bergperson und gehe zur Feuerwehrperson.", ((5,-2),(10,-2))))
        test_sentences.append(("Die Lehrerin steht beim Schüler und schaut zum Direktor.", "De Lehrere steht bei derm Schülere und schaut zurm Direktore.", ((2,34),(6,6),(11,72))))
        test_sentences.append(("Der Nachbar im Nachbarhaus ist nett.", "De Nachbare im Nachbarhaus ist nett.", ((2,82),)))
        for i,test in enumerate(test_sentences):
            print(f"Testing sentence {i + 1}.")
            input_text_with_split_prepositions = split_prepositions(test[0])
            parse = ParZu.main(input_text_with_split_prepositions)
            words = parse[0].split("\n")
            words = words[:-2]
            parse_list = []
            for word in words:
                parse_list.append(word.split("\t"))
            marking_tool = Marking_Tool(parse_list,{})
            parse_list = Marking_Tool.find_realizations(marking_tool,test[0])
            marking_form = marking_tool.get_marking_form(0)
            # for nounphrase in test[2]:
            #    marking_tool.find_nounphrase(marking_tool.parse_list[nounphrase[0] - 1])
            print("Noun phrases:")
            print(marking_tool.nounphrases)
            for nounphrase in test[2]:
                marking_tool.neutralize_nounphrase(nounphrase[0] - 1, nounphrase[1])
            self.assertEqual(marking_tool.get_sentence(), test[1], f"Text {i+1} doesn't have correct output.") 


if __name__ == "__main__":
    unittest.main()

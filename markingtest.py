from lexicon import Lexicon
from marking_tool import Marking_Tool
import parzu_class as parzu
import unittest


class Marking_Test(unittest.TestCase):
    def test_marking(self):
        test_sentence_1 = ("Der Lehrer gibt dem Schüler den Stift.", """Der <input type="checkbox" id="0|2|34" name="0|2|34" value="select">
                    <label for="0|2|34"><u>Lehrer</u></label> gibt dem <input type="checkbox" id="0|5|6" name="0|5|6" value="select">
                    <label for="0|5|6"><u>Schüler</u></label> den Stift. """)
        test_sentence_2 = ("Er gibt ihr den Stift.","""<input type="checkbox" id="0|1|0" name="0|1|0" value="select">
                <label for="0|1|0"><u>Er</u></label> gibt <input type="checkbox" id="0|3|0" name="0|3|0" value="select">
                <label for="0|3|0"><u>ihr</u></label> den Stift. """)
        test_sentence_3 = ("Morgen regnet es.", "Morgen regnet es. ")
        test_sentence_4 = ("Kennst Du meine Verlobte?", """Kennst Du meine <input type="checkbox" id="0|4|-1" name="0|4|-1" value="select">
                    <label for="0|4|-1"><u>Verlobte</u></label>? """)
        test_sentence_5 = ("Gleich kommen sie.", "Gleich kommen sie. ")
        test_sentence_6 = ("Es kostet nicht viel.", "Es kostet nicht viel. ")
        test_sentences = [test_sentence_1, test_sentence_2, test_sentence_3, test_sentence_4, test_sentence_5, test_sentence_6]
        ParZu = parzu.Parser(parzu.process_arguments())
        for i, test in enumerate(test_sentences):
            parse = ParZu.main(test[0])
            words = parse[0].split("\n")
            words = words[:-2]
            marking_tool = Marking_Tool(words)
            self.assertEqual(marking_tool.get_marking_form(0), test[1])


if __name__ == "__main__":
    unittest.main()

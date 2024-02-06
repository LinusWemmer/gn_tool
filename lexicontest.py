from lexicon import Lexicon
from marking_tool import Marking_Tool
import parzu_class as parzu
import unittest
import re
from __init__ import get_parse
from __init__ import split_prepositions
from __init__ import search_lonely_adjectives
from __init__ import hack_for_ordinal_numbers
from __init__ import undo_hack_for_ordinal_numbers


class Sentence_Test(unittest.TestCase):
    def test_sentences(self):
        ParZu = parzu.Parser(parzu.process_arguments())
        test_sentences = []
        test_sentences.append(("Der Lehrer gibt dem Schüler den Stift.", "De Lehrere gibt derm Schülere den Stift."))
        test_sentences.append(("Er gibt ihr den Stift.", "En gibt em den Stift."))
        test_sentences.append(("Das Buch meines Professors ist interessant.", "Das Buch meiners Professores ist interessant."))
        test_sentences.append(("Sein Buch ist interessant.", "Ens Buch ist interessant."))
        test_sentences.append(("Auch seine Vorlesungen sind spannend.", "Auch ense Vorlesungen sind spannend."))
        test_sentences.append(("Kennst du meine Verlobte Kim?", "Kennst du mein Verlobte Kim?"))
        test_sentences.append(("Ja, ich kenne sie schon.", "Ja, ich kenne en schon."))
        test_sentences.append(("Und kennst du auch ihre Kollegin Andrea?", "Und kennst du auch ens Kollegere Andrea?"))
        test_sentences.append(("Nein, ich glaub nicht, dass ich sie schon kennengelernt habe.", "Nein, ich glaub nicht, dass ich en schon kennengelernt habe."))
        test_sentences.append(("Ich kenne aber schon viele andere Kollegen von Kim.", "Ich kenne aber schon viele andere Kollegerne von Kim."))
        test_sentences.append(("Bei uns ist jeder willkommen!", "Bei uns ist jedey willkommen!"))
        test_sentences.append(("Als Vorsitzender hat Kim viel zu tun.", "Als Vorsitzendey hat Kim viel zu tun."))
        test_sentences.append(("Sein öffentliches Coming-Out als X-gender und asexuell hatte Kamatani in einem Tweet im Jahr 2012.", "Ens öffentliches Coming-Out als X-gender und asexuell hatte Kamatani in einem Tweet im Jahr 2012."))
        test_sentences.append(("Ich kenne viele andere Schüler.", "Ich kenne viele andere Schülerne."))
        test_sentences.append(("Wo ist das Hauptgebäude seiner Schule?", "Wo ist das Hauptgebäude enser Schule?"))
        test_sentences.append(("Kennst Du seinen Namen?", "Kennst Du ensen Namen?"))
        test_sentences.append(("Sicher kaum einer!", "Sicher kaum einey!"))
        test_sentences.append(("Der Schüler, der dort steht, ist nett.", "De Schülere, de dort steht, ist nett."))
        test_sentences.append(("Aufgrund ihrer Krankheit wird sie leider nicht dabei sein.", "Aufgrund enser Krankheit wird en leider nicht dabei sein."))
        test_sentences.append(("Mein Opa liegt im Krankenhaus.", "Mein Ota liegt im Krankenhaus."))
        test_sentences.append(("Einer von den beiden wird kommen.", "Einey von den beiden wird kommen."))
        test_sentences.append(("Als guter Lehrer kann er das.", "Als gutey Lehrere kann en das."))
        test_sentences.append(("Die Mitglieder nehmen als gute Lehrer teil.", "Die Mitglieder nehmen als gute Lehrerne teil."))
        test_sentences.append(("Das Mitglied nimmt als guter Lehrer teil.", "Das Mitglied nimmt als gutey Lehrere teil."))
        test_sentences.append(("Er nimmt als guter Lehrer teil.", "En nimmt als gutey Lehrere teil."))
        test_sentences.append(("Als gute Lehrer nehmen die Mitglieder teil.", "Als gute Lehrerne nehmen die Mitglieder teil."))
        test_sentences.append(("Kim arbeitet mit anderen Aktivisten zusammen.", "Kim arbeitet mit anderen Aktivisternen zusammen."))
        test_sentences.append(("Ich kenne andere Schüler.", "Ich kenne andere Schülerne."))
        test_sentences.append(("Sie war als Jugendliche mit dem Studenten befreundet.", "En war als Jugendlichey mit derm Studente befreundet."))
        test_sentences.append(("Ich habe ihn schon als Jugendlichen kennengelernt.", "Ich habe en schon als Jugendlichey kennengelernt."))
        test_sentences.append(("Das Brett steht zwischen den Spielern.", "Das Brett steht zwischen den Spielernen."))
        test_sentences.append(("Wir verteidigen die Rechte eines jeden Bürgers.", "Wir verteidigen die Rechte einers jeden Bürgeres."))
        test_sentences.append(("Jeder Lehrer kennt das.", "Jedey Lehrere kennt das."))
        test_sentences.append(("Ich war beim Bergmann und gehe zum Feuerwehrmann.", "Ich war bei der Bergperson und gehe zur Feuerwehrperson."))
        test_sentences.append(("Die Lehrerin steht beim Schüler und schaut zum Direktor.", "De Lehrere steht bei derm Schülere und schaut zurm Direktore."))
        test_sentences.append(("Der Nachbar im Nachbarhaus ist nett.", "De Nachbare im Nachbarnehaus ist nett."))
        test_sentences.append(("Wer das nicht weiß, der hat keine Chance bei den Frauen.", "Wer das nicht weiß, de hat keine Chance bei den Leuten."))
        test_sentences.append(("eine Schülerin", "ein Schülere"))
        test_sentences.append(("Ich gebe es meiner Kollegin.", "Ich gebe es meinerm Kollegere."))
        test_sentences.append(("Ich gebe es meinen Kollegen.", "Ich gebe es meinen Kollegernen."))
        test_sentences.append(("Er sprach auch mit seinen Studenten.", "En sprach auch mit ensen Studenternen."))
        test_sentences.append(("Sind das Deine Ahnen?", "Sind das Deine Ahnerne?"))
        test_sentences.append(("Es gab einen Konflikt zwischen Studenten und Regierung.", "Es gab einen Konflikt zwischen Studenternen und Regierung."))
        test_sentences.append(("Es gab einen Konflikt zwischen Regierung und Studenten.", "Es gab einen Konflikt zwischen Regierung und Studenternen."))
        test_sentences.append(("Es gab einen Konflikt unter Studenten.", "Es gab einen Konflikt unter Studenternen."))
        test_sentences.append(("Vor Studenten spricht er immer laut.", "Vor Studenternen spricht en immer laut."))
        test_sentences.append(("Hinter Studenten steht immer ein Lehrer.", "Hinter Studenternen steht immer ein Lehrere."))
        test_sentences.append(("Neben Studenten steht immer ein Lehrer.", "Neben Studenternen steht immer ein Lehrere."))
        test_sentences.append(("Ich habe einen netten und einen unfreundlichen Kollegen.", "Ich habe ein nette und ein unfreundliche Kollegere."))
        test_sentences.append(("Jedem anderen habe ich das gegeben.", "Jederm anderen habe ich das gegeben."))
        test_sentences.append(("Ich habe es jedem anderen gegeben.", "Ich habe es jederm anderen gegeben."))
        test_sentences.append(("Jeder hilft jedem anderen.", "Jedey hilft jederm anderen."))
        test_sentences.append(("Der Bruder meiner Mutter hilft der Cousine meines Sohnes.", "De Geschwister meiners Elters hilft derm Couse meiners Sprosses."))
        test_sentences.append(("Die Supermutter spielt mit ihrem Minisohn.", "De Superelter spielt mit enserm Minispross."))
        test_sentences.append(("Hat er das aus Brüderliebe oder aus Liebe zum Vaterland gemacht?", "Hat en das aus Geschwisterliebe oder aus Liebe zum Elterland gemacht?"))
        test_sentences.append(("Was ist Deine Muttersprache?", "Was ist Deine Eltersprache?"))
        test_sentences.append(("Er hat für mich eine Onkelrolle eingenommen.", "En hat für mich eine Tonkenrolle eingenommen."))
        test_sentences.append(("Ich habe es meiner Mutter gegeben.", "Ich habe es meinerm Elter gegeben."))
        test_sentences.append(("Der Hauptcharakter bleibt.", "De Hauptcharakter bleibt."))
        test_sentences.append(("Ich glaube ihr nicht.", "Ich glaube em nicht."))
        test_sentences.append(("Das ist der Schüler, welcher ihr geholfen hat.", "Das ist de Schülere, welchey em geholfen hat."))
        test_sentences.append(("Bitte hilf demjenigen, der das gesagt hat.", "Bitte hilf dermjenigen, de das gesagt hat."))
        test_sentences.append(("Wo ist das Superlehrerzimmer?", "Wo ist das Superlehrernezimmer?"))
        test_sentences.append(("Die Latina geht mit dem Superballerino zur Toreroshow.", "De Latine geht mit derm Superballerine zur Torererneshow."))
        test_sentences.append(("Wo ist die Bürgermeisterin?", "Wo ist de Bürgernemeistere?"))
        test_sentences.append(("Die Witwe gibt dem Bräutigam die Prinzenrolle.", "De Witwere gibt derm Braute die Prinzernerolle."))
        test_sentences.append(("Der Gast kommt.", "De Gast kommt."))
        test_sentences.append(("Unser Gast ist ein Fernsehstar.", "Unse Gast ist ein Fernsehstar."))
        test_sentences.append(("Als Englischsprachige ist sie mit keinem Deutschsprachigen befreundet.", "Als Englischsprachigey ist en mit keinerm Deutschsprachigen befreundet."))
        test_sentences.append(("Als Beamtin gibt sie den anderen Beamten einen Ausdruck des Sonderbeamtengesetzes.", "Als Beamtey gibt en den anderen Beamternen einen Ausdruck des Sonderbeamternegesetzes."))
        test_sentences.append(("Des Weiteren kandidiert Kim für die Wahl zum Kassierer des Bundesverbands von Fridays for Future.", "Des Weiteren kandidiert Kim für die Wahl zurm Kassierere des Bundesverbands von Fridays for Future."))
        test_sentences.append(("Eine große und eine kleine Schülerin gehen gemeinsam zur Direktorin.", "Ein große und ein kleine Schülere gehen gemeinsam zurm Direktore."))
        test_sentences.append(("Er ist ein Pole.", "En ist ein Polere."))
        test_sentences.append(("Die Heldentaten der Bürgermeisterin wurden von den anderen Bürgermeisterkandidaten während des Wahlkampes zur Bürgermeisterwahl totgeschwiegen.", "Die Heldernetaten ders Bürgernemeisteres wurden von den anderen Bürgernemeisternekandidaternen während des Wahlkampes zur Bürgernemeisternewahl totgeschwiegen."))
        test_sentences.append(("Jeder andere bleibt im Haus.", "Jedey andere bleibt im Haus."))
        test_sentences.append(("Im selben Monat stellte ihn der Bundesstaat Georgia u. a. wegen versuchter Wahlbeeinflussung unter Anklage.", "Im selben Monat stellte en der Bundesstaat Georgia u. a. wegen versuchter Wahlbeeinflussung unter Anklage."))
        test_sentences.append(("Sie wurde unter anderem wegen ihrer Programmierkenntnisse eingestellt.", "En wurde unter anderem wegen enser Programmierkenntnisse eingestellt."))
        test_sentences.append(("Trump ist der erste ehemalige US-Präsident, der sich wegen solcher Vergehen vor Gericht verantworten muss.", "Trump ist de erste ehemalige US-Präsidente, de sich wegen solcher Vergehen vor Gericht verantworten muss."))
        test_sentences.append(("Das ist ihrer.", "Das ist ensey."))
        test_sentences.append(("Das ist seines.", "Das ist enses."))
        test_sentences.append(("Das ist Deine.", "Das ist Deiney."))
        test_sentences.append(("Mit den Details des Gesetzes bin ich alles andere als zufrieden.", "Mit den Details des Gesetzes bin ich alles andere als zufrieden."))
        test_sentences.append(("Mit allem anderen bin ich zufrieden.", "Mit allem anderen bin ich zufrieden."))
        test_sentences.append(("Das ist das Auto vom Hausmeister.", "Das ist das Auto von derm Hausmeistere."))
        test_sentences.append(("Das liegt nur am Lehrer.", "Das liegt nur an derm Lehrere."))
        test_sentences.append(("So viel John Wayne steckt im Kanzler.", "So viel John Wayne steckt in derm Kanzlere."))
        test_sentences.append(("Das passiert am häufigsten im Auto.", "Das passiert am häufigsten im Auto."))
        test_sentences.append(("Mein Ururopa stammte aus Europa, aber mein Uropa ist schon in Brasilien geboren.", "Mein Ururota stammte aus Europa, aber mein Urota ist schon in Brasilien geboren."))
        test_sentences.append(("Erst der britische König Edward VII. konnte 1902 den Grenzstreit schlichten.", "Erst de britische Könige Edward VII. konnte 1902 den Grenzstreit schlichten."))
        test_sentences.append(("Als ehrlicher Kaufmann besteche ich keine Politiker.", "Als ehrliche Kaufperson besteche ich keine Politikerne."))
        test_sentences.append(("Mit mir als ehrlichem Kaufmann kann man keine solchen Geschäfte machen.", "Mit mir als ehrlicher Kaufperson kann mensch keine solchen Geschäfte machen."))
        test_sentences.append(("Ich gebe das einem ehrlichen Kaufmann.", "Ich gebe das einer ehrlichen Kaufperson."))
        test_sentences.append(("Wir brauchen mehr Zusammenhalt.", "Wir brauchen mehr Zusammenhalt."))
        test_sentences.append(("Ist hier jemand, der uns helfen kann?", "Ist hier jemand, de uns helfen kann?"))
        test_sentences.append(("Ein jeder kommt zu seiner Zeit.", "Ein jede kommt zu enser Zeit."))
        test_sentences.append(("Der hohe Angestellte verdient mehr als der niedrige.", "De hohe Angestellte verdient mehr als de niedrige."))
        test_sentences.append(("Der rosa Kämpfer ist mein Held.", "De rosa Kämpfere ist mein Helde."))
        test_sentences.append(("Das ist derselbe Lehrer wie gestern.", "Das ist deselbe Lehrere wie gestern."))
        test_sentences.append(("Ich habe es derselben Lehrerin zurückgegeben.", "Ich habe es dermselben Lehrere zurückgegeben."))
        test_sentences.append(("Diese Schülerin ist dieselbe, die gestern hier war.", "Diesey Schülere ist deselbe, de gestern hier war."))
        test_sentences.append(("Ich rede mit derjenigen Schülerin, die gestern hier war.", "Ich rede mit dermjenigen Schülere, de gestern hier war."))
        test_sentences.append(("Das ist unser Lehrer und nicht eurer.", "Das ist unse Lehrere und nicht eurey."))
        test_sentences.append(("Das ist eure Lehrerin und nicht unsere.", "Das ist eue Lehrere und nicht unserey."))
        test_sentences.append(("Ich spiele mit eurem Sohn Tennis.", "Ich spiele mit eurerm Spross Tennis."))
        test_sentences.append(("Das ist das Auto unserer Nachbarin.", "Das ist das Auto unserers Nachbares."))
        test_sentences.append(("Er war von 2009 bis 2017 der 44. Präsident der Vereinigten Staaten.", "En war von 2009 bis 2017 de 44. Präsidente der Vereinigten Staaten."))
        test_sentences.append(("Unter den Menschen, die in den großen Städten das Glück suchten, waren viele landlose Arbeiter und verarmte Kleinbauern.", "Unter den Menschen, die in den großen Städten das Glück suchten, waren viele landlose Arbeiterne und verarmte Kleinbauerne."))
        test_sentences.append(("Er ist Lehrer.", "En ist Lehrere."))
        test_sentences.append(("Er war zunächst unter dem Militärregime Ramírez Minister für Arbeit.", "En war zunächst unter dem Militärregime Ramírez Ministere für Arbeit."))
        test_sentences.append(("Die Veranstalter sprachen von rund 300.000 Teilnehmerinnen und Teilnehmern.", "Die Veranstalterne sprachen von rund 300.000 Teilnehmernen."))
        test_sentences.append(("Die Wählerinnen und Wähler wünschen sich kompetentere Politiker und Politikerinnen.", "Die Wählerne wünschen sich kompetentere Politikerne."))
        test_sentences.append(("Den Lehrerinnen und Lehrern ist die schulische Leistung der Schülerinnen und Schüler nicht egal.", "Den Lehrernen ist die schulische Leistung der Schülerne nicht egal."))
        for i,test in enumerate(test_sentences):
            print(f"Testing sentence {i + 1}.")
            input_text = hack_for_ordinal_numbers(test[0])
            input_text_with_split_prepositions = split_prepositions(input_text)
            parse = get_parse(input_text_with_split_prepositions)

            modified_text, capitalized_words, glauben, change = search_lonely_adjectives(parse,input_text)
            if not change:
                marking_tool = Marking_Tool(parse[0],{},[])
                marked_nouns = mark_nouns(parse,[],[])
            else:
                print("Parsing again with capitalized adjectives.")
                modified_text_with_split_prepositions = split_prepositions(modified_text)
                parse = get_parse(modified_text_with_split_prepositions)
                print(parse)            
                marking_tool = Marking_Tool(parse[0],{},[])
                modified_text = Marking_Tool.find_realizations(marking_tool,modified_text)
                marked_nouns = mark_nouns(parse,capitalized_words, glauben)
                # for capitalized_adj_address in capitalized_adj_addresses:
                #     print(capitalized_adj_address)
                #     parse[0][capitalized_adj_address[1]][2] = parse[0][capitalized_adj_address[1]][2].lower()
                #     parse[0][capitalized_adj_address[1]][-2] = parse[0][capitalized_adj_address[1]][-2].lower()
                #     if parse[0][capitalized_adj_address[1]][2].startswith("andere") and len(parse[0][capitalized_adj_address[1]][2]) < 8:
                #         parse[0][capitalized_adj_address[1]][2] = "andere"
                # for glauben_address in glauben:
                #     parse[0][glauben_address[1]][1] = re.sub(r"schreib", "glaub", parse[0][glauben_address[1]][1])
                #     parse[0][glauben_address[1]][1] = re.sub(r"Schreib", "Glaub", parse[0][glauben_address[1]][1])
                #     parse[0][glauben_address[1]][2] = re.sub(r"schreib", "glaub", parse[0][glauben_address[1]][2])
                #     parse[0][glauben_address[1]][-2] = re.sub(r"schreib", "glaub", parse[0][glauben_address[1]][-2])
                #     parse[0][glauben_address[1]][-2] = re.sub(r"Schreib", "Glaub", parse[0][glauben_address[1]][-2])
            print(parse)

            marking_form = marking_tool.get_marking_form(0)
            print("Noun phrases:")
            print(marking_tool.nounphrases)

            # In marked_nouns, search for strings of the form 'id="\d+\|(\d+)\|(-?\d+)"' and let selection be the list of pairs of integers corresponding to the matches.
            id_pattern = r"id=\"\d+\|(\d+)\|(-?\d+)\"" # Matches the id attribute of a noun.
            selection = []
            for match in re.finditer(id_pattern, marked_nouns):
                selection.append((int(match.group(1)), int(match.group(2))))

            list_of_neutralized_nouns = []
            for nounphrase in selection:
                if nounphrase[0] not in list_of_neutralized_nouns:
                    selected_components = []
                    for component_data in selection:
                        if component_data[0] == nounphrase[0]:
                            selected_components.append(component_data[1])
                    marking_tool.neutralize_nounphrase(nounphrase[0] - 1, selected_components)
                    list_of_neutralized_nouns.append(nounphrase[0])
            output_text = undo_hack_for_ordinal_numbers(marking_tool.get_sentence())
            self.assertEqual(output_text, test[1], f"Text {i+1} doesn't have correct output.") 

def mark_nouns(sentences: list, capitalized_adj_addresses, glauben):
    marking_form = ""
    sentence_number = 0
    for i, parse_list in enumerate(sentences):
        marking_tool = Marking_Tool(parse_list,{},[])
        for capitalized_adj_address in capitalized_adj_addresses:
            if i == capitalized_adj_address[0]:
                marking_tool.parse_list[capitalized_adj_address[1]][2] = marking_tool.parse_list[capitalized_adj_address[1]][2].lower()
                marking_tool.parse_list[capitalized_adj_address[1]][-2] = marking_tool.parse_list[capitalized_adj_address[1]][-2].lower()
                if marking_tool.parse_list[capitalized_adj_address[1]][2].startswith("andere") and len(marking_tool.parse_list[capitalized_adj_address[1]][2]) < 8:
                    marking_tool.parse_list[capitalized_adj_address[1]][2] = "andere"
        for glauben_address in glauben:
            if i == glauben_address[0]:
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"Schreib", "Glaub", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][2] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][-2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"Schreib", "Glaub", marking_tool.parse_list[glauben_address[1]][-2])
        #sentence_data.add_marking_tool(sentence_number, marking_tool)
        marking_form += marking_tool.get_marking_form(sentence_number)
        sentence_number += 1
    return marking_form

if __name__ == "__main__":
    unittest.main()

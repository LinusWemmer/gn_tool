from lexicon import Lexicon
from marking_tool import Marking_Tool
import unittest
import re
from __init__ import get_parse
from __init__ import split_prepositions
from __init__ import remove_special_character_gendering
from __init__ import search_lonely_adjectives
from __init__ import hack_for_ordinal_numbers
from __init__ import undo_hack_for_ordinal_numbers


class Sentence_Test(unittest.TestCase):
    def test_sentences(self):
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
        test_sentences.append(("Mein Opa liegt im Krankenhaus.", "Mein Owa liegt im Krankenhaus."))
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
        test_sentences.append(("Der Bruder meiner Mutter hilft der Cousine meines Sohnes.", "De Geschwister meiners Elters hilft derm Couse meines Kindes."))
        test_sentences.append(("Die Supermutter spielt mit ihrem Minisohn.", "De Superelter spielt mit ensem Minikind."))
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
        test_sentences.append(("Mein Ururopa stammte aus Europa, aber mein Uropa ist schon in Brasilien geboren.", "Mein Ururowa stammte aus Europa, aber mein Urowa ist schon in Brasilien geboren."))
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
        test_sentences.append(("Ich spiele mit eurem Sohn Tennis.", "Ich spiele mit eurem Kind Tennis."))
        test_sentences.append(("Das ist das Auto unserer Nachbarin.", "Das ist das Auto unserers Nachbares."))
        test_sentences.append(("Er war von 2009 bis 2017 der 44. Präsident der Vereinigten Staaten.", "En war von 2009 bis 2017 de 44. Präsidente der Vereinigten Staaten."))
        test_sentences.append(("Unter den Menschen, die in den großen Städten das Glück suchten, waren viele landlose Arbeiter und verarmte Kleinbauern.", "Unter den Menschen, die in den großen Städten das Glück suchten, waren viele landlose Arbeiterne und verarmte Kleinbauerne."))
        test_sentences.append(("Er ist Lehrer.", "En ist Lehrere."))
        test_sentences.append(("Er war zunächst unter dem Militärregime Ramírez Minister für Arbeit.", "En war zunächst unter dem Militärregime Ramírez Ministere für Arbeit."))
        test_sentences.append(("Die Veranstalter sprachen von rund 300.000 Teilnehmerinnen und Teilnehmern.", "Die Veranstalterne sprachen von rund 300.000 Teilnehmernen."))
        test_sentences.append(("Die Wählerinnen und Wähler wünschen sich kompetentere Politiker und Politikerinnen.", "Die Wählerne wünschen sich kompetentere Politikerne."))
        test_sentences.append(("Den Lehrerinnen und Lehrern ist die schulische Leistung der Schülerinnen und Schüler nicht egal.", "Den Lehrernen ist die schulische Leistung der Schülerne nicht egal."))
        test_sentences.append(("Die Beamten und Beamtinnen feiern.", "Die Beamterne feiern."))
        test_sentences.append(("Die Staatsbeamten und Staatsbeamtinnen feiern.", "Die Staatsbeamterne feiern."))
        test_sentences.append(("Die Putzfrauen und Putzmänner kommen gleich.", "Die Putzleute kommen gleich."))
        test_sentences.append(("Die Latinos und Latinas kommen gleich.", "Die Latinerne kommen gleich."))
        test_sentences.append(("Wie viele Tanten und Onkel hast Du?", "Wie viele Tonken hast Du?"))
        test_sentences.append(("Als Jugendlicher oder Jugendliche darf man das noch nicht.", "Als Jugendlichey darf mensch das noch nicht."))
        test_sentences.append(("Als Deutschsprachiger oder Deutschsprachige sollte man das wissen.", "Als Deutschsprachigey sollte mensch das wissen."))
        test_sentences.append(("Die Witwen und Witwer können sich auf eine Rentenerhöhung freuen.", "Die Witwerne können sich auf eine Rentenerhöhung freuen."))
        test_sentences.append(("Viele Einwohner – fast alles Serben – sind mit der Zentralregierung unzufrieden.", "Viele Einwohnerne – fast alles Serberne – sind mit der Zentralregierung unzufrieden."))
        test_sentences.append(("Ich kenne einen Russischsprachigen, der Dir helfen kann.", "Ich kenne ein Russischsprachige, de Dir helfen kann."))
        test_sentences.append(("Der Bräutigam hält seine Verlobte für eine Prinzessin.", "De Braute hält ens Verlobte für ein Prinze."))
        test_sentences.append(("Wir gedenken seiner.", "Wir gedenken enser."))
        test_sentences.append(("Nun gedachten sie seiner mit einer Schweigeminute.", "Nun gedachten sie enser mit einer Schweigeminute."))
        test_sentences.append(("Er hat sich ihrer nur sehr ungern angenommen.", "En hat sich enser nur sehr ungern angenommen."))
        test_sentences.append(("Er nahm sich ihrer nur sehr ungern an.", "En nahm sich enser nur sehr ungern an."))
        test_sentences.append(("Der Lehrer, der sich dieser Sache annimmt, ist nicht seiner.", "De Lehrere, de sich dieser Sache annimmt, ist nicht ensey."))
        test_sentences.append(("Wenn wir uns seiner aufgrund seiner damaligen Taten noch heute schämen, sagt das mehr über uns als über ihn aus.", "Wenn wir uns enser aufgrund enser damaligen Taten noch heute schämen, sagt das mehr über uns als über en aus."))
        test_sentences.append(("Die Ungarn leben in Ungarn.", "Die Ungarne leben in Ungarn."))
        test_sentences.append(("Er war der Erste, der das geschafft hat.", "En war de Erste, de das geschafft hat."))
        test_sentences.append(("Erster Mann zu sein ist nicht sein Ding.", "Erste Person zu sein ist nicht ens Ding."))
        test_sentences.append(("Unter Perón, der mit faschistischem Gedankengut sympathisierte, verfolgte Argentinien das Ziel, durch Zugeständnisse an die Arbeiter den Kommunismus abzuwehren.", "Unter Perón, de mit faschistischem Gedankengut sympathisierte, verfolgte Argentinien das Ziel, durch Zugeständnisse an die Arbeiterne den Kommunismus abzuwehren."))
        test_sentences.append(("Als Merkel, mit der ich in der Schule war, Kanzlerin wurde, war ich sehr überrascht.", "Als Merkel, mit derm ich in der Schule war, Kanzlere wurde, war ich sehr überrascht."))
        test_sentences.append(("Es ist nicht dasselbe Google, für das ich damals gearbeitet habe.", "Es ist nicht dasselbe Google, für das ich damals gearbeitet habe."))
        test_sentences.append(("Ich gebe es einem jeden Mann.", "Ich gebe es einer jeden Person."))
        test_sentences.append(("Der Mann, welcher das gesagt hat, ist doof.", "Die Person, welche das gesagt hat, ist doof."))
        test_sentences.append(("Er ist ein Transmann.", "En ist eine Transperson."))
        test_sentences.append(("Wo ist die Kim?","Wo ist de Kim?"))
        test_sentences.append(("Wo ist der nette Kim?","Wo ist de nette Kim?"))
        test_sentences.append(("Er kommt aus der Community.","En kommt aus der Community."))
        test_sentences.append(("Die Community ist wichtig.","Die Community ist wichtig."))
        test_sentences.append(("Die Schweiz ist teuer.","Die Schweiz ist teuer."))
        test_sentences.append(("Der Rhein ist lang.","Der Rhein ist lang."))
        test_sentences.append(("Wer war der bekannte Euler?","Wer war de bekannte Euler?"))
        test_sentences.append(("Wer war der bekannte Hermann?","Wer war de bekannte Hermann?"))
        test_sentences.append(("Wer war der bekannte Riemann?","Wer war de bekannte Riemann?"))
        test_sentences.append(("Wer war der bekannte Pellmann?","Wer war de bekannte Pellmann?"))
        test_sentences.append(("Hermann kommt.","Hermann kommt."))
        test_sentences.append(("Wer war der bekannte Zimmermann?","Wer war die bekannte Zimmerperson?"))
        test_sentences.append(("Der Feuerwehrmann kam.","Die Feuerwehrperson kam."))
        test_sentences.append(("Der Ehrenmann half.","Der Ehrenmensch half."))
        test_sentences.append(("Der nette Frank kommt.","De nette Frank kommt."))
        test_sentences.append(("Die Nato tagt.","Die Nato tagt."))
        test_sentences.append(("Der Ahorn blüht.","Der Ahorn blüht."))
        test_sentences.append(("Der Berg ist hoch.","Der Berg ist hoch."))
        test_sentences.append(("Jeder Schutzsuchende hat Rechte.","Jedey Schutzsuchende hat Rechte."))
        test_sentences.append(("Der Schutzsuchende hat Rechte.","De Schutzsuchende hat Rechte."))
        test_sentences.append(("Er sprach mit dem Schutzsuchenden.","En sprach mit derm Schutzsuchenden."))
        test_sentences.append(("Die Hilfesuchende kam.","De Hilfesuchende kam."))
        test_sentences.append(("Der Sachverständige sprach.","De Sachverständige sprach."))
        test_sentences.append(("Der Kriegsgefangene floh.","De Kriegsgefangene floh."))
        test_sentences.append(("Die Anspruchsberechtigte klagte.","De Anspruchsberechtigte klagte."))
        test_sentences.append(("Der Notleidende bat um Hilfe.","De Notleidende bat um Hilfe."))
        test_sentences.append(("Der Schüler kennt den anderen Schüler nicht.","De Schülere kennt de andere Schülere nicht."))
        test_sentences.append(("Er kennt die andere Schülerin.","En kennt de andere Schülere."))
        test_sentences.append(("Er sprach mit dem anderen Schüler.","En sprach mit derm anderen Schülere."))
        test_sentences.append(("Das Buch des anderen Schülers ist da.","Das Buch ders anderen Schüleres ist da."))
        test_sentences.append(("Die anderen Schüler kommen.","Die anderen Schülerne kommen."))
        test_sentences.append(("Er kennt die rosa Lehrerin.","En kennt de rosa Lehrere."))
        test_sentences.append(("Er kennt den super Lehrer.","En kennt de super Lehrere."))
        test_sentences.append(("Er kennt den Schweizer Lehrer.","En kennt de Schweizer Lehrere."))
        test_sentences.append(("Er kennt den Berliner Lehrer.","En kennt de Berliner Lehrere."))
        test_sentences.append(("Er kennt die beige Lehrerin.","En kennt de beige Lehrere."))
        test_sentences.append(("Er kennt den derartigen Lehrer.","En kennt de derartige Lehrere."))
        test_sentences.append(("Sie haben ein Keil zwischen die Bürger und die Regierung getrieben.","Sie haben ein Keil zwischen die Bürgerne und die Regierung getrieben."))
        test_sentences.append(("Sie hat das Buch gelesen.","En hat das Buch gelesen."))
        test_sentences.append(("Sie haben das Buch gelesen.","Sie haben das Buch gelesen."))
        test_sentences.append(("Sie ist gekommen, und die Kinder haben gespielt.","En ist gekommen, und die Kinder haben gespielt."))
        test_sentences.append(("Sie kam, weil die Lehrer streiken.","En kam, weil die Lehrerne streiken."))
        test_sentences.append(("1862 heiratete er Elise Koch, mit der er eine Tochter, Ida, hatte, die 1863 in Pisa geboren wurde.","1862 heiratete en Elise Koch, mit derm en ein Kind, Ida, hatte, das 1863 in Pisa geboren wurde."))
        test_sentences.append(("Er sprach mit der Lehrerin, Frau Meier, die gestern kam.","En sprach mit derm Lehrere, Person Meier, de gestern kam."))
        test_sentences.append(("Das Buch der Lehrerin, die gestern kam, ist da.","Das Buch ders Lehreres, de gestern kam, ist da."))
        test_sentences.append(("Er hatte einen Sohn, Max, der 1863 geboren wurde.","En hatte ein Kind, Max, das 1863 geboren wurde."))
        test_sentences.append(("Er hatte eine Tochter, Ida, die 1863 geboren wurde.","En hatte ein Kind, Ida, das 1863 geboren wurde."))
        test_sentences.append(("Er kannte den Lehrer, Herrn Meier, der gestern kam.","En kannte de Lehrere, Person Meier, de gestern kam."))
        test_sentences.append(("Er sprach mit der Lehrerin, Kim, die gestern kam.","En sprach mit derm Lehrere, Kim, de gestern kam."))
        test_sentences.append(("Kim, die gestern kam, ist da.","Kim, de gestern kam, ist da."))
        test_sentences.append(("Thomas, der gestern kam, ist da.","Thomas, de gestern kam, ist da."))
        test_sentences.append(("Bei den Wahlen im Vierjahresturnus können sie sich zwar ihre Herrschenden aus dem Angebot der Parteieliten auswählen.","Bei den Wahlen im Vierjahresturnus können sie sich zwar ense Herrschenden aus dem Angebot der Parteieliten auswählen."))
        test_sentences.append(("Ich sehe ihre Herrschenden.","Ich sehe ense Herrschenden."))
        test_sentences.append(("Ich sehe ihre Herrschende.","Ich sehe ens Herrschende."))
        test_sentences.append(("Ich sehe ihre Kollegen.","Ich sehe ense Kollegerne."))
        test_sentences.append(("Ich sehe ihren Kollegen.","Ich sehe ens Kollegere."))
        test_sentences.append(("Das ist die echte Alternative und die einzige, für die es sich zu kämpfen lohnt.","Das ist die echte Alternative und de einzige, für die es sich zu kämpfen lohnt."))
        test_sentences.append(("Die Reisende kam.","De Reisende kam."))
        test_sentences.append(("Er kennt den einen und den anderen Lehrer.","En kennt den einen und de andere Lehrere."))
        test_sentences.append(("Er sprach mit dem einen und dem anderen Lehrer.","En sprach mit dem einen und derm anderen Lehrere."))
        test_sentences.append(("Er kennt den ersten und den zweiten Lehrer.","En kennt de erste und de zweite Lehrere."))
        test_sentences.append(("Er kennt den jungen und den alten Lehrer.","En kennt de junge und de alte Lehrere."))
        test_sentences.append(("Der Junge kam.","Die junge Person kam."))
        test_sentences.append(("Das Mädchen kam.","Die junge Person kam."))
        test_sentences.append(("Der eine kam, der andere ging.","De eine kam, de andere ging."))
        test_sentences.append(("Die eine kam, die andere ging.","De eine kam, de andere ging."))
        test_sentences.append(("Die Frau, der ich half, ist da.","Die Person, der ich half, ist da."))
        test_sentences.append(("Sie hat kaufmännische Kenntnisse.","En hat kaufleutische Kenntnisse."))
        test_sentences.append(("Der bergmännische Betrieb ruht.","Der bergleutische Betrieb ruht."))
        test_sentences.append(("Er grüßte landsmännisch.","En grüßte landsleutisch."))
        test_sentences.append(("Die jungfräuliche Landschaft ist schön.","Die jungferliche Landschaft ist schön."))
        test_sentences.append(("Der kaufmännische Angestellte kam.","De kaufleutische Angestellte kam."))
        test_sentences.append(("Er sprach mit dem fachmännischen Lehrer.","En sprach mit derm fachleutischen Lehrere."))
        test_sentences.append(("Kaufmännische Kenntnisse sind nötig.","Kaufleutische Kenntnisse sind nötig."))
        test_sentences.append(("Der staatsmännische Auftritt gelang.","Der staatsleutische Auftritt gelang."))
        test_sentences.append(("Er jagte weidmännisch.","En jagte weidleutisch."))
        test_sentences.append(("Sein weltmännisches Auftreten beeindruckte.","Ens weltgewandtes Auftreten beeindruckte."))
        test_sentences.append(("Die Jungfräulichkeit galt als Tugend.","Die Jungferlichkeit galt als Tugend."))
        test_sentences.append(("Der Feuerwehrmann, der dort steht, kommt gleich her.","Die Feuerwehrperson, die dort steht, kommt gleich her."))
        test_sentences.append(("Jeglicher Politiker könnte diese Ministerien leiten.","Jeglichey Politikere könnte diese Ministerien leiten."))
        test_sentences.append(("Als ehrlicher Bürger macht man das nicht.","Als ehrlichey Bürgere macht mensch das nicht."))
        test_sentences.append(("Ich habe Sie gesehen.","Ich habe Sie gesehen."))
        test_sentences.append(("Wir zeigen ihr das Haus.","Wir zeigen em das Haus."))
        test_sentences.append(("sie","en"))
        test_sentences.append(("ihr","em"))
        test_sentences.append(("ihrem","enserm"))
        test_sentences.append(("sein","ens"))
        test_sentences.append(("die","de"))
        test_sentences.append(("Der","De"))
        test_sentences.append(("das","das"))
        test_sentences.append(("meine","meiney"))
        test_sentences.append(("einer","einey"))
        test_sentences.append(("Lehrer","Lehrere"))
        test_sentences.append(("Studenten","Studenterne"))
        test_sentences.append(("Kunden","Kunderne"))
        test_sentences.append(("Bauern","Bauerne"))
        test_sentences.append(("Das Buch ist nicht seins.","Das Buch ist nicht enses."))
        test_sentences.append(("Drei Tage darauf kündigte sie an, anstelle ihres Mannes in dessen Sinn den politischen Kampf fortsetzen zu wollen.","Drei Tage darauf kündigte en an, anstelle ensers Ehepartneres in dersen Sinn den politischen Kampf fortsetzen zu wollen."))
        test_sentences.append(("Der Mann, dessen Frau gleich kommt, ist schon da.","Die Person, dersen Ehepartnere gleich kommt, ist schon da."))
        test_sentences.append(("Eine Sprecherin des russischen Außenministeriums erklärte, dass die zahlreichen „westlichen Anschuldigungen“ „selbsterklärend“ seien, d. h. keines Kommentars von offizieller russischer Stelle bedürften.","Ein Sprechere des russischen Außenministeriums erklärte, dass die zahlreichen „westlichen Anschuldigungen“ „selbsterklärend“ seien, d. h. keines Kommentars von offizieller russischer Stelle bedürften."))
        test_sentences.append(("Er*sie ist ein*e nette*r Lehrer*in.", "En ist ein nette Lehrere."))
        test_sentences.append(("Er/sie ist ein/e nette/r Lehrer/-in.", "En ist ein nette Lehrere."))
        test_sentences.append(("Das weiß doch jede(r).", "Das weiß doch jedey."))
        test_sentences.append(("Das weiß doch jede_r.", "Das weiß doch jedey."))
        test_sentences.append(("Ihr(e) Lehrer(in) kommt gleich.", "Ens Lehrere kommt gleich."))
        test_sentences.append(("Kannst Du ihr*ihm sagen, dass ihre*seine Bücher schon auf dem Weg zu ihrem*r zukünftigen Besitzer*in sind.", "Kannst Du em sagen, dass ense Bücher schon auf dem Weg zu enserm zukünftigen Besitzere sind."))
        test_sentences.append(("Das Buch ist nicht ihrs*seins.", "Das Buch ist nicht enses."))
        test_sentences.append(("Der Schüler ist nicht ihrer*seiner.", "De Schülere ist nicht ensey."))
        test_sentences.append(("Unsere Mitarbeiter*innen sind stets bereit, Ihnen zu helfen.", "Unsere Mitarbeiterne sind stets bereit, Ihnen zu helfen."))
        test_sentences.append(("In unserem Team ist jede*r willkommen, der/die seine*ihre Ideen einbringen möchte.", "In unserem Team ist jedey willkommen, de ense Ideen einbringen möchte."))
        test_sentences.append(("Die Schüler*innen haben ihre*seine Bücher schon.", "Die Schülerne haben ense Bücher schon."))
        test_sentences.append(("Der/die Vorsitzende des Vereins wird bald eine Rede halten.", "De Vorsitzende des Vereins wird bald eine Rede halten."))
        test_sentences.append(("Die Kandidat:innen für die Stelle müssen über mindestens fünf Jahre Berufserfahrung verfügen.", "Die Kandidaterne für die Stelle müssen über mindestens fünf Jahre Berufserfahrung verfügen."))
        test_sentences.append(("Die Geschäftsleitung sucht nach einer/m engagierten Mitarbeiter*in für das neue Projekt.", "Die Geschäftsleitung sucht nach einerm engagierten Mitarbeitere für das neue Projekt."))
        test_sentences.append(("Als Vorsitzende:r des Vereins hat sie/er viel zu tun.", "Als Vorsitzendey des Vereins hat en viel zu tun."))
        test_sentences.append(("Gibt es eine/n Freiwillige/n, die/der uns helfen kann?", "Gibt es ein Freiwillige, de uns helfen kann?"))
        test_sentences.append(("Haben Sie schon einmal eine/n Lehrer*in getroffen, die/der so jung ist?", "Haben Sie schon einmal ein Lehrere getroffen, de so jung ist?"))
        test_sentences.append(("Bitte erkläre den SchülerInnen das Binnen-I.", "Bitte erkläre den Schülernen das Binnen-I."))
        test_sentences.append(("Kim geht mit ihr*seinem Nachbarn spazieren.", "Kim geht mit enserm Nachbare spazieren."))
        test_sentences.append(("Kim geht mit ihr*seiner Nachbarin spazieren.", "Kim geht mit enserm Nachbare spazieren."))
        test_sentences.append(("Kim geht mit ihr*seiner*m Nachbar*in spazieren.", "Kim geht mit enserm Nachbare spazieren."))
        test_sentences.append(("Der/die Schüler(in) ist nicht sein*ihre(r).", "De Schülere ist nicht ensey."))
        test_sentences.append(("Der/die Schüler(in) ist nicht seine(r)*ihre(r).", "De Schülere ist nicht ensey."))
        test_sentences.append(("Das ist seine*ihre Lehrerin.", "Das ist ens Lehrere."))
        test_sentences.append(("Das ist ihr*e/sein*e Lehrer*in.", "Das ist ens Lehrere."))
        test_sentences.append(("Pädagog(inn)en", "Pädagogerne"))
        test_sentences.append(("Als Lehrer/Lehrerin macht man das nicht.", "Als Lehrere macht mensch das nicht."))
        test_sentences.append(("Die*r Lehrer*in gibt der*m Vorsitzenden ein Buch.", "De Lehrere gibt derm Vorsitzenden ein Buch."))
        test_sentences.append(("Ich kenne einen bekannten und reichen Sänger.", "Ich kenne ein bekannte und reiche Sängere."))
        test_sentences.append(("Er ist der Sohn des Historikers und sächsischen Landespolitikers Dietmar Pellman.", "En ist das Kind ders Historikeres und sächsischen Landespolitikeres Dietmar Pellman."))
        test_sentences.append(("Nur eine von hundert kennt die Antwort darauf.", "Nur einey von hundert kennt die Antwort darauf."))
        test_sentences.append(("Er sagte das unter den gütigen Augen Mutter Teresas.", "En sagte das unter den gütigen Augen Elter Teresas."))
        test_sentences.append(("Männer und Frauen sowie Lehrerinnen und Lehrer", "Leute sowie Lehrerne"))
        test_sentences.append(("Rieman sollte zunächst wie sein Vater Theologe werden und hatte dazu Hebräisch gelernt.", "Rieman sollte zunächst wie ens Elter Theologere werden und hatte dazu Hebräisch gelernt."))
        test_sentences.append(("Ein guter Sohn, der hier wohnt, kommt bald.", "Ein gutes Kind, das hier wohnt, kommt bald."))
        test_sentences.append(("Der gute Sohn, der hier wohnt, kommt bald.", "Das gute Kind, das hier wohnt, kommt bald."))
        test_sentences.append(("Als Latino oder Latina will ich das nicht wissen.", "Als Latine will ich das nicht wissen."))
        test_sentences.append(("Als Mann oder Frau", "Als Person"))
        test_sentences.append(("Als Sohn oder Tochter will ich das nicht wissen.", "Als Kind will ich das nicht wissen."))
        test_sentences.append(("Mann oder Frau", "Person"))
        test_sentences.append(("Lehrer oder Lehrerin", "Lehrere"))
        test_sentences.append(("Die Tochter sieht ihren Onkel", "Das Kind sieht ens Tonke"))
        test_sentences.append(("Männer und Frauen sowie Lehrerinnen und Lehrer", "Leute sowie Lehrerne"))
        test_sentences.append(("Der Fahrer hat keine Fahrerlaubnis.", "De Fahrere hat keine Fahrerlaubnis."))
        test_sentences.append(("Siehst Du diesen Herrn?", "Siehst Du diese Person?"))
        test_sentences.append(("Sie nennt sich »Lehrer«.", "En nennt sich »Lehrere«."))
        test_sentences.append(("Nimue hatte vor, bei einem renommierten Barden in die Lehre zu gehen.","Nimue hatte vor, bei einerm renommierten Bardere in die Lehre zu gehen."))
        # "Junge"/"Mädchen" werden zu "junge Person" mit femininer Kongruenz:
        test_sentences.append(("Der Junge spielt.", "Die junge Person spielt."))
        test_sentences.append(("Ich sehe ein junges Mädchen.", "Ich sehe eine sehr junge Person."))
        test_sentences.append(("Die Jungs spielen.", "Die jungen Leute spielen."))
        # Steigerungsformen bleiben erhalten, sonst ginge der Vergleich verloren:
        test_sentences.append(("Ich sehe das jüngere Mädchen.", "Ich sehe die jüngere junge Person."))
        test_sentences.append(("Ich sehe das jüngste Mädchen.", "Ich sehe die jüngste junge Person."))
        # "Ehemann"/"Ehefrau" werden zu "Ehepartnere" und nicht zu "Eheperson":
        test_sentences.append(("Ihr Ehemann kommt.", "Ens Ehepartnere kommt."))
        test_sentences.append(("Die Ehefrauen kommen.", "Die Ehepartnerne kommen."))
        # Umlaut im Plural, aus maskuliner wie femininer Eingabeform:
        test_sentences.append(("Die Ärzte sind da.", "Die Ärzterne sind da."))
        test_sentences.append(("Die Ärztinnen sind da.", "Die Ärzterne sind da."))
        test_sentences.append(("Ich gehe zu den Zahnärzten.", "Ich gehe zu den Zahnärzternen."))
        # ... aber nicht bei Substantiven, deren maskuliner Plural keinen Umlaut hat:
        test_sentences.append(("Die Bäuerinnen kommen.", "Die Bauerne kommen."))
        # Abkürzungen sind keine Personenbezeichnungen:
        test_sentences.append(("Die DDR war ein Staat.", "Die DDR war ein Staat."))
        # "Einzelne" wird als substantiviertes Adjektiv erkannt:
        test_sentences.append(("Der Einzelne kann viel bewirken.", "De Einzelne kann viel bewirken."))
        # Im Dativ ohne Endung ist "Liebe" das Abstraktum, nicht das substantivierte Adjektiv:
        test_sentences.append(("Er tat es aus Liebe.", "En tat es aus Liebe."))
        # ... mit Endung dagegen schon; der Kasus stammt dann aus der Dependenzrelation:
        test_sentences.append(("Ich gebe es meiner Lieben.", "Ich gebe es meinerm Lieben."))
        # ... auch als Genitivattribut eines Nomens:
        test_sentences.append(("Das Buch meiner Lieben ist da.", "Das Buch meiners Lieben ist da."))
        # Die starke Endung "-er" schlägt einen Artikel, den ParZu im Relativsatz
        # fälschlich an das substantivierte Adjektiv gehängt hat:
        test_sentences.append(("Er gab ihm ein Geschenk, welches Zweiterer allerdings schon besaß.", "En gab em ein Geschenk, welches Zweiterey allerdings schon besaß."))
        test_sentences.append(("Er gab ihm ein Geschenk, das Zweiterer allerdings schon besaß.", "En gab em ein Geschenk, das Zweiterey allerdings schon besaß."))
        test_sentences.append(("Er gab ihm ein Amt, das Beamter gerne annahm.", "En gab em ein Amt, das Beamtey gerne annahm."))
        # Nach dem ein-Paradigma bleibt es dagegen schwach:
        test_sentences.append(("Ein Jugendlicher kommt.", "Ein Jugendliche kommt."))
        test_sentences.append(("Mein Verlobter kommt.", "Mein Verlobte kommt."))
        # ... und ein Artikel, der wirklich zum Wort gehört, ebenfalls:
        test_sentences.append(("Welcher Jugendliche kommt?", "Welchey Jugendliche kommt?"))
        # "Mannschaft" wird zu "Team", die abhängigen Wörter ins Neutrum:
        test_sentences.append(("Die Mannschaft gewinnt.", "Das Team gewinnt."))
        test_sentences.append(("Das Auto der Mannschaft ist rot.", "Das Auto des Teams ist rot."))
        test_sentences.append(("Die Fußballmannschaft gewinnt.", "Das Fußballteam gewinnt."))
        test_sentences.append(("Die Mannschaftsleitung entscheidet.", "Die Teamleitung entscheidet."))
        test_sentences.append(("Der Mannschaftskapitän kommt.", "De Teamkapitäne kommt."))
        # "Mannomann" ist ein Ausruf und keine Personenbezeichnung:
        test_sentences.append(("Mannomann, war das knapp!", "Mannomann, war das knapp!"))
        # "Hampelmann" wird zu "Hampelmensch", schwach dekliniert und im Maskulinum:
        test_sentences.append(("Der Hampelmann steht da.", "Der Hampelmensch steht da."))
        test_sentences.append(("Ich gebe dem Hampelmann das Buch.", "Ich gebe dem Hampelmenschen das Buch."))
        test_sentences.append(("Das Auto des Hampelmanns ist rot.", "Das Auto des Hampelmenschen ist rot."))
        test_sentences.append(("Die Hampelmänner stehen da.", "Die Hampelmenschen stehen da."))
        # Weitere Komposita auf "-mann", bei denen weder die Form auf "-frau" noch der Plural
        # auf "-leute" gebräuchlich ist:
        test_sentences.append(("Er war der Buhmann.","En war der Buhmensch."))
        test_sentences.append(("Der Biedermann schwieg.","Der Biedermensch schwieg."))
        test_sentences.append(("Der Schneemann schmilzt.","Der Schneemensch schmilzt."))
        test_sentences.append(("Die Schneemänner schmelzen.","Die Schneemenschen schmelzen."))
        test_sentences.append(("Der Weihnachtsmann kommt.","Der Weihnachtsmensch kommt."))
        test_sentences.append(("Der Butzemann erschreckt.","Der Butzemensch erschreckt."))
        test_sentences.append(("Er ist ein Strohmann.","En ist ein Strohmensch."))
        # Nach einer Wechselpräposition lässt ParZu den Kasus offen. Nominativ wäre die einzige
        # Form ohne "-en", deshalb wird dort der Akkusativ angenommen.
        test_sentences.append(("Ich glaube nicht an den Weihnachtsmann, aber ich glaube an den Schneemann.","Ich glaube nicht an den Weihnachtsmenschen, aber ich glaube an den Schneemenschen."))
        test_sentences.append(("Ich glaube an den Weihnachtsmann.","Ich glaube an den Weihnachtsmenschen."))
        test_sentences.append(("Ich denke an den Weihnachtsmann.","Ich denke an den Weihnachtsmenschen."))
        # Nach "vor", "zwischen" und den übrigen Präpositionen aus DATIVE_PREPOSITIONS bleibt es
        # beim Dativ.
        test_sentences.append(("Er steht vor dem Schneemann.","En steht vor dem Schneemenschen."))
        # Ein unangebundenes "ihr" ist das Dativpronomen, keine Possessivform:
        test_sentences.append(("Kannst Du ihr bitte sagen, dass ich komme.","Kannst Du em bitte sagen, dass ich komme."))
        test_sentences.append(("Ich gebe ihr das Buch.","Ich gebe em das Buch."))
        # Gegenproben: echte Possessivformen und das "ihr" der zweiten Person Plural
        test_sentences.append(("Ich sehe ihr Buch.","Ich sehe ens Buch."))
        test_sentences.append(("Ihr Buch ist gut.","Ens Buch ist gut."))
        test_sentences.append(("Ihr seid gekommen.","Ihr seid gekommen."))
        # Ein Dativ bei "sein" begleitet immer ein Prädikativ; fehlt das, ist das Substantiv
        # selbst das Prädikatsnomen und steht im Nominativ. Der Auslöser dafür steht in
        # test_reported_sentences_from_notes; hier nur die Gegenproben.
        test_sentences.append(("Es war den Leuten egal.","Es war den Leuten egal."))
        test_sentences.append(("Das ist Kindern egal.","Das ist Kindern egal."))
        # ParZu taggt das finite Verb als Adjektiv; der Grossschreibungs-Trick machte daraus ein
        # Substantiv ("anfreundetey"). Anrede-Adjektive haben dieselbe leere Merkmalsliste,
        # stehen aber vor einem Substantiv.
        test_sentences.append(("Ihn besuchten Mathematiker, mit denen er sich anfreundete und denen er half.","En besuchten Mathematikerne, mit denen en sich anfreundete und denen en half."))
        # Hängt der Artikel an der Konjunktion statt am Substantiv, wird er diesem zugeschlagen;
        # den Kasus gibt dann die Artikelform vor, nicht ParZus Angabe am Substantiv.
        test_sentences.append(("Eulers Mutter kam selbst aus einer gebildeten Familie, und der Vater hatte mathematische Interessen und bei Jakob I Bernoulli nicht nur Vorlesungen gehört, sondern sogar 1688 eine mathematische Dissertation verfasst.","Eulers Elter kam selbst aus einer gebildeten Familie, und de Elter hatte mathematische Interessen und bei Jakob I Bernoulli nicht nur Vorlesungen gehört, sondern sogar 1688 eine mathematische Dissertation verfasst."))
        test_sentences.append(("Ich helfe dem Lehrer und dem Schüler.","Ich helfe derm Lehrere und derm Schülere."))
        # Folgt auf ein vermeintliches "Genitiv Plural" ein Personenname, ist die Apposition
        # gemeint und damit der Singular. Der Fehler tritt nur im vollen Satz auf.
        test_sentences.append(("Zwischen Mai 2023 und Februar 2024 starben mindestens fünf politisch Inhaftierte an Haftbedingungen, so am 20. Februar 2024 der Oppositionspolitiker Igor Lednik.","Zwischen Mai 2023 und Februar 2024 starben mindestens fünf politisch Inhaftierte an Haftbedingungen, so am 20. Februar 2024 de Oppositionspolitikere Igor Lednik."))
        # Gegenstueck dazu: Hier ist der Genitiv Plural echt, denn er haengt an einem Substantiv
        # ("das Gericht"). Der Artikel muss also stehen bleiben.
        test_sentences.append(("Er erkannte seinen Fehler erst, als das Gericht der Nationalsozialisten Saul Cohen zu Tode verurteilte.","En erkannte ensen Fehler erst, als das Gericht der Nationalsozialisterne Saul Cohen zu Tode verurteilte."))
        # Doppelnennungen, bei denen auch das zweite Substantiv einen eigenen Artikel hat.
        test_sentences.append(("Der Lehrer oder die Lehrerin ist da.","De Lehrere ist da."))
        test_sentences.append(("Der gute Lehrer oder die gute Lehrerin ist da.","De gute Lehrere ist da."))
        test_sentences.append(("Ich sehe den Lehrer oder die Lehrerin.","Ich sehe de Lehrere."))
        test_sentences.append(("Ich helfe dem Lehrer oder der Lehrerin.","Ich helfe derm Lehrere."))
        test_sentences.append(("Die Lehrerin oder der Lehrer ist da.","De Lehrere ist da."))
        test_sentences.append(("Ein Lehrer oder eine Lehrerin kommt.","Ein Lehrere kommt."))
        test_sentences.append(("Die Bürgerinnen und die Bürger sind gefragt.","Die Bürgerne sind gefragt."))
        test_sentences.append(("Der Sohn oder die Tochter kommt.","Das Kind kommt."))
        test_sentences.append(("Der Kaufmann oder die Kauffrau kommt.","Die Kaufperson kommt."))
        test_sentences.append(("Der Lehrer oder die Lehrerin des Kindes ist da.","De Lehrere des Kindes ist da."))
        # Keine Doppelnennung: zwei Einzelpersonen als Subjekt eines pluralischen Verbs, und ein
        # Substantivpaar, das gar nicht zusammengehoert.
        test_sentences.append(("Der Lehrer und die Lehrerin sind da.","De Lehrere und de Lehrere sind da."))
        test_sentences.append(("Der Lehrer und die Schüler kamen.","De Lehrere und die Schülerne kamen."))
        test_sentences.append(("Der Lehrer, die Lehrerin und der Schüler kamen.","De Lehrere, de Lehrere und de Schülere kamen."))
        # Zusammengezogen wird nur, wenn beide Nennungen dieselben Attribute tragen.
        test_sentences.append(("Der alte kluge Lehrer oder die alte kluge Lehrerin kommt.","De alte kluge Lehrere kommt."))
        test_sentences.append(("Der gute Lehrer oder die schlechte Lehrerin kommt gleich.","De gute Lehrere oder de schlechte Lehrere kommt gleich."))
        test_sentences.append(("Der Lehrer oder die neue Lehrerin ist da.","De Lehrere oder de neue Lehrere ist da."))
        test_sentences.append(("Der gute Lehrer oder die Lehrerin kommt.","De gute Lehrere oder de Lehrere kommt."))
        test_sentences.append(("Der alte kluge Lehrer oder die kluge alte Lehrerin kommt.","De alte kluge Lehrere oder de kluge alte Lehrere kommt."))
        # split_prepositions zerlegt "vom", "im" und "am"; die Praeposition muss danach wieder
        # vollstaendig werden, auch wenn das Substantiv zu "-person" oder "-kind" wird.
        test_sentences.append(("Ich habe es vom Kaufmann gehört.","Ich habe es von der Kaufperson gehört."))
        test_sentences.append(("Im Kaufmann steckt viel Erfahrung.","In der Kaufperson steckt viel Erfahrung."))
        test_sentences.append(("Am Kaufmann lag es nicht.","An der Kaufperson lag es nicht."))
        # Aendert sich der Artikel selbst nicht, bleibt die Zusammenziehung stehen.
        test_sentences.append(("Ich habe es vom Sohn gehört.","Ich habe es vom Kind gehört."))
        test_sentences.append(("Im Sohn steckt viel Kraft.","Im Kind steckt viel Kraft."))
        test_sentences.append(("Ich habe es zum Sohn gesagt.","Ich habe es zum Kind gesagt."))
        test_sentences.append(("Fürs Erste kam der Lehrer.","Fürs Erste kam de Lehrere."))
        test_sentences.append(("Vorm Lehrer stand sie.","Vor derm Lehrere stand en."))
        # ParZu gibt "von" keinen Kasus mit. Ohne Ergänzung ging der Dativ verloren, und der
        # Kasus des Kopfes erreichte die abhängigen Wörter auf dem "-kind"- und dem
        # "-person"-Zweig ohnehin nicht.
        test_sentences.append(("Das Buch von der Tochter ist kaputt.","Das Buch vom Kind ist kaputt."))
        test_sentences.append(("Das Buch von der Lehrerin ist kaputt.","Das Buch von derm Lehrere ist kaputt."))
        test_sentences.append(("Das Buch von der Kauffrau ist kaputt.","Das Buch von der Kaufperson ist kaputt."))
        test_sentences.append(("Er sprach von der Tochter.","En sprach vom Kind."))
        # Präposition und dativisches "dem" ziehen sich zusammen ...
        test_sentences.append(("Bei der Tochter war es schön.","Beim Kind war es schön."))
        test_sentences.append(("In der Tochter steckt viel.","Im Kind steckt viel."))
        test_sentences.append(("Ich ging zu der Tochter.","Ich ging zum Kind."))
        # ... aber nicht zu den umgangssprachlichen Formen "vorm", "überm", "unterm", "hinterm".
        test_sentences.append(("Vor der Tochter stand er.","Vor dem Kind stand en."))
        # Der Ersatztext von hack_for_ordinal_numbers darf nicht in die Ausgabe gelangen.
        test_sentences.append(("Am 1. 2. 2020 kam der Lehrer.","Am 1. 2. 2020 kam de Lehrere."))
        test_sentences.append(("Der 43. und der 44. Präsident kamen.","Der 43. und de 44. Präsidente kamen."))
        # Gegenderte Formen von "ein" muessen wie ihre einfachen Entsprechungen behandelt werden.
        test_sentences.append(("Ein*eine Lehrende kam.","Ein Lehrende kam."))
        test_sentences.append(("Ein/eine Lehrende kam.","Ein Lehrende kam."))
        test_sentences.append(("Die Rolle eines*einer Lehrenden ist wichtig.","Die Rolle einers Lehrenden ist wichtig."))
        test_sentences.append(("Er sprach mit einem*einer Lehrenden.","En sprach mit einerm Lehrenden."))
        test_sentences.append(("Das Buch der Lehrer ist da.","Das Buch der Lehrerne ist da."))
        # Ein unangebundenes Relativpronomen nimmt den Numerus des Bezugsworts und ist im
        # Plural nicht markierbar:
        test_sentences.append(("Zur Sichtbarmachung der Geschlechter werden Bezeichnungsformen verwendet, die mit dem Geschlecht der referierten Personen (fachsprachlich: ihrem Sexus) übereinstimmen.","Zur Sichtbarmachung der Geschlechter werden Bezeichnungsformen verwendet, die mit dem Geschlecht der referierten Personen (fachsprachlich: ensem Sexus) übereinstimmen."))
        # Ein unangebundener Artikel vor einem artikellosen Substantiv gehört zu diesem und ist
        # nicht selbst markierbar:
        test_sentences.append(("Sie lernten sich eines Tages in einem Park kennen, als Jack ihr anbot, ihr die Bücher von der Schule nach Hause zu tragen.","Sie lernten sich eines Tages in einem Park kennen, als Jack em anbot, em die Bücher von der Schule nach Hause zu tragen."))
        test_sentences.append(("Der Knochenmann holt ihn.","Der Knochenmensch holt en."))
        test_sentences.append(("Der Saubermann redete.","Der Saubermensch redete."))
        test_sentences.append(("Dieser Blödmann stört.","Dieser Blödmensch stört."))
        test_sentences.append(("Der Pfeifenmann kam.","Der Pfeifenmensch kam."))
        test_sentences.append(("Er ist ein Weltmann.","En ist ein Weltmensch."))
        # "Wassermann" wird zu "Wassergeist". Ein Wassergeist ist keine Person, deshalb behält
        # das Wort seinen eigenen Artikel, anders als die übrigen Neologismen.
        test_sentences.append(("Der Wassermann taucht auf.","Der Wassergeist taucht auf."))
        test_sentences.append(("Die Wassermänner tauchen auf.","Die Wassergeister tauchen auf."))
        test_sentences.append(("Er sprach mit dem Wassermann.","En sprach mit dem Wassergeist."))
        # "Sohnemann" wird zu "Sprössling" und bekommt als Personenbezeichnung den Artikel "de",
        # so wie das gleichgebaute "de Flüchtling".
        test_sentences.append(("Der Sohnemann kam.","De Sprössling kam."))
        test_sentences.append(("Die Sohnemänner kamen.","Die Sprösslinge kamen."))
        # "Du"/"Ich" bleiben unverändert, die Apposition wird stark dekliniert ("-ey"):
        test_sentences.append(("Du Arme!","Du Armey!"))
        test_sentences.append(("Du Armer!","Du Armey!"))
        test_sentences.append(("Du Kranke!","Du Krankey!"))
        test_sentences.append(("Du Reisender!","Du Reisendey!"))
        test_sentences.append(("Ich Armer!","Ich Armey!"))
        # Nach dem endungslosen "ein" steht die starke Form, die das Genus verrät:
        test_sentences.append(("Vielleicht kocht ein Anderer.","Vielleicht kocht ein Andere."))
        # Gegenproben: Nach "der"/"die"/"das" steht die schwache Form, das Genus lässt sich
        # dort nicht aus der Endung ablesen.
        test_sentences.append(("Das Gute siegt.","Das Gute siegt."))
        test_sentences.append(("Ein Reisender kam.","Ein Reisende kam."))
        test_sentences.append(("Die Reisenden kamen.","Die Reisenden kamen."))
        test_sentences.append(("Der Flüchtling kam.","De Flüchtling kam."))
        # "Feuerwehrfrau" und "Feuerwehrleute" sind gebräuchlich, deshalb bleibt es bei "-person":
        test_sentences.append(("Der Feuerwehrmann kam.","Die Feuerwehrperson kam."))
        # Das Pronomen "jedermann", auch im Genitiv:
        test_sentences.append(("Jedermann weiß das.","Jedermensch weiß das."))
        test_sentences.append(("Das gefällt jedermann.","Das gefällt jedermensch."))
        test_sentences.append(("Das ist jedermanns Sache.","Das ist jedermenschs Sache."))
        # Grossgeschriebene Adjektive ohne Nomen darüber werden auch dann neutralisiert, wenn
        # ParZu sie nach dem Reparse weiter als Adjektiv führt ("Juli" ist auch ein Monat):
        test_sentences.append(("Willkommen, liebe Juli!", "Willkommen, liebey Juli!"))
        test_sentences.append(("Willkommen, liebe Kim!", "Willkommen, liebey Kim!"))
        # Ein Adjektiv an einem Eigennamen macht diesen auch ohne Artikel markierbar:
        test_sentences.append(("Hallo, liebe Sonja!", "Hallo, liebey Sonja!"))
        test_sentences.append(("Die liebe Sonja kommt.", "De liebe Sonja kommt."))
        # ... ebenso in der blossen Anrede, wo eine Apposition den Numerus verrät:
        test_sentences.append(("Lieber Thomas!", "Liebey Thomas!"))
        # ... und wenn ParZu das Genus des Adjektivs offenlässt:
        test_sentences.append(("Er gibt sich als heiliger Franz aus.", "En gibt sich als heiligey Franz aus."))
        # Namen, die ParZu als gewöhnliche Substantive taggt, obwohl sie nur Eigennamen sind:
        test_sentences.append(("Sie gibt sich als heilige Maria aus.", "En gibt sich als heiligey Maria aus."))
        # Namen, die zugleich gebräuchliche Substantive sind, zählen nur mit Anrede-Adjektiv:
        test_sentences.append(("Hallo, liebe Juli!", "Hallo, liebey Juli!"))
        test_sentences.append(("Liebe Rose!", "Liebey Rose!"))
        test_sentences.append(("Im Juli fahren wir weg.", "Im Juli fahren wir weg."))
        test_sentences.append(("Die schöne Rose blüht.", "Die schöne Rose blüht."))
        test_sentences.append(("Der graue Wolf heult.", "Der graue Wolf heult."))
        # "Mark" unterscheidet sich am Genus: der Mark ist ein Name, die/das Mark nicht:
        test_sentences.append(("Lieber Mark!", "Liebey Mark!"))
        test_sentences.append(("Der liebe Mark kommt.", "De liebe Mark kommt."))
        test_sentences.append(("Die Mark war die Währung.", "Die Mark war die Währung."))
        test_sentences.append(("Das Mark im Knochen ist weich.", "Das Mark im Knochen ist weich."))
        # "Frank" ist kein gebräuchliches Substantiv und braucht kein Anrede-Adjektiv:
        test_sentences.append(("Der nette Frank kommt.", "De nette Frank kommt."))
        # ... Ortsnamen bleiben davon unberührt, weil sie Neutra sind:
        test_sentences.append(("Wir besuchen das schöne Berlin.", "Wir besuchen das schöne Berlin."))
        # Zwei Einzelpersonen als Subjekt eines pluralischen Verbs werden nicht wie eine
        # Doppelnennung zusammengezogen:
        test_sentences.append(("Wo sind Mutter und Vater?", "Wo sind Elter und Elter?"))
        test_sentences.append(("Wo sind Sohn und Tochter?", "Wo sind Kind und Kind?"))
        # ... bei singularischem Verb bleibt die Zusammenführung dagegen richtig:
        test_sentences.append(("Wo ist Mutter oder Vater?", "Wo ist Elter?"))
        # ... und echte Doppelnennungen im Plural sind unberührt:
        test_sentences.append(("Die Bürgerinnen und Bürger stimmen ab.", "Die Bürgerne stimmen ab."))
        # Jedes Adjektiv gilt bei eindeutigem Genus als substantiviert, nicht nur die kuratierte Liste:
        test_sentences.append(("Die Reisende steigt ein.", "De Reisende steigt ein."))
        test_sentences.append(("Der Betroffene klagt.", "De Betroffene klagt."))
        test_sentences.append(("Die Überlebende berichtet.", "De Überlebende berichtet."))
        test_sentences.append(("Katharina die Große kam.", "Katharina de Große kam."))
        # ... im Neutrum bezeichnet es keine Person:
        test_sentences.append(("Das Gute siegt.", "Das Gute siegt."))
        # ... und deadjektivische Abstrakta bleiben aussen vor:
        test_sentences.append(("Die Ebene ist flach.", "Die Ebene ist flach."))
        test_sentences.append(("Die Klasse lacht.", "Die Klasse lacht."))
        test_sentences.append(("Auf diese Weise geht es.", "Auf diese Weise geht es."))
        # Auch im Dativ, wo Maskulinum und Neutrum zusammenfallen, greift die kuratierte Liste:
        test_sentences.append(("Die Reisende sprach mit dem Betroffenen.", "De Reisende sprach mit derm Betroffenen."))
        test_sentences.append(("Er half dem Beteiligten.", "En half derm Beteiligten."))
        # "Linke" ist mit bestimmtem Artikel im Femininum die Partei oder die Hand ...
        test_sentences.append(("Die Linke fordert das.", "Die Linke fordert das."))
        test_sentences.append(("Der Linken gefällt das.", "Der Linken gefällt das."))
        # ... sonst eine Person:
        test_sentences.append(("Der Linke fordert das.", "De Linke fordert das."))
        test_sentences.append(("Eine Linke fordert das.", "Ein Linke fordert das."))
        # Fehlt ParZu das Genus, wird es an der Form des Determinierers abgelesen:
        test_sentences.append(("Jede Linke fordert das.", "Jedey Linke fordert das."))
        test_sentences.append(("Jede Reisende steigt ein.", "Jedey Reisende steigt ein."))
        test_sentences.append(("Meine Linke schmerzt.", "Meine Linke schmerzt."))
        # ... "jedes" zeigt ein Neutrum an und damit keine Person:
        test_sentences.append(("Jedes Gute hat ein Ende.", "Jedes Gute hat ein Ende."))
        # Der von split_prepositions abgespaltene Artikel ("im" wird zu "in dem") ist kein
        # eigenständiges Wort und darf nicht markierbar sein:
        test_sentences.append(("Er kam im Anschluss an die Sitzung.", "En kam im Anschluss an die Sitzung."))
        # "Omi" darf nicht mitten in einem Wort anschlagen ("NationalkOMItees"):
        test_sentences.append(("Das Bild des Nationalkomitees ist alt.", "Das Bild des Nationalkomitees ist alt."))
        # ... als eigenes Wort und als Kopf eines Kompositums aber schon:
        test_sentences.append(("Meine Omi kommt.", "Mein Owi kommt."))
        test_sentences.append(("Die Lieblingsomi kommt.", "De Lieblingsowi kommt."))
        # "ihr" bleibt markierbar, auch wenn es sich nicht auf eine Person bezieht:
        test_sentences.append(("Die Zeitschriften stellten ihr Erscheinen ein.", "Die Zeitschriften stellten ens Erscheinen ein."))
        # Altersangaben: die Grossschreibung steht hinter der Zahl, das Adjektiv im zweiten Teil:
        test_sentences.append(("Der 37-Jährige sagte das.", "De 37-Jährige sagte das."))
        test_sentences.append(("Die 18-Jährige gewann.", "De 18-Jährige gewann."))
        test_sentences.append(("Der 37-jährige Mann sagte das.", "Die 37-jährige Person sagte das."))
        # Ein Adjektiv auf "-er" im Maskulinum zeigt den Singular an, den ParZu offenlässt:
        test_sentences.append(("Du kleiner Lehrer!", "Du kleiney Lehrere!"))
        # ... im Plural bleibt es beim Plural:
        test_sentences.append(("Kleine Lehrer kommen.", "Kleine Lehrerne kommen."))
        test_sentences.append(("Die Arbeit kleiner Lehrer ist wichtig.", "Die Arbeit kleiner Lehrerne ist wichtig."))
        for i,test in enumerate(test_sentences):
            print(f"Testing sentence {i + 1}.")
            input_text = hack_for_ordinal_numbers(test[0])
            input_text_with_split_prepositions = split_prepositions(input_text)
            input_text_with_split_prepositions = remove_special_character_gendering(input_text_with_split_prepositions)
            parse = get_parse(input_text_with_split_prepositions)

            modified_text, capitalized_words, glauben, change = search_lonely_adjectives(parse,input_text)
            if not change:
                marking_tool = Marking_Tool(parse[0],{},[])
                marked_nouns = mark_nouns(parse,[],[])
            else:
                print("Parsing again with capitalized adjectives.")
                modified_text_with_split_prepositions = split_prepositions(modified_text)
                modified_text_with_split_prepositions = remove_special_character_gendering(modified_text_with_split_prepositions)
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

    # Bei ungrammatischer Eingabe lässt ParZu den Kasus offen. Der Zugriff auf die Paradigmen
    # lieferte dann None, und die Übersetzung brach ab, statt einen Nominativ anzunehmen.
    def test_ungrammatical_input_does_not_crash(self):
        for text in ("Sie ist ein dumme Frau.",
                     "Er ist ein dumme Mann.",
                     "Ich sehe ein dumme Frau."):
            remaining = text
            for parse_list in get_parse(remove_special_character_gendering(split_prepositions(text))):
                marking_tool = Marking_Tool(parse_list, {}, [])
                remaining = Marking_Tool.find_realizations(marking_tool, remaining)
                marked = marking_tool.get_marking_form(0)
                for position, component in re.findall(r'id="\d+\|(\d+)\|(-?\d+)"', marked):
                    # Darf keine Exception werfen:
                    marking_tool.neutralize_nounphrase(int(position) - 1, [int(component)])

    # Eingaben aus den Fehlermeldungen in reports/reports.txt, die die öffentliche Version zum
    # Absturz brachten. Allen gemeinsam ist, dass ParZu die Merkmale eines Wortes ganz offen
    # lässt oder ein Zeichen im Eingabetext nicht wiedergefunden wird; geprüft wird deshalb nur,
    # dass keine Exception fliegt, nicht eine bestimmte Ausgabe.
    def test_reported_inputs_do_not_crash(self):
        for text in (
                # Trennstriche aus einer PDF-Kopie: "deren" bekommt keine Merkmale.
                "Über deren Auto-s wird gesprochen.",
                # "als" nach einem Relativpronomen: dessen Merkmale sind anders angeordnet
                # als die eines Personalpronomens.
                "Die Leute, die als Reisende kommen, warten.",
                # Typografische Anführungszeichen und Gedankenstriche um ein gegendertes Wort.
                "Das Wort “gender” ist schwierig.",
                "Das Wort ‚gender‘ ist schwierig.",
                "Das Wort –gender– ist schwierig.",
                # Durchgehende Kleinschreibung: "anderen" bekommt keine Merkmale.
                "der spieler darf sich eine der karten vor einem anderen spieler anschauen"):
            remaining = text
            for parse_list in get_parse(remove_special_character_gendering(split_prepositions(text))):
                marking_tool = Marking_Tool(parse_list, {}, [])
                remaining = Marking_Tool.find_realizations(marking_tool, remaining)
                marked = marking_tool.get_marking_form(0)
                for position, component in re.findall(r'id="\d+\|(\d+)\|(-?\d+)"', marked):
                    # Darf keine Exception werfen:
                    marking_tool.neutralize_nounphrase(int(position) - 1, [int(component)])

    # ParZu bindet in diesem Satz den Artikel "Die" nicht an "Akademie" an und hängt den Beinamen
    # "Großen" als Attribut an ein späteres Substantiv. Der Ablauf hier entspricht dem der
    # Anwendung: eine einzige Marking_Tool-Instanz, die genau einmal markiert.
    def test_dangling_article_and_epithet(self):
        text = ("Die von Peter dem Großen gegründete Akademie in Sankt Petersburg sollte die "
                "Ausbildung in Russland verbessern und den wissenschaftlichen Vorsprung "
                "Westeuropas aufholen.")
        parse = get_parse(remove_special_character_gendering(split_prepositions(text)))
        marking_tool = Marking_Tool(parse[0], {}, [])
        Marking_Tool.find_realizations(marking_tool, text)
        marked = marking_tool.get_marking_form(0)
        selection = [(int(a), int(b)) for a, b in re.findall(r'id="\d+\|(\d+)\|(-?\d+)"', marked)]
        done = []
        for position, component in selection:
            if position not in done:
                components = [c for p, c in selection if p == position]
                marking_tool.neutralize_nounphrase(position - 1, components)
                done.append(position)
        output = marking_tool.get_sentence()
        self.assertIn("derm Großen", output, "Der Beiname wurde nicht neutralisiert")
        self.assertNotIn("Diey", output, "Der nicht angebundene Artikel wurde neutralisiert")

    # ParZus Tokenizer trennt an allen Unicode-Leerzeichen. Kannte die Zuordnung der Wörter auf
    # den Eingabetext eines davon nicht, geriet sie aus dem Tritt und brach mit einer Exception ab.
    def test_unicode_whitespace_is_handled(self):
        for codepoint in (0x2000, 0x2009, 0x202F, 0x205F, 0x3000, 0x2028, 0x2029, 0x0085):
            text = "Der Lehrer kommt." + chr(codepoint) + "Er ist alt."
            remaining = text
            for parse_list in get_parse(remove_special_character_gendering(split_prepositions(text))):
                marking_tool = Marking_Tool(parse_list, {}, [])
                # Wirft eine Exception, sobald ein Wort im Eingabetext nicht gefunden wird:
                remaining = Marking_Tool.find_realizations(marking_tool, remaining)

    # HTML aus dem Eingabetext darf nicht ungefiltert in die Markierungsansicht gelangen,
    # sonst liesse sich über den Eingabetext beliebiges Markup einschleusen.
    def test_html_in_input_is_escaped(self):
        text = 'Der Lehrer <img src=x onerror=alert(1)> und <!-- Kommentar --> die Frau.'
        parse = get_parse(remove_special_character_gendering(split_prepositions(text)))
        marking_tool = Marking_Tool(parse[0], {}, [])
        Marking_Tool.find_realizations(marking_tool, text)
        form = marking_tool.get_marking_form(0)
        # Die spitzen Klammern sind entscheidend: maskiert bleibt der Rest wirkungsloser Text.
        for raw in ["<img", "<!--", "</textarea>"]:
            self.assertNotIn(raw, form, f"{raw!r} steht ungefiltert im Markierungsformular")
        self.assertIn("&lt;img", form, "Das eingegebene Markup fehlt in maskierter Form")

    def test_markable_words_are_highlightable(self):
        text = "Ich helfe meiner alten Nachbarin."
        parse = get_parse(remove_special_character_gendering(split_prepositions(text)))
        marking_tool = Marking_Tool(parse[0], {}, [])
        Marking_Tool.find_realizations(marking_tool, text)
        form = marking_tool.get_marking_form(0)
        # Auswählbare Wörter tragen die Klasse, an der das Stylesheet den gelben Hintergrund und
        # den Wechsel auf lila festmacht -- unterstrichen werden sie nicht mehr.
        self.assertIn('<span class="markable">Nachbarin</span>', form)
        self.assertNotIn("<u>", form, "Die Unterstreichung ist noch im Markierungsformular")
        # Der Wechsel auf lila haengt daran, dass das Label unmittelbar auf sein Kaestchen folgt.
        self.assertRegex(form, r'<input type="checkbox"[^>]*>\s*<label ')

    def test_neuter_relative_pronoun_is_not_markable(self):
        # "was" bezeichnet keine Person. ParZu bindet es hier an keine Nominalphrase an, wodurch
        # es in den Zweig für freistehende Relativpronomen fiel -- der prüfte das Genus nicht.
        text = ("In der direkten Reaktion darauf war aus Politik und Feuilletons wenig zu hören, "
                "was man nicht schon tausend Mal gehört hätte.")
        parse = get_parse(remove_special_character_gendering(split_prepositions(text)))
        marking_tool = Marking_Tool(parse[0], {}, [])
        Marking_Tool.find_realizations(marking_tool, text)
        form = marking_tool.get_marking_form(0)
        markable = re.findall(r'<span class="markable">([^<]*)</span>', form)
        self.assertNotIn("was", markable, "\"was\" ist markierbar")
        # "man" soll dagegen weiterhin markierbar sein.
        self.assertIn("man", markable, "\"man\" ist nicht mehr markierbar")

    # Der Satz löst den Fehler nur in voller Länge aus, enthält dann aber weitere, hier nicht
    # betroffene Schwächen ("Bürgermeister" wird zerlegt). Geprüft wird deshalb nur die Stelle,
    # um die es geht: ParZu macht "Soldaten" zum Dativobjekt von "sein", woraus der Dativ Plural
    # "Soldaternen" wurde.
    # Die Wörter, die im Kästchen einer Doppelnennung aufgehen, wurden früher schon beim Erzeugen
    # des Formulars aus dem Ausgabetext entfernt. Wählte der Benutzer das Kästchen nicht aus, fehlte
    # die halbe Doppelnennung: "Die Bürgerinnen und Bürger stimmen ab." wurde zu "Die Bürgerinnen
    # stimmen ab."
    def test_unselected_double_naming_stays_complete(self):
        for sentence in ["Die Bürgerinnen und Bürger stimmen ab.",
                         "Der Lehrer oder die Lehrerin ist da.",
                         "Der Sohn oder die Tochter kommt.",
                         "Der Kaufmann oder die Kauffrau kommt.",
                         "Liebe Kolleginnen und Kollegen!"]:
            self.assertEqual(neutralize_all(sentence, select=lambda *_: False), sentence,
                             "Ohne Auswahl muss der Text unverändert bleiben")

    def test_double_naming_survives_partial_selection(self):
        # Nur das zweite Kästchen ("Lehrer") auswählen; die Doppelnennung davor bleibt stehen.
        text = "Die Bürgerinnen und Bürger trafen den Lehrer."
        self.assertEqual(neutralize_all(text, select=lambda satz, pos: pos > 3),
                         "Die Bürgerinnen und Bürger trafen de Lehrere.")
        # Nur die Doppelnennung auswählen; "den Lehrer" bleibt stehen.
        self.assertEqual(neutralize_all(text, select=lambda satz, pos: pos <= 3),
                         "Die Bürgerne trafen den Lehrer.")

    def test_predicate_after_sein_is_nominative(self):
        text = ("Damals waren es Soldaten aus den USA, Italien, Polen und Ungarn, die zwischen "
                "den Fronten standen, als gewalttätige Hooligans, aufgepeitscht auch von lokalen "
                "serbischen Politikern, den albanischen Bürgermeister vertreiben wollten.")
        ausgabe = neutralize_all(text)
        self.assertIn("Soldaterne", ausgabe)
        self.assertNotIn("Soldaternen", ausgabe)

    def test_output_highlights_only_the_changed_parts(self):
        # Nur der geänderte Teil eines Wortes wird hervorgehoben; wird ausschliesslich gestrichen,
        # bleibt kein Stück übrig und das ganze Wort wird hervorgehoben.
        faelle = [("Nachbarin", "Nachbare", 'Nachbar<span class="changed">e</span>'),
                  ("meiner", "meinerm", 'meiner<span class="changed">m</span>'),
                  ("Mutter", "Elter", '<span class="changed">El</span>ter'),
                  ("der", "de", '<span class="changed">de</span>'),
                  ("Frau", "Person", '<span class="changed">Person</span>'),
                  ("alten", "alten", "alten"),
                  ("und", "", ""),
                  # "en" wird immer ganz hervorgehoben, damit es unabhängig von der Quellform
                  # gleich aussieht -- über den gemeinsamen Anfang "e" bliebe bei "er" nur das
                  # "n" farbig, bei "sie" dagegen das ganze Wort.
                  ("er", "en", '<span class="changed">en</span>'),
                  ("Er", "En", '<span class="changed">En</span>'),
                  ("sie", "en", '<span class="changed">en</span>'),
                  ("Sie", "En", '<span class="changed">En</span>'),
                  ("ihn", "en", '<span class="changed">en</span>'),
                  # Dasselbe gilt für den Dativ "em" aus "ihm" und "ihr".
                  ("ihm", "em", '<span class="changed">em</span>'),
                  ("ihr", "em", '<span class="changed">em</span>'),
                  ("Ihm", "Em", '<span class="changed">Em</span>'),
                  # Ein unverändertes "en" bleibt ohne Hervorhebung.
                  ("en", "en", "en"),
                  ("em", "em", "em"),
                  # "einerm" ist absichtlich nicht in der Regel: Dass sich nur ein Buchstabe
                  # geändert hat, bleibt sichtbar.
                  ("einem", "einerm", 'eine<span class="changed">r</span>m'),
                  ("einer", "einerm", 'einer<span class="changed">m</span>')]
        for original, neutralized, expected in faelle:
            self.assertEqual(Marking_Tool.highlight_change(original, neutralized), expected,
                             f"{original!r} -> {neutralized!r}")
        # Eingegebenes Markup darf auch hier nicht durchschlagen.
        highlighted = Marking_Tool.highlight_change("<b>Lehrerin", "<b>Lehrere")
        self.assertNotIn("<b>", highlighted)
        self.assertIn("&lt;b&gt;", highlighted)


# Übersetzt einen Text vollständig, so wie es /translate_directly tut: markieren, alle Kästchen
# auswählen, neutralisieren. Anders als die Satzpaar-Schleife oben verarbeitet die Funktion auch
# mehrsätzige Eingaben und gibt nur den Ausgabetext zurück.
def neutralize_all(text: str, select=None) -> str:
    """select entscheidet je (Satznummer, Position), ob das Kästchen ausgewählt wird.
    Ohne Angabe wird alles ausgewählt -- wie /translate_directly."""
    input_text = hack_for_ordinal_numbers(text)
    parse = get_parse(remove_special_character_gendering(split_prepositions(input_text)))
    modified_text, capitalized_words, glauben, change = search_lonely_adjectives(parse, input_text)
    if change:
        parse = get_parse(remove_special_character_gendering(split_prepositions(modified_text)))
        remaining = modified_text
    else:
        remaining = input_text
    marking_tools, marked = [], ""
    for i, parse_list in enumerate(parse):
        marking_tool = Marking_Tool(parse_list, {}, [])
        remaining = Marking_Tool.find_realizations(marking_tool, remaining)
        for address in capitalized_words:
            if i == address[0]:
                marking_tool.parse_list[address[1]][2] = marking_tool.parse_list[address[1]][2].lower()
                marking_tool.parse_list[address[1]][-2] = marking_tool.parse_list[address[1]][-2].lower()
        marking_tools.append(marking_tool)
        marked += marking_tool.get_marking_form(i)
    selected = [(int(a), int(b), int(c)) for a, b, c
                in re.findall(r'id="(\d+)\|(\d+)\|(-?\d+)"', marked)]
    done = set()
    for sentence_number, position, _ in selected:
        if (sentence_number, position) in done:
            continue
        if select is not None and not select(sentence_number, position):
            continue
        done.add((sentence_number, position))
        components = [c for s, p, c in selected if s == sentence_number and p == position]
        marking_tools[sentence_number].neutralize_nounphrase(position - 1, components)
    return undo_hack_for_ordinal_numbers("".join(t.get_sentence() for t in marking_tools))


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
                # replace artificial "schreib" by original "glaub"
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"eschrieben", "eglaubt", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"Schreib", "Glaub", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][2] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"eschrieben", "eglaubt", marking_tool.parse_list[glauben_address[1]][-2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][-2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"Schreib", "Glaub", marking_tool.parse_list[glauben_address[1]][-2])
                # replace artificial "sag" by original "zeig"
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"sag", "zeig", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"Sag", "Zeig", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][2] = re.sub(r"sag", "zeig", marking_tool.parse_list[glauben_address[1]][2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"sag", "zeig", marking_tool.parse_list[glauben_address[1]][-2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"Sag", "Zeig", marking_tool.parse_list[glauben_address[1]][-2])
        #sentence_data.add_marking_tool(sentence_number, marking_tool)
        marking_form += marking_tool.get_marking_form(sentence_number)
        sentence_number += 1
    return marking_form

if __name__ == "__main__":
    unittest.main()

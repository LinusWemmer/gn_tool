from flask import Flask, render_template, request, url_for, redirect, session
from marking_tool import Marking_Tool
from sentence_data import Sentence_Data
from flask_session import Session

import parzu_class as parzu
import re
import sys
import os
import traceback
import redis


app = Flask(__name__)
app.config.from_pyfile('key_config.py')
app.secret_key = app.config['SECRET_KEY']

app.config['SESSION_TYPE'] = 'redis'  # Use Redis for session storage
app.config['SESSION_PERMANENT'] = False  # Don't make the sessions permanent
app.config['SESSION_USE_SIGNER'] = True  # Securely sign the session
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')  # Use the local Redis server

Session(app)

sentence_data = Sentence_Data()
options = parzu.process_arguments()
ParZu = parzu.Parser(options)

def get_parse(text: str):
    sentences = ParZu.main(text)
    formatted_sentences = []
    for sentence in sentences:
        words = sentence.split("\n")
        words = words[:-2]
        parse_list = []
        for word in words:
           parse_list.append(word.split("\t"))
        formatted_sentences.append(parse_list)
    return formatted_sentences

# The following function ensures that whitespace in the input is visible in the output.
def replace_whitespace_outside_html_tags(text):
    def replace_whitespace(match):
        # If it's an HTML tag, return it unchanged
        if match.group(0).startswith('<'):
            return match.group(0)
        # Otherwise, it's text, so replace the whitespaces
        else:
            return match.group(0).replace('  ', '&nbsp; ').replace('  ', '&nbsp; ').replace('\n', '<br/>')

    # Use regex to find HTML tags and non-tag parts
    pattern = r'(<[^>]+>|[^<]+)'
    return re.sub(pattern, replace_whitespace, text)

# The following function capitalizes adjectives that do not modify a noun. It is a hack that ensures that
# adjectives in conjunctions like "netten" in "einen netten und einen unfreundlichen Kollegen" can be
# neutralized. The function also replaces "glauben" by "schreiben" internally, since ParZu does not
# recognize the dative object of "glauben" as such. Similarly it replaces "zeigen" bei "sagen".
def search_lonely_adjectives(parse: list, input_text: str):
        change = False
        modified_text = ""
        capitalized_words = []
        glauben = []
        for sentence_number, parse_list in enumerate(parse):
            marking_tool = Marking_Tool(parse_list,{})
            input_text = Marking_Tool.find_realizations(marking_tool,input_text)
            unter = False
            alles = False
            an = False
            am = False
            for word_number, word in enumerate(marking_tool.parse_list):
                # Wir setzen alle Adjektive, die nicht von einem Nomen abhängen und nicht im Neutrum stehen, auf groß.
                # Ausnahmen sind "am ...sten", "unter anderem" und "alles andere".
                if ((word[3] == "ADJA" and not (am and (word[1].endswith("sten")))) or (word[2] == "andere" and not unter and not alles)) and word[1][0].islower() and lonely_adjective(parse,sentence_number,word_number) and not "Neut" in word[5]:
                    word[1] = word[1].capitalize()
                    capitalized_words.append([sentence_number,word_number])
                    change = True
                if word[2].lower() == "unter":
                    unter = True
                else:
                    unter = False
                if word[2].lower() == "alle": # This covers "alles" and declined forms of it.
                    alles = True
                else:
                    alles = False
                if an and word[1].lower() == "dem":
                    am = True
                else:
                    am = False
                if word[2].lower() == "an":
                    an = True
                else:
                    an = False
            # Wir ersetzen "glauben" intern durch "schreiben", da ParZu Dativ-Objekte von "glauben" häufig nicht als solche erkennt.
            for word_number, word in enumerate(marking_tool.parse_list):
                if word[2] == "glauben":
                    word[1] = re.sub(r"eglaubt", "eschrieben", word[1])
                    word[1] = re.sub(r"glaub", "schreib", word[1])
                    word[1] = re.sub(r"Glaub", "Schreib", word[1])
                    glauben.append([sentence_number,word_number])
                    change = True
                if word[2] == "zeigen":
                    word[1] = re.sub(r"zeig", "sag", word[1])
                    word[1] = re.sub(r"Zeig", "Sag", word[1])
                    glauben.append([sentence_number,word_number])
                    change = True
            modified_text += marking_tool.get_internal_sentence()
        return modified_text, capitalized_words, glauben, change

# The following function checks whether an adjective is lonely, i.e. whether it does not modify a noun.
def lonely_adjective(parse: list, sentence_number: int, word_number: int):
    parse_list = parse[sentence_number]
    word = parse_list[word_number]
    print("determining status of adjective:", word)
    if int(word[6]) == 0 or not parse_list[int(word[6])-1][3] in ["N", "KON"]:
        print("adjective is lonely, case 1")
        return True
    elif parse_list[int(word[6])-1][3] == "KON" and (int(parse_list[int(word[6])-1][6]) == 0 or int(parse_list[int(parse_list[int(word[6])-1][6])-1][6]) == 0 or parse_list[int(parse_list[int(parse_list[int(word[6])-1][6])-1][6])-1][3] != "N"):
        print("adjective is lonely, case 2")
        return True
    else:
        print("adjective is not lonely")
        return False

# The following function creates the marking form for the user interface, i.e. the form that allows the user to select
# the words that should be neutralized.
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
        marking_form += marking_tool.get_marking_form(sentence_number)
        session[f"markingtool{sentence_number}"] = marking_tool.__dict__
        sentence_number += 1
    session["sentence_number"] = sentence_number
    return marking_form

# The following function is a hack to ensure that ParZu doesn't cut sentences off at ordinal numbers
# with dots, e.g. "43. Präsident". The function replaces the dots in such positions with "-tägig rosa".
# This replacement is undone before the final output.
def hack_for_ordinal_numbers(input_text: str) -> str:
    ordinal_number_pattern = r' (\d\d?\d?)\. '
    input_text = re.sub(ordinal_number_pattern, r' \1-tägig rosa ', input_text)
    return input_text

def undo_hack_for_ordinal_numbers(input_text: str) -> str:
    ordinal_number_pattern = r' (\d\d?\d?)-tägig rosa '
    input_text = re.sub(ordinal_number_pattern, r' \1. ', input_text)
    return input_text

# The following function splits prepositions that are conjoined with articles. This is necessary because ParZu
# does not recognize the preposition and the article as separate words, but we need to consider them separately
# for the neutralization.
# Additionally we here replace "seins" and "ihrs" by "seines" and "ihres", because ParZu does not recognize
# "seins" and "ihrs" as possible neuter forms of "seiner" and "ihrer".
def split_prepositions(input_text: str) ->str:
    quotation_mark_pattern = r'„|“|”'
    input_text = re.sub(quotation_mark_pattern, '"', input_text)
    words = re.split(r"(\s|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_])", input_text)
    output = ""
    for word in words:
        if word =="beim":
            output += "bei dem"
        elif word == "Beim":
            output +="Bei dem"
        elif word == "zum":
            output += "zu dem"
        elif word == "Zum":
            output += "Zu dem"
        elif word == "zur":
            output += "zu der"
        elif word == "Zur":
            output += "Zu der"
        elif word == "im":
            output += "in dem"
        elif word == "Im":
            output += "In dem"
        elif word == "ins":
            output += "in das"
        elif word == "Ins":
            output += "In das"
        elif word == "vom":
            output += "von dem"
        elif word == "Vom":
            output += "Von dem"
        elif word == "vorm":
            output += "vor dem"
        elif word == "Vorm":
            output += "Vor dem"
        elif word == "am":
            output += "an dem"
        elif word == "Am":
            output += "An dem"
        elif word == "ans":
            output += "an das"
        elif word == "Ans":
            output += "An das"
        elif word == "aufs":
            output += "auf das"
        elif word == "Aufs":
            output += "Auf das"
        elif word == "fürs":
            output += "für das"
        elif word == "Fürs":
            output += "Für das"
        elif word == "seins":
            output += "seines"
        elif word == "ihrs":
            output += "ihres"
        elif word == "Ihrs":
            output += "Ihres"
        else:
            output += word
    return output

# The following function removes forms of gendering involving special characters, such as "Lehrer*innen" and "er/sie".
# They are replaced by the corresponding female form, e.g. "Lehrerinnen" and "sie".
def remove_special_character_gendering(input_text: str) ->str:
    input_text = re.sub(r"([a-zA-ZäöüßÄÖÜẞ]{3})[*_:/]in", r"\1in", input_text)
    input_text = re.sub(r"([a-zA-ZäöüßÄÖÜẞ]{3})/-in", r"\1in", input_text)
    input_text = re.sub(r"([a-zA-ZäöüßÄÖÜẞ]{3})\(in\)", r"\1in", input_text)
    input_text = re.sub(r"([a-zA-ZäöüßÄÖÜẞ]{3})\(inn\)(?=en($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"\1inn", input_text)
    input_text = re.sub(r"([a-zA-ZäöüßÄÖÜẞ]{3})\(innen\)", r"\1innen", input_text)
    input_text = re.sub(r"er[/*_:]sie", "sie", input_text)
    input_text = re.sub(r"sie[/*_:]er", "sie", input_text)
    input_text = re.sub(r"Er[/*_:][sS]ie", "Sie", input_text)
    input_text = re.sub(r"Sie[/*_:][eE]r", "Sie", input_text)
    input_text = re.sub(r"ihm[/*_:]ihr", "ihr", input_text)
    input_text = re.sub(r"ihr[/*_:]ihm", "ihr", input_text)
    input_text = re.sub(r"Ihm[/*_:][iI]hr", "Ihr", input_text)
    input_text = re.sub(r"Ihr[/*_:][iI]hm", "Ihr", input_text)
    input_text = re.sub(r"ihn[/*_:]sie", "sie", input_text)
    input_text = re.sub(r"sie[/*_:]ihn", "sie", input_text)
    input_text = re.sub(r"Ihn[/*_:][sS]ie", "Sie", input_text)
    input_text = re.sub(r"Sie[/*_:][iI]hn", "Sie", input_text)
    input_text = re.sub(r"der[/*_:]die", "die", input_text)
    input_text = re.sub(r"die[/*_:]der", "die", input_text)
    input_text = re.sub(r"Der[/*_:][dD]ie", "Die", input_text)
    input_text = re.sub(r"Die[/*_:][dD]er", "Die", input_text)
    input_text = re.sub(r"des[/*_:]der", "der", input_text)
    input_text = re.sub(r"der[/*_:]des", "der", input_text)
    input_text = re.sub(r"Des[/*_:][dD]er", "Der", input_text)
    input_text = re.sub(r"Der[/*_:][dD]es", "Der", input_text)
    input_text = re.sub(r"dem[/*_:]der", "der", input_text)
    input_text = re.sub(r"der[/*_:]dem", "der", input_text)
    input_text = re.sub(r"Dem[/*_:][dD]er", "Der", input_text)
    input_text = re.sub(r"Der[/*_:][dD]em", "Der", input_text)
    input_text = re.sub(r"den[/*_:]die", "die", input_text)
    input_text = re.sub(r"die[/*_:]den", "die", input_text)
    input_text = re.sub(r"Den[/*_:][dD]ie", "Die", input_text)
    input_text = re.sub(r"Die[/*_:][dD]en", "Die", input_text)
    # eine/ein(er):
    input_text = re.sub(re.compile(r"([mdks])?([eE])in(er|en)?[/*_:]\1[eE]ine", re.IGNORECASE), r"\1\2ine", input_text)
    input_text = re.sub(re.compile(r"([mdks])?([eE])ine[/*_:]\1[eE]in(er|en)?", re.IGNORECASE), r"\1\2ine", input_text)
    input_text = re.sub(re.compile(r"([mdks])?([eE])ine[sm]][/*_:]\1[eE]iner", re.IGNORECASE), r"\1\2iner", input_text)
    input_text = re.sub(re.compile(r"([mdks])?([eE])iner[/*_:]\1[eE]ine[sm]]", re.IGNORECASE), r"\1\2iner", input_text)
    input_text = re.sub(r"[*_:/]e(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"e", input_text)
    input_text = re.sub(r"e[*_:/][rn](?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"e", input_text)
    input_text = re.sub(r"er[*_:/]s(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"er", input_text)
    input_text = re.sub(r"es[*_:/]r(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"er", input_text)
    input_text = re.sub(r"er[*_:/]m(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"er", input_text)
    input_text = re.sub(r"em[*_:/]r(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"er", input_text)
    input_text = re.sub(r"\(e\)(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"e", input_text)
    input_text = re.sub(r"e\(r\)(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"e", input_text)
    input_text = re.sub(r"e\(n\)(?=($|[ .,!?;: ‑\n\r\t„“'’\"(){}<>|\[\]+/*_]))", r"e", input_text)
    input_text = re.sub(r"[sS]eine?[rsmn]?[/*_:]([iI]hre?[rsmn]?)", r"\1", input_text)
    input_text = re.sub(r"([iI]hr)e?[rsmn]?[/*_:][sS]ein(e?[rsmn]?)", r"\1\2", input_text)
    input_text = re.sub(r"([a-zA-ZäöüßÄÖÜẞ])In", r"\1in", input_text)

    return input_text


# The following function ensures that the user does not see the internal error message of the program,
# but a more user-friendly error message combined with a form that allows the user to report the error.
@app.errorhandler(Exception)
def handle_error(error):
    error_info = str(error) + "\n\n" + traceback.format_exc()
    print("Error:")
    print(error_info)
    input_text = session.get("input_text", "")
    session["error"] = error_info
    return render_template("report.html", dataToRender= f"""Eingegebener Text: <br/>
        <textarea id="textInput" readonly>{input_text}</textarea><br/><br/>
        Ein unerwartetes Problem ist aufgetreten. Du kannst uns helfen, dieses Problem zu beheben, indem Du auf „Problem melden“ klickst. In diesem Fall wird der von Dir eingegebene Text zusammen mit einer automatisch erzeugten Fehlerbeschreibung an die Entwicklerne des De-e-Automaten gesendet.<br/><br/>
        <form action="/error_report_sent" method="POST">
        <button type="submit" class="grey-button">Problem melden</button>
        </form>
        <br/><br/>""")

# The following function returns the basic user interface.
@app.route("/", methods=["POST", "GET"])
def index():
    input_text = session.get("input_text", "")
    return render_template("index.html", input_text=input_text)

# The following function parses the input text and returns the marking form.
@app.route("/parse", methods=["POST", "GET"])
def parse():
    if request.method == "POST":
        input_text = request.form["inputText"]
        session.clear()
        session["input_text"] = input_text

        # If input text has more than 5000 characters, return an error message.
        if len(input_text) > 5000:
            return render_template("index.html", input_text=input_text, dataToRender= f"""Der eingegebene Text ist zu lang. Bitte gib einen Text mit weniger als 5000 Zeichen ein.""")

        stripped_input_text = input_text.lstrip()
        # Remove soft hyphens from input text
        stripped_input_text = stripped_input_text.replace("­","")
        stripped_input_text = hack_for_ordinal_numbers(stripped_input_text)
        input_text_with_split_prepositions = split_prepositions(stripped_input_text)
        input_text_with_split_prepositions = remove_special_character_gendering(input_text_with_split_prepositions)
        print(input_text_with_split_prepositions)
        parse = get_parse(input_text_with_split_prepositions)

        # If there is an adjective that does not modify a noun, capitalize it and repeat the parsing.
        modified_text, capitalized_words, glauben, change = search_lonely_adjectives(parse,stripped_input_text)
        if not change:
            marked_nouns = mark_nouns(parse,[],[])
        else:
            print("Parsing again with capitalized adjectives.")
            modified_text_with_split_prepositions = split_prepositions(modified_text)
            modified_text_with_split_prepositions = remove_special_character_gendering(modified_text_with_split_prepositions)
            print(modified_text_with_split_prepositions)
            parse = get_parse(modified_text_with_split_prepositions)
            print(parse)
            for parse_list in parse:
                marking_tool = Marking_Tool(parse_list,{},[])
                modified_text = Marking_Tool.find_realizations(marking_tool,modified_text)
            marked_nouns = mark_nouns(parse,capitalized_words, glauben)

        marked_nouns = undo_hack_for_ordinal_numbers(marked_nouns)
        marked_nouns = replace_whitespace_outside_html_tags(marked_nouns)
        # Add warning for single word input (only when the word as a whole is marked, i.e. when marked_nouns contains "checkbox" and has no letter after "</u></label></div>"):
        warning = False
        if len(parse) == 1 and (len(parse[0]) == 1 or (len(parse[0]) == 2 and parse[0][1][3] == "$.")) and marked_nouns.find("checkbox") != -1 and not re.search(r"</u></label></div>[a-zA-ZäöüßÄÖÜẞ]", marked_nouns):
            # sie
            if parse[0][0][1] == "sie":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob sich das Wort „sie“ auf eine einzelne Person bezieht oder auf eine Gruppe von Personen. Im zweiten Fall ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. "
            # Sie
            elif parse[0][0][1] == "Sie":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „Sie“ als höfliche Alternative zu „du“ verwendet wird, sich auf eine Gruppe von Personen bezieht oder auf eine einzelne Person. In den ersten beiden Fällen ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. "
            # ihr
            elif parse[0][0][1] == "ihr":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „" + parse[0][0][1] + "“ Bezug auf eine einzelne Person oder auf eine Gruppe von Personen nimmt. Wenn es Bezug auf eine Gruppe von Personen nimmt, ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. Mit Bezug auf eine einzelne Person kann das Wort „ihr“ entweder eine besitzanzeigende Funktion haben oder die Dativ-Form von „sie“ sein. Im ersten Fall lautet die geschlechtsneutrale Form „ens“, im zweiten Fall „em“. "
            # Ihr
            elif parse[0][0][1] == "ihr" or parse[0][0][1] == "Ihr" or parse[0][0][1] == "ihrem" or parse[0][0][1] == "Ihrem" or parse[0][0][1] == "ihres" or parse[0][0][1] == "Ihres" or parse[0][0][1] == "ihrs" or parse[0][0][1] == "Ihrs":
                warning = True
                ending = parse[0][0][1][3:]
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „" + parse[0][0][1] + "“ als höfliche Alternative zu „dein" + ending + "“ verwendet wird, Bezug auf eine einzelne Person oder auf eine Gruppe von Personen nimmt. Wenn es als höfliche Alternative zu „dein" + ending + "“ verwendet wird oder Bezug auf eine Gruppe von Personen nimmt, ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. "
            # ihre, ihrem, ihr(e)s (since this has two ambiguities, we only give a generic warning for single-word inputs)
            elif parse[0][0][1] == "ihre" or parse[0][0][1] == "Ihre" or parse[0][0][1] == "ihrem" or parse[0][0][1] == "ihres" or parse[0][0][1] == "ihrs":
                warning = True
                special_warning = ""
            # sein
            elif parse[0][0][1] == "sein":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „sein“ mit besitzanzeigender Funktion oder als Verb verwendet wird. Als Verb sollte es im De-e-System natürlich nicht geändert werden. "
            # die
            elif parse[0][0][1] == "die" or parse[0][0][1] == "Die":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob sich das Wort „" + parse[0][0][1] + "“ auf eine einzelne einzelne Person bezieht oder auf eine Gruppe von Personen. Im zweiten Fall ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. "
            # der
            elif parse[0][0][1] == "der" or parse[0][0][1] == "Der":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „" + parse[0][0][1] + "“ die maskuline Nominativ-Form oder die feminine Genitiv-Form des bestimmten Artikels ist, sodass nicht klar ist, ob im Inklusivum die Nominativ-Form „de“ oder die Genitiv-Form „ders“ verwendet werden sollte. "
            # den
            elif parse[0][0][1] == "den" or parse[0][0][1] == "Den":
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „" + parse[0][0][1] + "“ die maskuline Akkusativ-Form oder die Dativ-Plural-Form des bestimmten Artikels ist. Im zweiten Fall ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. "
            # meine/keine usw.
            elif (parse[0][0][4] == "PIS" or parse[0][0][4] == "PPOSAT") and parse[0][0][1].endswith("e") and parse[0][0][5].endswith("_") and marked_nouns.find("checkbox-container") == marked_nouns.rfind("checkbox-container"): # The last condition ensures that "seine" and "ihre" are not covered by this warning, as they contain two ambiguities.
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob sich das Wort „" + parse[0][0][1] + "“ auf eine einzelne Person bezieht oder auf eine Gruppe von Personen. Im zweiten Fall ist das Wort bereits geschlechtsneutral und sollte daher im De-e-System nicht geändert werden. "
            # Substantiv auf "-er", dass kein Kompositum aus mehreren movierbaren Susbtantiven ist (marked_nouns contains at most one "checkbox-container")
            elif marked_nouns.find("checkbox-container") == marked_nouns.rfind("checkbox-container") and parse[0][0][4] == "NN" and parse[0][0][1].endswith("er") and parse[0][0][5].endswith("_"):
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob sich das Wort „" + parse[0][0][1] + "“ auf eine einzelne Person bezieht oder auf eine Gruppe von Personen. Im ersten Fall lautet die geschlechtsneutrale Form „" + parse[0][0][1] + "e“, im zweiten Fall „" + parse[0][0][1] + "ne“. "
            # Substantiv auf "-er", dass ein Kompositum aus mehreren movierbaren Susbtantiven ist
            elif parse[0][0][4] == "NN" and parse[0][0][1].endswith("er") and parse[0][0][5].endswith("_"):
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob sich das Wort „" + parse[0][0][1] + "“ auf eine einzelne Person bezieht oder auf eine Gruppe von Personen. Im ersten Fall endet die geschlechtsneutrale Form auf „‑ere“, im zweiten Fall auf „‑erne“. "
            # Substantiv wie "Studenten" (declined form is base form with additional "en")
            elif parse[0][0][4] == "NN" and (parse[0][0][1] == parse[0][0][2] + "en" or parse[0][0][1] == "Bauern") and parse[0][0][5].endswith("_"):
                warning = True
                if parse[0][0][1] == "Bauern":
                    plural_form = "Bauerne"
                else:
                    plural_form = parse[0][0][2] + "erne"
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „" + parse[0][0][1] + "“ die Pluralform oder eine nicht-nominative Singularform von „" + parse[0][0][2] + "“ ist. Im ersten Fall lautet die geschlechtsneutrale Form „" + plural_form + "“ (bzw. im Dativ „" + plural_form + "n“), im zweiten Fall „" + parse[0][0][2] + "e“ (bzw. im Genitiv „" + parse[0][0][2] + "es“). "
            # Substantive wie "Kunden" (base form ends in "e" and declined form is base form with additional "n")
            elif parse[0][0][4] == "NN" and parse[0][0][2].endswith("e") and parse[0][0][1] == parse[0][0][2] + "n" and parse[0][0][5].endswith("_"):
                warning = True
                special_warning = "Der De-e-Automat kann in diesem Fall nicht erkennen, ob das Wort „" + parse[0][0][1] + "“ die Pluralform oder eine nicht-nominative Singularform von „" + parse[0][0][2] + "“ ist. Im ersten Fall lautet die geschlechtsneutrale Form „" + parse[0][0][2] + "rne“ (bzw. im Dativ „" + parse[0][0][2] + "rnen“), im zweiten Fall „" + parse[0][0][2] + "re“. (bzw. im Genitiv „" + parse[0][0][2] + "res“). "
            else:
                special_warning = ""
            if warning:
                marked_nouns = marked_nouns + f"""<br/><br/><div class="warning">Hinweis: """ + special_warning + """Allgemein ist es empfehlenswert, mehr als ein Wort einzugeben, damit der De-e-Automat auf Grundlage des grammatischen Kontexts mehrdeutige Wörter korrekt interpretieren kann.</div>"""

        session["marked_nouns"] = marked_nouns
        if "checkbox" in marked_nouns:
            return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
            <button id="selectAllButton" type="button" class="yellow-button">Alle auswählbaren Wörter auswählen</button>
            <br/><br/>{marked_nouns}<br/><br/>
            <button type="submit" class="purple-button">Ausgewählte Wörter geschlechtsneutral machen</button>
            </form>""")
        else:
            return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
            <br/>{marked_nouns}<br/><br/>
            <button type="reset" class="warning-button">Keine neutralisierbare Personenbezeichnung gefunden.</button>
            </form>""")
    else:
        input_text = session.get("input_text", "")
        session.clear()
        return render_template("index.html", input_text=input_text)
    
# The following function neutralizes the selected words and returns the neutralized text.
@app.route("/mark", methods=["POST", "GET"])
def neutralize_marked():
    if request.method == "POST":
        selected_nouns = request.form
        sentence_number = session.get("sentence_number")
        marking_tool_list = []
        neutralized_text = ""
        for i in range(sentence_number):
            marking_tool_dict = session[f"markingtool{i}"]
            parse_list = marking_tool_dict["parse_list"]
            nounphrases = marking_tool_dict["nounphrases"]
            nounlist = marking_tool_dict["nounlist"]
            nounphrases = {int(k):v for k,v in nounphrases.items()}
            marking_tool = Marking_Tool(parse_list, nounphrases, nounlist)
            marking_tool_list.append(marking_tool)
        # Neutralize all selected words of the form
        list_of_neutralized_nouns = []
        for selected_noun in selected_nouns:
            noun_data = selected_noun.split("|")
            if [noun_data[0], noun_data[1]] not in list_of_neutralized_nouns:
                marking_tool = marking_tool_list[int(noun_data[0])]
                selected_components = []
                for selected_component in selected_nouns:
                    component_data = selected_component.split("|")
                    if component_data[0] == noun_data[0] and component_data[1] == noun_data[1]:
                        selected_components.append(int(component_data[2]))
                marking_tool.neutralize_nounphrase(int(noun_data[1])-1, selected_components)
                list_of_neutralized_nouns.append([noun_data[0], noun_data[1]])
        neutralized_text = ""
        for i in range(sentence_number):
            neutralized_text += marking_tool_list[i].get_sentence()
        neutralized_text = undo_hack_for_ordinal_numbers(neutralized_text)
        neutralized_text = replace_whitespace_outside_html_tags(neutralized_text)
        input_text = session.get("input_text")
        marked_nouns = session.get("marked_nouns")
        # Pre-check previously selected checkboxes
        for selected_noun in selected_nouns:
            marked_nouns = marked_nouns.replace(f'id="{selected_noun}"', f'id="{selected_noun}" checked')
        
        
        return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
                <button id="selectAllButton" type="button" class="yellow-button">Alle auswählbaren Wörter auswählen</button>
                <br/><br/>{marked_nouns}<br/><br/>
                <button type="submit" class="purple-button">Ausgewählte Wörter geschlechtsneutral machen</button>
                </form>""", outputText = neutralized_text)
    else:
        input_text = session.get("input_text", "")
        session.clear()
        return render_template("index.html", input_text=input_text)

# The following function returns the error report form.
@app.route("/report", methods=["POST", "GET"])
def report():
    input_text = session.get("input_text")
    #output_text = request.form["outputText"]

    return render_template("report.html", dataToRender= f"""Eingegebener Text: <br/>
        <textarea id="textInput" readonly>{input_text}</textarea><br/><br/>
        <!--Vom De-e-Automat produzierter Ausgabge-Text: <br/>ouput_text<br/><br/>-->
        Falls Du uns noch weitere Informationen zu dem Problem geben möchtest, kannst Du das hier tun:<br/>
        <form action="/report_sent" method="POST">
        <textarea id="reportText" name="reportText" maxlength="20000"></textarea>
        <button type="submit" class="grey-button">Problem-Meldung abschicken</button>
        </form>
        <br/><br/>""")

# The following function sends the problem report to the developers and returns a confirmation message.
@app.route("/report_sent", methods=["POST", "GET"])
def report_sent():
    if request.method == "POST":
        input_text = session.get("input_text")
        #output_text = request.form["outputText"]
        report_text = request.form["reportText"]

        # Determine the execution environment
        execution_environment = os.environ.get("EXECUTION_ENVIRONMENT")

        # Set the file path based on the execution environment
        if execution_environment == "docker":
            file_path = "/app/reports/reports.txt"
        else:
            file_path = "/home/marcos/Dropbox/geschlechtsneutral/gn_tool/gn_tool/reports/reports.txt"

        with open(file_path, "a") as file:
            file.write(f"Input text:\n{input_text}\n\n")
            #file.write(f"Output Text:\n{output_text}\n\n")
            file.write(f"Report text:\n{report_text}\n\n\n")

        return render_template("report.html", dataToRender= f"""Die Problem-Meldung wurde abgeschickt.<br/><br/>
        Vielen Dank für den Beitrag zur Verbesserung des De-e-Automaten!<br/><br/>
        <form action="/" method="POST">
        </form>""")
    else:
        input_text = session.get("input_text", "")
        session.clear()
        return render_template("index.html", input_text=input_text)
    
# The following function sends the error report to the developers and returns a confirmation message.
@app.route("/error_report_sent", methods=["POST", "GET"])
def error_report_sent():
    if request.method == "POST":
        input_text = session.get("input_text")
        error = session.get("error")

        # Determine the execution environment
        execution_environment = os.environ.get("EXECUTION_ENVIRONMENT")

        # Set the file path based on the execution environment
        if execution_environment == "docker":
            file_path = "/app/reports/reports.txt"
        else:
            file_path = "/home/marcos/Dropbox/geschlechtsneutral/gn_tool/gn_tool/reports/reports.txt"

        with open(file_path, "a") as file:
            file.write(f"Input text:\n{input_text}\n\n")
            #file.write(f"Output Text:\n{output_text}\n\n")
            file.write(f"Error:\n{error}\n\n\n")

        return render_template("report.html", dataToRender= f"""Die Problem-Meldung wurde abgeschickt.<br/><br/>
        Vielen Dank für den Beitrag zur Verbesserung des De-e-Automaten!<br/><br/>
        <form action="/" method="POST">
        </form>""")
    else:
        input_text = session.get("input_text", "")
        session.clear()
        return render_template("index.html", input_text=input_text)

# The following function determines the execution environment and runs the Flask app accordingly.
if __name__ == "__main__":
    # Docker shouldn't be in debug mode
    debugging = True
    if len(sys.argv) >= 2:
        if sys.argv[1] == "run":
            debugging = False
    app.run(debug=debugging, host='0.0.0.0', port=4000)

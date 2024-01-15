from flask import Flask, render_template, request, url_for, redirect, session
from marking_tool import Marking_Tool
from sentence_data import Sentence_Data

import parzu_class as parzu
import re
import sys

sentence_data = Sentence_Data()
options = parzu.process_arguments()
ParZu = parzu.Parser(options)

def get_parse(text: str):
    sentences = ParZu.main(text)
    #sentence_data.clear_marking_tools()
    return sentences

# No longer needed:
def add_split(split_words:dict, sentence_nr:int, word_nr:int):
    if sentence_nr in split_words.keys():
        splits = split_words[sentence_nr]
        splits.append(word_nr)
        split_words[sentence_nr] = splits
    else:
        split_words[sentence_nr] = [word_nr]

def replace_whitespace_outside_html_tags(text):
    # Function to replace whitespace in non-tag parts
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


def mark_nouns(sentences: list, input_text: str):
    marking_form = ""
    sentence_number = 0
    for sentence in sentences:
        words = sentence.split("\n")
        words = words[:-2]
        parse_list = []
        for word in words:
           parse_list.append(word.split("\t"))
        marking_tool = Marking_Tool(parse_list,{})
        input_text = Marking_Tool.find_realizations(marking_tool,input_text)
        print(marking_tool.parse_list)
        session[f"markingtool{sentence_number}"] = marking_tool.__dict__
        #sentence_data.add_marking_tool(sentence_number, marking_tool)
        marking_form += marking_tool.get_marking_form(sentence_number)
        sentence_number += 1
    session["sentence_number"] = sentence_number
    return marking_form

# To ensure correct parsing, 
def split_prepositions(input_text: str) ->str:
    words = re.split('(\s)', input_text)     
    output = ""
    for word in words:
        print(word)
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
        else:
            output += word
    # session["split_words"] = split_words
    return output

app = Flask(__name__)
app.secret_key = "BAD_KEY"

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")
    
@app.route("/parse", methods=["POST"])
def parse_text():
    if request.method == "POST":
        input_text = request.form["inputText"]
        session.clear()
        session["input_text"] = input_text
        stripped_input_text = input_text.lstrip()
        input_text_with_split_prepositions = split_prepositions(stripped_input_text)
        print(input_text_with_split_prepositions)
        parse = get_parse(input_text_with_split_prepositions)
        print(parse)
        marked_nouns = mark_nouns(parse,stripped_input_text)
        marked_nouns = replace_whitespace_outside_html_tags(marked_nouns)
        #session["sentencedata"] = sentence_data.__dict__
        session["marked_nouns"] = marked_nouns
        if "checkbox" in marked_nouns:
            return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
            <button id="selectAllButton" type="button" style="margin-top: 20px;">Alle auswählbaren Wörter auswählen</button>
            <br/><br/>{marked_nouns}<br/><br/>
            <button type="submit" >Ausgewählte Wörter geschlechtsneutral machen</button>
            </form>""")
        else:
            return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
            <br/><br/>{marked_nouns}<br/><br/>
            <button type="reset" style="color:Red">Keine neutralisierbare Personenbezeichnung gefunden.</button>
            </form>""")
    else:
        return render_template("index.html")
    
@app.route("/mark", methods=["POST"])
def neutralize_marked():
    selected_nouns = request.form
    sentence_number = session.get("sentence_number")
    marking_tool_list = []
    neutralized_text = ""
    for i in range(sentence_number):
        marking_tool_dict = session[f"markingtool{i}"]
        parse_list = marking_tool_dict["parse_list"]
        nounphrases = marking_tool_dict["nounphrases"]
        nounphrases = {int(k):v for k,v in nounphrases.items()}
        marking_tool = Marking_Tool(parse_list, nounphrases)
        marking_tool_list.append(marking_tool)
    # Neutralize all selected words of the form
    for selected_noun in selected_nouns:
        print(selected_noun)
        noun_data = selected_noun.split("|")
        marking_tool = marking_tool_list[int(noun_data[0])]
        marking_tool.neutralize_nounphrase(int(noun_data[1])-1, int(noun_data[2]))
        print("New parse list:")
        print(marking_tool.parse_list)
    #neutralized_text = sentence_data.get_text()
    neutralized_text = ""
    #split_words =  {int(k):v for k,v in session["split_words"].items()}
    #print(split_words)
    for i in range(sentence_number):
    #    if i in split_words.keys():
    #        neutralized_text += marking_tool_list[i].get_sentence(split_words[i])
    #    else:
        neutralized_text += marking_tool_list[i].get_sentence()
    neutralized_text = replace_whitespace_outside_html_tags(neutralized_text)
    input_text = session.get("input_text")
    marked_nouns = session.get("marked_nouns")
    return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
            <button id="selectAllButton" type="button" style="margin-top: 20px;">Alle auswählbaren Wörter auswählen</button>
            <br/><br/>{marked_nouns}<br/><br/>
            <button type="submit" >Ausgewählte Wörter geschlechtsneutral machen</button>
            </form>""", outputText = neutralized_text)

if __name__ == "__main__":
    # Docker shouldn't be in debug mode
    debugging = True
    if len(sys.argv) >= 2:
        if sys.argv[1] == "run":
            debugging = False
    app.run(debug=debugging, host='0.0.0.0', port=4000)

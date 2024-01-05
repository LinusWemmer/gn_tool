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

def add_split(split_words:dict, sentence_nr:int, word_nr:int):
    if sentence_nr in split_words.keys():
        splits = split_words[sentence_nr]
        splits.append(word_nr)
        split_words[sentence_nr] = splits
    else:
        split_words[sentence_nr] = [word_nr]

def mark_nouns(sentences: list):
    marking_form = ""
    sentence_number = 0
    for sentence in sentences:
        words = sentence.split("\n")
        words = words[:-2]
        parse_list = []
        for word in words:
           parse_list.append(word.split("\t"))
        marking_tool = Marking_Tool(parse_list,{})
        session[f"markingtool{sentence_number}"] = marking_tool.__dict__
        #sentence_data.add_marking_tool(sentence_number, marking_tool)
        marking_form += marking_tool.get_marking_form(sentence_number)
        sentence_number += 1
    session["sentence_number"] = sentence_number
    return marking_form

# To ensure correct parsing, 
def split_prepositions(input_text: str) ->str:
    sentences = re.split(r"(\.|\!|\?)", input_text)
    # Dict of where words have been split in two. Key: Sentence , Value: List of Positions in that sentence
    split_words = {}                   
    output = ""
    for i,sentence in enumerate(sentences):
        words = sentence.split(" ")
        k = 0
        for j, word in enumerate(words):
            if word =="beim":
                output += "bei dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "Beim":
                output +="Bei dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "zum":
                output += "zu dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "Zum":
                output += "Zu dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "zur":
                output += "zu der "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "Zur":
                output += "Zu der "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "im":
                output += "in dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "Im":
                output += "In dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "vom":
                output += "von dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "Vom":
                output += "Von dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "am":
                output += "an dem "
                add_split(split_words, i,j+k+1)
                k += 1
            elif word == "Am":
                output += "An dem "
                add_split(split_words, i,j+k+1)
                k += 1
            else:
                output += word + " "
    session["split_words"] = split_words
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
        original_input_text = input_text # This is needed for returning the original input text in unaltered form back to the input textarea.
        session.clear()
        input_text = split_prepositions(input_text)
        print(session["split_words"])
        parse = get_parse(input_text)
        print(parse)
        marked_nouns = mark_nouns(parse)
        #session["sentencedata"] = sentence_data.__dict__
        if "checkbox" in marked_nouns:
            return render_template("index.html", input_text=original_input_text, dataToRender= f"""<form action="/mark" method="POST">
            <button id="selectAllButton" type="button" style="margin-top: 20px;">Alle auswählbaren Wörter auswählen</button>
            <p>{marked_nouns}</p>
            <button type="submit" >Ausgewählte Wörter geschlechtsneutral machen</button>
            </form>""")
        else:
            return render_template("index.html", dataToRender= f"""<form action="/mark" method="POST">
            <p>{marked_nouns}</p>
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
    #neutralized_text = sentence_data.get_text()
    neutralized_text = ""
    split_words =  {int(k):v for k,v in session["split_words"].items()}
    #print(split_words)
    for i in range(sentence_number):
        if i in split_words.keys():
            neutralized_text += marking_tool_list[i].get_sentence(split_words[i])
        else:
            neutralized_text += marking_tool_list[i].get_sentence()
    return render_template("index.html", outputText = neutralized_text)

if __name__ == "__main__":
    # Docker shouldn't be in debug mode
    debugging = True
    if len(sys.argv) >= 2:
        if sys.argv[1] == "run":
            debugging = False
    app.run(debug=debugging, host='0.0.0.0', port=4000)
    
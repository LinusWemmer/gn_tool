from flask import Flask, render_template, request, url_for, redirect
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


def mark_nouns(sentences: list):
    nouns = ""
    sentence_number = 0
    for sentence in sentences:
        words = sentence.split("\n")
        words = words[:-2]
        marking_tool = Marking_Tool(words)
        sentence_data.add_marking_tool(sentence_number, marking_tool)
        nouns += marking_tool.get_marking_form(sentence_number)
        sentence_number += 1
    return nouns

# To ensure correct parsing, 
def split_prepositions(input_text: str) ->str:
    sentences = re.split(r"(\.|\!|\?)", input_text)
    output = ""
    for i,sentence in enumerate(sentences):
        words = sentence.split(" ")
        for j,word in enumerate(words):
            k = 0
            if word =="beim":
                output += "bei dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "Beim":
                output +="Bei dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "zum":
                output += "zu dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "Zum":
                output += "Zu dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "zur":
                output += "zu der "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "Zur":
                output += "Zu der "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "im":
                output += "in dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "Im":
                output += "In dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "vom":
                output += "von dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "Vom":
                output += "Von dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "am":
                output += "an dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            elif word == "Am":
                output += "An dem "
                sentence_data.add_split(i,j+k+1)
                k += 1
            else:
                output += word + " "
    return output

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")
    
@app.route("/parse", methods=["POST"])
def parse_text():
    if request.method == "POST":
        input_text = request.form["inputText"]
        sentence_data.clear_marking_tools()
        input_text = split_prepositions(input_text)
        parse = get_parse(input_text)
        print(parse)
        marked_nouns = mark_nouns(parse)
        return render_template("index.html", dataToRender= f"""<form action="/mark" method="POST">
        <p>{marked_nouns}</p>
        <button type="submit" >Ausgewählte Wörter neutralisieren.</button>
        </form>""")
    else:
        return render_template("index.html")
    
@app.route("/mark", methods=["POST"])
def neutralize_marked():
    selected_nouns = request.form
    for selected_noun in selected_nouns:
        print(selected_noun)
        noun_data = selected_noun.split("|")
        marking_tool = sentence_data.get_marking_tool(int(noun_data[0]))
        marking_tool.neutralize_nounphrase(int(noun_data[1])-1, int(noun_data[2]))
    neutralized_text = sentence_data.get_text()
    return render_template("index.html", outputText = neutralized_text)

if __name__ == "__main__":
    # DOcker should'nt be in debug mode
    debugging = False
    if len(sys.argv) >= 2:
        if sys.argv[1] == "Debug":
            debugging = True
    app.run(debug=debugging, host='0.0.0.0', port=4000)
    
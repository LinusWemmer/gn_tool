from flask import Flask, render_template, request, url_for, redirect
from marking_tool import Marking_Tool
from sentence_data import Sentence_Data

import parzu_class as parzu
import sys

sentence_data = Sentence_Data()

def get_parse(text: str):
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main(text)
    sentence_data.clear_marking_tools
    return sentences


#TODO: fix this, find if role noun.
def mark_nouns(sentences: list):
    nouns = ""
    sentence_number = 0
    for sentence in sentences:
        words = sentence.split("\n")
        words = words[:-2]
        marking_tool = Marking_Tool(words)
        # marking_tool.find_nounphrase()
        sentence_data.add_marking_tool(sentence_number, marking_tool)
        nouns += marking_tool.get_marking_form(sentence_number)
        sentence_number += 1
    return nouns

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")
    
@app.route("/parse", methods=["POST"])
def parse_text():
    if request.method == "POST":
        input_text = request.form["inputText"]
        parse = get_parse(input_text)
        print(parse)
        marked_nouns = (mark_nouns(parse))

        return render_template("index.html", dataToRender= f"""<form action="/mark" method="POST">
        <p>{marked_nouns}</p>
        <button type="submit" >Submit</button>
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
    app.run(debug=True)

# TODO: Dort ist ein netter Schüler (nette, adjektive)
# TODO: Plural.
# TODO: Der Lehrer , der dort ist , ist nett
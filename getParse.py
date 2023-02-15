from flask import Flask, render_template, request, url_for, redirect

import parzu_class as parzu
import sys

def get_parse(text: str):
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main(text)
    return sentences

def mark_nouns(sentences: list):
    nouns = ""
    sentence_number = 0
    for sentence in sentences:
        words = sentence.split("\n")
        words = words[:-2]
        for word in words:
            word_parse = word.split("\t")
            if word_parse[3] == "N":
                input_form = f"""<input type="checkbox" id="noun{sentence_number}|{word_parse[0]}" name="noun{sentence_number}|{word_parse[0]}" value="select"> 
                <label for="noun{sentence_number }|{word_parse[0]}">{"<mark>" + word_parse[1] + "</mark>"}</label> """
                nouns += input_form
            elif word_parse[3] == "$.":
                nouns = nouns[:-1] + word_parse[1]
            else:
               nouns += word_parse[1] + " "
        sentence_number += 1
    return nouns

def get_dependencies(pos: int, words: list):
    children = ""

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
        return render_template("index.html", dataToRender=marked_nouns)
    else:
        return render_template("index.html")
    
@app.route("/mark", methods=["POST"])
def neutralize_marked():
    selected_nouns = request.form
    print(selected_nouns)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
#    input_text = sys.argv[1]
#    for sentence in get_parse(input_text):
#        print(sentence)
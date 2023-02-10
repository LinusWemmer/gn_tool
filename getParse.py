from flask import Flask, render_template, request

import parzu_class as parzu
import sys

def get_parse(text: str):
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main(text)
    return sentences

def mark_nouns(sentences: list):
    nouns = ""
    for sentence in sentences:
       words = sentence.split(" ")
       for word in words:
           word_parse = word.split("|")
           if word_parse[1][:2] == "N.":
               nouns += "<b>" + word_parse[0] + "</b> "
           else:
               nouns += word_parse[0] + " "
    return nouns

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        input_text = request.form["inputText"]
        parse = get_parse(input_text)
        print(mark_nouns(parse))
        return render_template("index.html", dataToRender=mark_nouns(parse))
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
#    input_text = sys.argv[1]
#    for sentence in get_parse(input_text):
#        print(sentence)
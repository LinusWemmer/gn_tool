from flask import Flask, render_template, request

import parzu_class as parzu
import sys

def get_parse(text: str):
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main(text)
    return sentences

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        input_text = request.form["inputText"]
        parse = get_parse(input_text)
        return render_template("index.html", dataToRender=parse)
    else:
        return render_template("index.html")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
#    input_text = sys.argv[1]
#    for sentence in get_parse(input_text):
#        print(sentence)
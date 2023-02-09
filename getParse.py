from flask import Flask

import parzu_class as parzu
import sys

def get_parse(text: str):
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main(text)
    #for sentence in sentences:
    #    print(sentence)
    return sentences

app = Flask(__name__)

@app.route("/")
def index():
    return("Hello World!")

if __name__ == "__main__":
    app.run(debug=True)
#    input_text = sys.argv[1]
#    for sentence in get_parse(input_text):
#        print(sentence)
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

def search_lonely_adjectives(parse: list, input_text: str):
        change = False
        modified_text = ""
        capitalized_words = []
        glauben = []
        for sentence_number, parse_list in enumerate(parse):
            marking_tool = Marking_Tool(parse_list,{})
            input_text = Marking_Tool.find_realizations(marking_tool,input_text)
            for word_number, word in enumerate(marking_tool.parse_list):
                if (word[3] == "ADJA" or word[2] == "andere") and (int(word[6] == 0 or parse_list[int(word[6])-1][3] != "N")):
                    word[1] = word[1].capitalize()
                    capitalized_words.append([sentence_number,word_number])
                    change = True
            # Wir ersetzen "glauben" intern durch "schreiben", da ParZu Dativ-Objekte von "glauben" häufig nicht als solche erkennt.
            for word_number, word in enumerate(marking_tool.parse_list):
                if word[2] == "glauben":
                    word[1] = re.sub(r"glaub", "schreib", word[1])
                    word[1] = re.sub(r"Glaub", "Schreib", word[1])
                    glauben.append([sentence_number,word_number])
                    change = True
            modified_text += marking_tool.get_internal_sentence()
        print("capitalized_words:")
        print(capitalized_words)
        return modified_text, capitalized_words, glauben, change

def mark_nouns(sentences: list, input_text: str, capitalized_adj_addresses, glauben):
    print("capitalized_adj_addresses:")
    print(capitalized_adj_addresses)
    marking_form = ""
    sentence_number = 0
    for i, parse_list in enumerate(sentences):
        marking_tool = Marking_Tool(parse_list,{})
        # print("parse_list:")
        # print(marking_tool.parse_list)
        # input_text = Marking_Tool.find_realizations(marking_tool,input_text)
        # print("marking_tool.parse_list:")
        # print(marking_tool.parse_list)
        print("i:")
        print(i)
        print("marking_tool.parse_list:")
        print(marking_tool.parse_list)
        for capitalized_adj_address in capitalized_adj_addresses:
            if i == capitalized_adj_address[0]:
                marking_tool.parse_list[capitalized_adj_address[1]][2] = marking_tool.parse_list[capitalized_adj_address[1]][2].lower()
                marking_tool.parse_list[capitalized_adj_address[1]][-2] = marking_tool.parse_list[capitalized_adj_address[1]][-2].lower()
                if marking_tool.parse_list[capitalized_adj_address[1]][2].startswith("andere") and len(marking_tool.parse_list[capitalized_adj_address[1]][2]) < 8:
                    marking_tool.parse_list[capitalized_adj_address[1]][2] = "andere"
        for glauben_address in glauben:
            if i == glauben_address[0]:
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][1] = re.sub(r"Schreib", "Glaub", marking_tool.parse_list[glauben_address[1]][1])
                marking_tool.parse_list[glauben_address[1]][2] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"schreib", "glaub", marking_tool.parse_list[glauben_address[1]][-2])
                marking_tool.parse_list[glauben_address[1]][-2] = re.sub(r"Schreib", "Glaub", marking_tool.parse_list[glauben_address[1]][-2])
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
        <button type="submit" >Problem melden</button>
        </form>
        <br/><br/>""")

@app.route("/", methods=["POST", "GET"])
def index():
    input_text = session.get("input_text", "")
    return render_template("index.html", input_text=input_text)
    
@app.route("/parse", methods=["POST", "GET"])
def parse():
    if request.method == "POST":
        input_text = request.form["inputText"]
        session.clear()
        session["input_text"] = input_text
        stripped_input_text = input_text.lstrip()
        input_text_with_split_prepositions = split_prepositions(stripped_input_text)
        print(input_text_with_split_prepositions)
        parse = get_parse(input_text_with_split_prepositions)

        # If there is an adjective that does not modify a noun, capitalize it and repeat the parsing.
        modified_text, capitalized_words, glauben, change = search_lonely_adjectives(parse,input_text)
        # print(parse)
        if not change:
            marked_nouns = mark_nouns(parse,stripped_input_text,[],[])
        else:
            print("Parsing again with capitalized adjectives.")
            print(modified_text)
            parse = get_parse(modified_text)
            for parse_list in parse:
                marking_tool = Marking_Tool(parse_list,{})
                modified_text = Marking_Tool.find_realizations(marking_tool,modified_text)
            marked_nouns = mark_nouns(parse,stripped_input_text,capitalized_words, glauben)

        marked_nouns = replace_whitespace_outside_html_tags(marked_nouns)
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
        input_text = session.get("input_text", "")
        return render_template("index.html", input_text=input_text)
    
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
            nounphrases = {int(k):v for k,v in nounphrases.items()}
            marking_tool = Marking_Tool(parse_list, nounphrases)
            marking_tool_list.append(marking_tool)
        # Neutralize all selected words of the form
        for selected_noun in selected_nouns:
            noun_data = selected_noun.split("|")
            marking_tool = marking_tool_list[int(noun_data[0])]
            marking_tool.neutralize_nounphrase(int(noun_data[1])-1, int(noun_data[2]))
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
        # Pre-check previously selected checkboxes
        for selected_noun in selected_nouns:
            marked_nouns = marked_nouns.replace(f'id="{selected_noun}"', f'id="{selected_noun}" checked')
        
        
        return render_template("index.html", input_text=input_text, dataToRender= f"""<form action="/mark" method="POST">
                <button id="selectAllButton" type="button" style="margin-top: 20px;">Alle auswählbaren Wörter auswählen</button>
                <br/><br/>{marked_nouns}<br/><br/>
                <button type="submit" >Ausgewählte Wörter geschlechtsneutral machen</button>
                </form>""", outputText = neutralized_text)
    else:
        input_text = session.get("input_text", "")
        return render_template("index.html", input_text=input_text)

# This web application should have a button that allows users to report problems with the tool.
# The button should open a form where users can write a message and send it to the developers.
# The form should also show the input text, the marked nouns and the output text.
# The form should be saved to a newly created text file.
@app.route("/report", methods=["POST", "GET"])
def report():
    input_text = session.get("input_text")
    #output_text = request.form["outputText"]

    return render_template("report.html", dataToRender= f"""Eingegebener Text: <br/>
        <textarea id="textInput" readonly>{input_text}</textarea><br/><br/>
        <!--Vom De-e-Automat produzierter Ausgabge-Text: <br/>ouput_text<br/><br/>-->
        Falls Du uns noch weitere Informationen zu dem Problem geben möchtest, kannst Du das hier tun:<br/>
        <form action="/report_sent" method="POST">
        <textarea id="reportText" name="reportText"></textarea>
        <button type="submit" >Problem-Meldung abschicken</button>
        </form>
        <br/><br/>""")
    

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
        return render_template("index.html", input_text=input_text)
    
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
        return render_template("index.html", input_text=input_text)

if __name__ == "__main__":
    # Docker shouldn't be in debug mode
    debugging = True
    if len(sys.argv) >= 2:
        if sys.argv[1] == "run":
            debugging = False
    app.run(debug=debugging, host='0.0.0.0', port=4000)

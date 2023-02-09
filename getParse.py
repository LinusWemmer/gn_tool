import parzu_class as parzu
import sys

def get_parse(text: str):
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main(text)
    #for sentence in sentences:
    #    print(sentence)
    return sentences

# input should be a string
if __name__ == "__main__":
    input_text = sys.argv[1]
    for sentence in get_parse(input_text):
        print(sentence)
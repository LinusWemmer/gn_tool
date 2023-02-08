import parzu_class as parzu

def get_parse():
    options = parzu.process_arguments()
    ParZu = parzu.Parser(options)
    sentences = ParZu.main('Der Schüler gibt der Lehrerin sein Buch.')
    for sentence in sentences:
        print(sentence)


get_parse()
from parser import DictionaryParser

parser = DictionaryParser("french_words.csv")

assert len(parser) == 10000

spaces = [x for x in parser.word_list if " " in x]
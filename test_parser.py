from parser import DictionaryParser

parser = DictionaryParser("test_words.csv")

assert len(parser) == 9

parser.parse_dictionary()

parser.load_target_dictionary()
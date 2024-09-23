# Sentence tokenization:
example = "Jadis, une nuit, je fus un papillon, voltigeant, content de son sort. Puis, je m’éveillai, étant Tchouang-tseu. Qui suis-je en réalité ? Un papillon qui rêve qu’il est Tchouang-tseu ou Tchouang qui s’imagine qu’il fut papillon ?"

# Word tokenization
from nltk.tokenize import word_tokenize
tokens = word_tokenize(example, language='french')


# stopword removal
from nltk.corpus import names, stopwords, words

fswords = sorted(stopwords.words("french"))

out = [x for x in tokens if x not in fswords]
out = [x.lower() for x in out if x.isalpha()]
out = list(set(out))
# crossreference this against a dictionary of french words and we're done
# https://opendata.stackexchange.com/questions/11227/french-word-list
# this is what we are after
# http://www.lexique.org/
# the .tsv contains all words grouped by lemmata


# Sentences and documents are a bit more tricky


# we need to perform stop word removal for the list of 10k words
# this would eliminate lots of failure cases.
# for documents we could to part of speech tagging and remove all names etc.

# this does not tag the name properly => useless.
# we could just crossreference against a full dictionary


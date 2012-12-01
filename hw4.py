# Jason Mow (jmow@seas.upenn.edu)
# Nate Close (closen@seas.upenn.edu)

from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import word_tokenize

def get_tag_mapping(map_file):
    tags = dict()
    f = open(map_file)
    for line in f:
        data = line.split("\t")
        tags[data[0]] = data[1]
    return tags


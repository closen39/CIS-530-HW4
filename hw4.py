# Jason Mow (jmow@seas.upenn.edu)
# Nate Close (closen@seas.upenn.edu)

from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import word_tokenize
from BeautifulSoup import BeautifulSoup as Soup

def get_all_files(directory):
    files = PlaintextCorpusReader(directory, '.*')
    return [directory + "/" + x for x in files.fileids()]

def get_tag_mapping(map_file):
    tags = dict()
    f = open(map_file)
    for line in f:
        data = line.split("\t")
        tags[data[0]] = data[1]
    return tags

# Assuming that xml_files is a list of filenames to xml files, not the actual xml
def get_all_sent_tok(xml_files):
    retList = list()
    for file in xml_files:
        text = open(file).read()
        doc = Soup(text)
        sents = [x.string for x in doc.findAll("sentence")]
        for s in sents:
            sentList = list()
            sentence = Soup(s)
            toks = [x.string for x in sentence.findAll("token")
            for tok in toks:
                token = Soup(tok)
                sentList.append((token.find("word").string.lower(), token.find("lemma").string.lower(), token.find("pos").string.lower()))
            retList.append(sentList)
    return retList

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
        tags[data[0]] = data[1].rstrip()
    return tags

# Assuming that xml_files is a list of filenames to xml files, not the actual xml
def get_all_sent_tok(xml_files):
    retList = list()
    for file in xml_files:
        text = open(file).read()
        doc = Soup(text)
        sents = doc.findAll("tokens")
        for s in sents:
            sentList = list()
            toks = [x for x in s.contents if x != "\n"]
            for tok in toks:
                sentList.append((tok.contents[1].string.lower(), tok.contents[3].string.lower(), tok.contents[9].string))
            retList.append(sentList)
    return retList

def get_nounverb_lemma_dict(tok_sents, tagmap):
    retDict = dict()
    for sent in tok_sents:
        for tup in sent:
            if tagmap[tup[2]] == "VERB" or tagmap[tup[2]] == "NOUN":
                retDict[tup[0]] = tup[1]
    return retDict

def main():
    tagmap = get_tag_mapping('en-ptb-modified.map')
    files = get_all_files('xmlDir')
    toks = get_all_sent_tok(files)
    nvDict = get_nounverb_lemma_dict(toks, tagmap)
    print nvDict

if  __name__ =='__main__':
    main()
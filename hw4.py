# Jason Mow (jmow@seas.upenn.edu)
# Nate Close (closen@seas.upenn.edu)

from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
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

def get_func_words(filename):
    retList = list()
    f = open(filename)
    for line in f:
        retList.append(line.rstrip())
    return retList

# Assuming that we check the lemma for existence in funcwords list
def get_top_nouns_verbs(tok_sents, tagmap, n):
    # get_func_words('/home1/c/cis530/hw4/funcwords.txt')
    funcwords = get_func_words('funcwords.txt')
    fdNoun = FreqDist()
    fdVerb = FreqDist()
    for sent in tok_sents:
        for tup in sent:
            if tagmap[tup[2]] == "VERB" and tup[1] not in funcwords:
                fdVerb.inc(tup[1]) 
            elif tagmap[tup[2]] == "NOUN" and tup[1] not in funcwords:
                fdNoun.inc(tup[1])
    return (fdNoun.keys()[:n], fdVerb.keys()[:n])

def main():
    tagmap = get_tag_mapping('en-ptb-modified.map')
    files = get_all_files('xmlDir')
    toks = get_all_sent_tok(files)
    # nvDict = get_nounverb_lemma_dict(toks, tagmap)
    topnv = get_top_nouns_verbs(toks, tagmap, 10)
    print topnv

if  __name__ =='__main__':
    main()
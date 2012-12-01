# Jason Mow (jmow@seas.upenn.edu)
# Nate Close (closen@seas.upenn.edu)

from BeautifulSoup import BeautifulSoup as Soup
from math import sqrt
from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import wordnet as wn
from stanford_parser.parser import Parser

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

def get_context(lemmas, tok_sents):
    # get_func_words('/home1/c/cis530/hw4/funcwords.txt')
    funcwords = get_func_words('funcwords.txt')
    retDict = dict()
    for lemma in lemmas:
        retDict[lemma] = set()
    for sent in tok_sents:
        sentence_lemmas = [x[1] for x in sent]
        for lemma in lemmas:
            if lemma in sentence_lemmas and lemma not in funcwords:
                # context consists of lemmas, not words
                context = [x[1] for x in sent if x[1] != lemma]
                for x in context:
                    retDict[lemma].add(x)
    return retDict

# Undefined behavior if synset from wn.synsets(word, pos) returns nothing
def get_path_similarity(word1, context1, word2, context2, pos):
    wn_pos = wn.VERB
    if pos == 'noun':
        wn_pos = wn.NOUN
    # get synsets
    synset1 = wn.synsets(word1, wn_pos)
    synset2 = wn.synsets(word2, wn_pos)
    # print "word1 is", word1
    # print "word2 is", word2
    # print "synset 1 is", synset1
    # print "synset 2 is", synset2
    best1 = find_best_synset(synset1, context1)
    best2 = find_best_synset(synset2, context2)
    print "best1", best1
    print "best2", best2
    return wn.path_similarity(best1, best2)

# finds and returns best Synset object
def find_best_synset(synsets, context):
    synset_scores = dict()
    for synset in synsets:
        vec = [0] * len(context)
        context_vec = [1] * len(context)
        definition = synset.definition.lower()
        for idx, word in enumerate(context):
            if word in definition:
                vec[idx] = 1
        #generate cosine similarity
        synset_scores[synset] = cosine_similarity(vec, context_vec)
    print "synset_scores", synset_scores
    return max(synset_scores.items(), key=lambda x: x[1])[0]

def cosine_similarity(x, y):
    prodCross = 0.0
    xSquare = 0.0
    ySquare = 0.0
    for i in range(min(len(x), len(y))):
        prodCross += x[i] * y[i]
        xSquare += x[i] * x[i]
        ySquare += y[i] * y[i]
    if (xSquare == 0 or ySquare == 0):
        return 0.0
    return prodCross / (sqrt(xSquare) * sqrt(ySquare))

def dependency_parse_files(fileList):
    p = Parser()
    retList = list()
    for file in fileList:
        deps = p.parseToStanfordDependencies(open(file).read().rstrip())
        retList.extend([(r, gov.text, dep.text) for r, gov, dep in deps.dependencies])
    return retList

def main():
    tagmap = get_tag_mapping('en-ptb-modified.map')
    files = get_all_files('xmlDir')
    toks = get_all_sent_tok(files)
    # nvDict = get_nounverb_lemma_dict(toks, tagmap)
    topnv = get_top_nouns_verbs(toks, tagmap, 2)
    # print topnv
    contexts = get_context(topnv[1], toks)
    path_sim = get_path_similarity(topnv[1][0], contexts[topnv[1][0]], topnv[1][1], contexts[topnv[1][1]], "verb")
    print path_sim

if  __name__ =='__main__':
    main()
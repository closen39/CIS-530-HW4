# Jason Mow (jmow@seas.upenn.edu)
# Nate Close (closen@seas.upenn.edu)

from BeautifulSoup import BeautifulSoup as Soup
from math import sqrt
from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import wordnet as wn
#from stanford_parser.parser import Parser

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
                if wn.synsets(tup[1]):
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
            if tagmap[tup[2]] == "VERB" and tup[1] not in funcwords and wn.synsets(tup[1]):
                fdVerb.inc(tup[1]) 
            elif tagmap[tup[2]] == "NOUN" and tup[1] not in funcwords and wn.synsets(tup[1]):
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
    # print "best1", best1
    # print "best2", best2
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
    # print "synset_scores", synset_scores
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
        for sent in sent_tokenize(open(file).read().rstrip()):
            deps = p.parseToStanfordDependencies(sent)
            retList.extend([(r.lower(), gov.text.lower(), dep.text.lower()) for r, gov, dep in deps.dependencies if wn.synsets(gov.text) and wn.synsets(dep.text)])
    return retList

# pos is a pos, lolz
# word_list is list of lemmas to be considered
# word is a lemma
def get_linked_words(word, word_list, pos, dependency_list, lemma_dict):
    dep_list = [(r, lemma_dict[gov], lemma_dict[dep]) for r, gov, dep in dependency_list if gov in lemma_dict and dep in lemma_dict]
    retList = list()
    for lemma in word_list:
        dep1 = [(r, gov, dep) for r, gov, dep in dep_list if gov == lemma and dep == word]
        if len(dep1):
            retList.append(lemma)
        dep2 = [(r, gov, dep) for r, gov, dep in dep_list if dep == lemma and gov == word]
        if len(dep2):
            retList.append(lemma)
    return list(set(retList))

def get_top_n_linked_words(word, word_list, pos, dependency_list, lemma_dict, context_dict, n):
    linked_words = get_linked_words(word, word_list, pos, dependency_list, lemma_dict)
    word_scores = dict()
    for lemma in linked_words:
        word_scores[lemma] = get_path_similarity(word, context_dict[word], lemma, context_dict[lemma], pos)
    return sorted(word_scores.keys(), key=lambda x: word_scores[x], reverse=True)[:n]

def create_graphviz_file(edge_list, output_file):
    file = open(output_file, "w")
    file.write("graph G {\n")
    for (x, y) in edge_list:
        file.write(x + " -- " + y + ";\n")
    file.write("}")

# Question 1.6.2
def gen_graph_files():
    tagmap = get_tag_mapping('en-ptb-modified.map')
    files = get_all_files('smallXmlDir')
    toks = get_all_sent_tok(files)
    lemmaDict = get_nounverb_lemma_dict(toks, tagmap)

    topnv = get_top_nouns_verbs(toks, tagmap, 20)
    nouns = topnv[0]
    nContext = get_context(nouns, toks)
    verbs = topnv[1]
    vContext = get_context(verbs, toks)

    print "Starting Dependency List Generation"
    depList = dependency_parse_files(get_all_files('/home1/c/cis530/hw4/small_set'))
    print "Finished generating Dependency List"

    print "Processing Nouns"
    edge_list = list()
    for noun in nouns:
        top_words = get_top_n_linked_words(noun, nouns, "noun", depList, lemmaDict, nContext, 5)
        for word in top_words:
            if noun != word:
                edge_list.append((noun, word))
    create_graphviz_file(edge_list, "nouns.viz")

    print "Processing verbs"
    edge_list = list()
    for verb in verbs:
            top_words = get_top_n_linked_words(verb, verbs, "verb", depList, lemmaDict, vContext, 5)
            for word in top_words:
                if verb != word:
                    edge_list.append((verb, word))
    create_graphviz_file(edge_list, "verbs.viz")

def calc_gloss_sim(gloss1, gloss2):
    count = 0
    visited = set(get_func_words('funcwords.txt'))
    # calculate length 2
    for idx, word in enumerate(word_tokenize(gloss1)):
        if idx + 1 < len(gloss1) and word not in visited and gloss1[idx + 1] not in visited:
            if str(word) + " " + str(gloss1[idx + 1]) in gloss2:
                count += 4
                visited.add(word)
                visited.add(gloss1[idx + 1])
                print word, gloss1[idx+1]
    # calculate length 1
    for word in word_tokenize(gloss1):
        if word not in visited and word in gloss2:
            count += 1
            visited.add(word)
            print word
    return count


def get_lesk_similarity(word1, context1, word2, context2, pos):
    wn_pos = wn.VERB
    if pos == 'noun':
        wn_pos = wn.NOUN
    # get synsets
    synset1 = wn.synsets(word1, wn_pos)
    synset2 = wn.synsets(word2, wn_pos)

    best1 = find_best_synset(synset1, context1)
    best2 = find_best_synset(synset2, context2)

    #get hyponym glosses
    gloss1 = best1.definition
    hyp1 = best1.hyponyms()
    for hyp in hyp1:
        gloss1 += " " + hyp.definition
    gloss2 = best2.definition
    hyp2 = best2.hyponyms()
    for hyp in hyp2:
        gloss2 += " " + hyp.definition
    return calc_gloss_sim(gloss1, gloss2)


def main():
    ###########################
    ##          Main         ##
    ###########################
    #gen_graph_files()
    
    ###########################
    ##        Testing        ##
    ###########################
    # tagmap = get_tag_mapping('en-ptb-modified.map')
    # files = get_all_files('xmlDir')
    # toks = get_all_sent_tok(files)
    # nvDict = get_nounverb_lemma_dict(toks, tagmap)
    # topnv = get_top_nouns_verbs(toks, tagmap, 2)
    # print topnv
    # contexts = get_context(topnv[1], toks)
    # path_sim = get_path_similarity(topnv[1][0], contexts[topnv[1][0]], topnv[1][1], contexts[topnv[1][1]], "verb")
    # print path_sim
    sent1 = "paper that is specially prepared for use in drafting"
    sent2 = "the art of transferring designs from specially prepared paper to wood or glass or metal surface"
    print calc_gloss_sim(sent1, sent2)

if  __name__ =='__main__':
    main()

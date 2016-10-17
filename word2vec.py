import re

import numpy
from gensim.models import Word2Vec
from gensim.utils import any2unicode
from nltk.stem.porter import PorterStemmer
from nltk.tokenize.regexp import WhitespaceTokenizer
import random
__author__ = 'Ameer'

def myhashfxn(obj):
  return hash(obj) % (2 ** 32)

class Corpus(object):

    def __init__(self,input):
        self.input = input

    def __iter__(self):
        for text in self.input: # for each relevant file
            yield  self.analyize(text)

    def analyize(self,text):
        try:
            unitext = any2unicode(text, encoding='utf8', errors='strict')
        except:
            print ("Not utf-8")
            return []
        pass

        #convert to lower
        lowerText = unitext.lower()

        # Regex way: gives some text 'qwe (x)' as 'qwe' '(x)'
        # very aggresive regex...removes puncs and digits..keeps only alphabetic words
        tokenizer = WhitespaceTokenizer()
        regexTokens = tokenizer.tokenize(lowerText)
        p_stemmer = PorterStemmer()
        stemmedTokens = [p_stemmer.stem(i) for i in regexTokens]

        stemmedRemSingleLetterTokens = [w for w in stemmedTokens if len(w)>1]
        return stemmedRemSingleLetterTokens





class WordToVecModeler(object):
    """
    Simple word2vec modeling
    """

    def train(self, name,input):
        """
        Implements this method in subclass to process text and modeling topcis in texts.
        Once this method finished modeling succesfull the model should be stored at data/models and its corpus at data/corpora.
        """
        corpus = Corpus(input);
        word2v = Word2Vec(corpus,hashfxn=myhashfxn,workers=4)

        word2v.save(name+".model")



    def model_topics(self,name, sentences):
        """
        Implements this method in subclass to process text and modeling topcis in texts.
        Once this method finished modeling succesfull the model should be stored at data/models and its corpus at data/corpora.
        """
        corpus = Corpus(input=sentences)
        voc = []

        word2v = Word2Vec.load(name + ".model")

        for sentence in corpus:
            voc.append(word2v.most_similar(sentence))

        return voc


def sample(mylist, sample_size):

    list = random.sample(mylist,sample_size)
    return list


docs = ["Inter Press Service Militarising the Ebola Crisis Militarising the Ebola Crisis",
        "Combating the Ebola Outbreak",
        "U.S. to assign 3,000 military personnel to fight Ebola | Air Force Times | airforcetimes.com",
        "Newstime Africa Ebola Crisis British military medics to help with Ebola crisis in Sierra Leone Ebola Crisis: EU organises airlift operation to West Africa"
        "Militarising the Ebola Crisis | Inter Press Service"
        "US Marines complete two months of support to Ebola Response in West Africa | United States Africa Command"
        "U.S. bringing home almost all troops sent to Africa in Ebola crisis | FOX6Now.com"
        "What 3,000 American Troops Will Be Doing To Fight Ebola In Africa | ThinkProgress"]
w2v = WordToVecModeler()

lines = [line for line in open("data.txt","r")]

lines = [line for line in open("data.txt","r")]
w2v.train("reports",sample(lines,10000))
topics = w2v.model_topics("reports",[line for line in open("tests.dic").readlines()])


print (topics)
"""
Written by: Dena Schaeffer, Beth Hosek, Justen Stall, Jacob Scheetz

Description
=======================================
File is used to calculate TF, IDF, and TF-IDF. This is a statistical measure used to determine how relevant a term is to a document.
"""
import json
import math
import re
from string import punctuation
from commonwords import commonwords
from keywords import keywords

def computeBasicRelevance(documentText):
    # Split document text into list of words
    wordArray = re.split(' |\?|#|,|\n', documentText)

    wordArray = [word.lower().strip(punctuation)
         for word in wordArray]  # Lowercase all words, strip punctuation
    
    # Filter words for common words
    wordArray = list(filter(lambda word: word not in commonwords and word != "", wordArray))

    keywordsHitCount = 0

    for word in keywords:
        wordHits = wordArray.count(word)
        wordHits = wordHits * keywords[word]/100
        keywordsHitCount += wordHits

    relevance = 1000 * (keywordsHitCount / len(wordArray)) 

    return relevance

def computeTF(wordDict, bagOfWords):
    """
    Caluclates Term-Frequency: measures how frequent a term appears in a document. 
    TF(t)= (Number of times term t appears in a document) / (Total number of terms in the document)

    Parameters
    ----------
    wordDict : dict
        The custom wordlist
    bagOfWords : dict
        All words in the document with their frequency - negates common words
    """

    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

def computeIDF(documents, dirWordCount):
    """
    Calculates Inverse Document Frequency: measures the importance of the term using weights 
    IDF(t) = log_e(Total number of documents / Number of documents with term t in it).


    Parameters
    ----------
    documents : list of Document objects
        All documents in the folder
    allWordCount : dict
        All words with their wordcounts - negates common words
    """

    N = len(documents)

    idfDict = dict.fromkeys(dirWordCount.keys(), 0)
    for document in documents:
        for word, val in document.wordCount.items():
            if val > 0:
                idfDict[word] += 1

    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val))
    return idfDict
    
def computeTFIDF(tfBagOfWords, idfs):
    """
    Calculates TF-IDF: Statistical measure used to evaluate how important a word is to a document. 

    Parameters
    ----------
    tfBagOfWords : dict
        Result from computeTF()
    idfs : dict
        Result from computeIDF()
    """
    tfidf = {}
    for word, val in tfBagOfWords.items():
        idfValue = idfs.get(word, 0)
        tfidf[word] = val * idfValue
    return tfidf
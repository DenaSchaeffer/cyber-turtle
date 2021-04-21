'''
myparser.py

Written by: Jacob Scheetz, Justen Stall, Dena Schaeffer, Beth Hosek

Description
===================================
The keygen file contains functions to handle parsing of HTML and PDF files

Class Attributes
===================================
dirWordCount --> gives the wordcount for every word in a document
    -type: dict
listOfWordCounts --> lost of all word counts in the directory
    - type: dict  
req --> the url to be stripped of HTML
    - type: string
soup --> html content of the given url
    - type: string
wordcount --> document word count
    - type: dict
directoryWordCount --> gives the wordcount for every word in a document
    - type: dict
'''

# Usage: python3 keyword_generator.py <Directory Containing Files>
from sys import argv, exit
from io import StringIO
from string import punctuation
import re
from collections import Counter
from json import dump, dumps
import time
import os
import requests
import xml.etree.ElementTree as ET

# Additional library imports
# PDFMiner3 handles PDF Parsing
# Beatiful Soup 4 handles HTML parsing
# Feedparser handles xml files
from pdfminer3.high_level import extract_text_to_fp
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar
from document import Document
from commonwords import commonwords
import feedparser


# parseUrl
# Returns page name and text
def parseUrl(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    name = soup.find('title').get_text()

    text = soup.get_text()

    return name, text


def parsePdf(inputFile):
    with open(inputFile, 'rb') as i:
        text = StringIO()
        extract_text_to_fp(i, text)
        text = text.getvalue()

    return text


def parseHtml(inputFile):
    with open(inputFile.path, 'rb') as i:
        text = ""
        soup = BeautifulSoup(i, 'html.parser')
        text = soup.get_text()

    return text


def parseRss(url):
    rss = feedparser.parse(url)

    return rss


def parseOpml(inputFile):
    tree = ET.parse(inputFile)
    root = tree.getroot()
    urls = []
    for tag in root.find('body').findall('outline'):
        urls.append(tag.get('xmlUrl'))

    return urls


def countWords(text):
    wordCount = Counter()

    # Split document text into list of words
    wordArray = re.split(' |\?|#|,|\n', text)
    wordArray = [word.lower().strip(punctuation)
                 for word in wordArray]  # Lowercase all words, strip punctuation
    # Filter words for common words
    wordArray = list(
        filter(lambda word: word not in commonwords and word != "", wordArray))

    # Update word counts for document
    wordCount.update(word for word in wordArray)

    documentWordCount = dict(wordCount.most_common())

    return documentWordCount


def countDirectoryWords(documents):
    wordCount = Counter()

    for document in documents:
        # Split document text into list of words
        wordArray = re.split(' |\?|#|,|\n', document.text)
        wordArray = [word.lower().strip(punctuation)
                     for word in wordArray]  # Lowercase all words, strip punctuation
        # Filter words for common words
        wordArray = list(
            filter(lambda word: word not in commonwords and word != "", wordArray))

        # Update word counts for document
        wordCount.update(word for word in wordArray)

        dirWordCount = dict(wordCount.most_common())

    return dirWordCount

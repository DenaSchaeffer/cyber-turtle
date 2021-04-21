'''
ctirt.py


Written by: Beth Hosek, Dena Schaeffer, Jacob Scheetz, and Justen Stall for GE Aviation in University of Dayton's Computer Science Capstone

Usage
===================================
Usage: python3 ctirt.py --help [for options]

Required Packages: see environment.yml for required packages

Description
===================================
This Main class is defined to efficently get the relevent words to search for, read files that may be relevant, and compare the two and compute a relevancy score

Class Attributes
===================================
newWordList --> The Word list, as a set of key value pairs
	- type: dictionary
documents --> self defined class, see documentation for further explanation in document.py
    -type: document
listOfWordCounts --> list containing the words of each document split on special characters and stripped for common words
    - type: list 
allWordCount --> a count of all the words that were parsed in a file/directory
    - int
idfs --> inverse document frequency, see http://www.tfidf.com/ for further info
    - type: dictionary
tf --> term frequency, see http://www.tfidf.com/ for further info
    - type: dictionary
tfidf --> term frequency - inverse document frequency model, the resulting relevancy score
    - type: dictionary
relevanceScore --> derived from the tf-idf model, a score given to a document based on its similarity to a predefined wordlist and other factors
    - type: float

'''
from json import dump, dumps, load
import os
from sys import argv, exit
import click
import time
from tabulate import tabulate
from keywords import keywords
from progress.bar import IncrementalBar

import myparser as parser
import relevance as relevance
from document import Document

@click.command()
@click.option('-u', '--url', help='A given url to be parsed for relevance')
@click.option('-f', '--file', 'inputFile', help='Single file to be analyzed', type=click.Path(exists=True))
@click.option('-d', '--directory', help='Files to be analyzed')
@click.option('-rss', '--rss', help='RSS feed to be analyzed')
@click.option('-op', '--opml', help='RSS feed to be analyzed', type=click.Path(exists=True))
@click.option('-o', '--output', default='assets/output.json', help='Specify name and location of output file. Default is ')
@click.option('-v', '--verbose', count=True, help='Provides detailed information')
@click.option('-dB', '--debug', count=True ,help='print all of the calculated scores for debugging purposes')
@click.option('-r', '--relevance', 'relevanceAlgorithm', default='basic' ,help='select a relevance algorithm')

def main(url, inputFile, directory, rss, opml, output, verbose, debug, relevanceAlgorithm):

    """
    \b
                  888                                      
                  888                                        
                  888                                      
 .d8888b 888  888 88888b.   .d88b.  888d888        
d88P"    888  888 888 "88b d8P  Y8b 888P"        
888      888  888 888  888 88888888 888          
Y88b.    Y88b 888 888 d88P Y8b.     888          
 "Y8888P  "Y88888 88888P"   "Y8888  888              
              888                                                                             
         Y8b d88P                                                                            
          "Y88P"
888                     888    888
888                     888    888
888                     888    888
888888 888  888 888d888 888888 888  .d88b.     _____     ____
888    888  888 888P"   888    888 d8P  Y8b   /      \  |  o |
888    888  888 888     888    888 88888888  |        |/ ___\|
Y88b.  Y88b 888 888     Y88b.  888 Y8b.      |_________/
"Y888  "Y88888 888      "Y888 888  "Y8888    |_|_| |_|_|

GE Aviation - Cyber Threat Reporting Tool
=========================================\n
Written By: Beth Hosek, Dena Schaeffer, Jacob Scheetz, Justen Stall\n 
Under Supervision of: Jeff Archer, Dr. Phu Phung\n
University of Dayton '21
                                                                                         
                                           
    """

    if (len(argv) < 2):
        print(
            "Usage: python3 ctirt.py [options] [target files]\n\n Use --> ctirt.py --help for more details..."
        )
        exit(1)

    if (verbose and url) or (url and debug):
        print("URL is mutually exclusive with verbose and debug")
        exit(1)
    
    
    
    # INITIALIZE DOCUMENTS LIST
    documents = []  # list of document objects

    # OPML FILE INPUT

    if opml:
        printLogo()
        print("\033[0;34m" + "Parsing provided opml file: " + "\033[0m" + "\033[1m" + opml + "\033[0m")

        rssList = parser.parseOpml(opml)

        for rss in rssList:
            print("Parsing RSS feed: " + "\033[1m" + rss + "\033[0m")

            feed = parser.parseRss(rss)
            
            if not verbose:
                # progress bar
                progressBar = IncrementalBar('\tParsing URLs in RSS feed:', max=len(feed.entries), suffix='%(index)d / %(max)d')

            for entry in feed.entries:
                document = Document()

                document.path = entry.link
                
                document.name, document.text = parser.parseUrl(document.path)
                
                document.wordCount = parser.countWords(document.text)
                        
                # Add document object to list, add document wordcount to list
                documents.append(document)

                if not verbose:
                    progressBar.next()
                else:
                    print("Done.")
            
            print("\n\t" + "\033[0;32m" + u'\u2713' + " Done parsing RSS feed: " + "\033[0m" + "\033[1m" + rss + "\033[0m")
    # RSS INPUT

    elif rss:
        printLogo()
        print("Parsing", rss)

        feed = parser.parseRss(rss)
        if not verbose:
            # progress bar
            progressBar = IncrementalBar('Parsing URLs', max=len(feed.entries), suffix='%(index)d / %(max)d')

        for entry in feed.entries:
            document = Document()

            document.path = entry.link
            
            document.name, document.text = parser.parseUrl(document.path)
            
            document.wordCount = parser.countWords(document.text)
                    
            # Add document object to list, add document wordcount to list
            documents.append(document)

            if not verbose:
                progressBar.next()
            else:
                print("Done.")
        
        if not verbose:
            progressBar.finish()

        print("Done.")
    
    # URL INPUT
    
    elif url:
        printLogo()
        print("Parsing...")

        document = Document()

        document.path = url
        
        document.name, document.text = parser.parseUrl(url)
        
        document.wordCount = parser.countWords(document.text)
                
        # Add document object to list, add document wordcount to list
        documents.append(document)

        print("Done.")

    
    # SINGLE FILE INPUT

    elif inputFile:
        printLogo()
        print("Parsing...")

        document = Document()

        document.name = os.path.splitext(inputFile)[0]
        document.path = inputFile

        if inputFile.lower().endswith(".pdf"):  # PDF Parsing
            document.text = parser.parsePdf(inputFile)
        elif inputFile.lower().endswith(".html"):  # HTML Parsing
            document.text = parser.parseHtml(inputFile)

        document.wordCount = parser.countWords(document.text)  # Document word count

        # Add document object to list, add document wordcount to list
        documents.append(document)

        print("Done.")


    # DIRECTORY INPUT

    elif directory:
        printLogo()
        if not verbose:
            # progress bar
            progressBar = IncrementalBar('Parsing', max=len(
                os.listdir(directory)), suffix='%(index)d / %(max)d')

        # Loop through files in directory
        for inputFile in os.scandir(directory):
            beginningTime = time.time()

            if verbose:
                timeStamp = time.time()
                print("***[" + inputFile.name[0:50] + "]***", "is currently being parsed",
                    "-->", (timeStamp - beginningTime), "seconds have elapsed...")

            document = Document()

            document.name = os.path.splitext(inputFile.name)[0]
            document.path = inputFile.path

            if verbose:
                print(inputFile.name)

            if inputFile.name.lower().endswith(".pdf"):  # PDF Parsing
                document.text = parser.parsePdf(inputFile.path)
            elif inputFile.name.lower().endswith(".html"):  # HTML Parsing
                document.text = parser.parseHtml(inputFile.path)

            document.wordCount = parser.countWords(
                document.text)  # Document word count

            # Add document object to list, add document wordcount to list
            documents.append(document)

            if not verbose:
                progressBar.next()
            else:
                print("Done.")
        
        if not verbose:
            progressBar.finish()


    # BASIC RELEVANCE CALCULATION

    for document in documents:
        document.relevance = relevance.computeBasicRelevance(document.text)


    # TF-IDF RELEVANCE CALCULATION

    if directory and (verbose or debug or relevanceAlgorithm == "tfidf"):
        dirWordCount = parser.countDirectoryWords(documents)

        wordList = {}
        with open('./assets/wordlist.json') as f:
            jsonWordList = load(f)
            for pair in jsonWordList.items():
                wordList[pair[0]] = float(pair[1])

        for document in documents:
            # TODO Figure out how to run - fix arguments (ex. import wordlist), make debug work better by allowing it to work not in verbose
            idfs = relevance.computeIDF(documents, dirWordCount)
            print("**************** IDFS ****************")
            print(idfs)
            tf = relevance.computeTF(wordList, document.wordCount)
            print("**************** TF DICT ****************")
            print(tf)

            tfidf = relevance.computeTFIDF(tf, idfs)
            print("**************** TF-IDF Values ****************")
            print(tfidf)

            relevanceScore = 0

            for word, val in tfidf.items():
                relevanceScore += val
            
            document.tfidf = relevanceScore * 100


    # OUTPUT SECTION

    documents.sort(key=lambda document: document.relevance, reverse=True)

    table = []
    tableHeaders = []
    outputData = []
    # print("**************** RELEVANCE SCORES ****************")
    for document in documents:
        outputData.append({'name': document.name[0:30], 'relevance': document.relevance,'path': document.path, 'topTerms': list(document.wordCount.items())[:10]})
        if url or rss or opml: 
            table.append([document.name[0:30], document.relevance, document.path])
            tableHeaders = ["Document","Relevance Score","URL"]
        elif not verbose:
            table.append([document.name[0:70], document.relevance])
            tableHeaders=["Document","Relevance Score"]
        elif verbose and directory:
            table.append([document.name[0:70], document.relevance, document.tfidf, list(document.wordCount.items())[:10]])
            tableHeaders=["Document","Relevance Score", "TF-IDF Score", "Top Terms"]
        else:
            table.append([document.name[0:70], document.relevance, list(document.wordCount.items())[:10]])
            tableHeaders=["Document","Relevance Score", "Top Terms"]

    print(tabulate(table, headers=tableHeaders, tablefmt="fancy_grid"))

    # OUTPUT TO FILE

    with open(output, 'w', encoding='utf-8') as o:
        dump(outputData, o, indent=3)


class color:
   BLUE = '\u001b[34m'
   BASE = '\033[0m'
   RED = '\u001b[31m'

def printLogo():
    print("""
                            Written By: Beth Hosek, Dena Schaeffer, Jacob Scheetz, Justen Stall | University of Dayton '21
                                                Under Supervision of: Jeff Archer, Dr. Phu Phung

               @@@@@@@@@@@@@@@@@@                 | \u001b[34m                   888\033[0m                       \u001b[31m 888                     888    888\033[0m          
           @@@@@((((((@@@@@(((((@@@@@@@           | \u001b[34m                   888\033[0m                       \u001b[31m 888                     888    888\033[0m            
        @@@@(((((((((((@@((((((((((((@@@@@        | \u001b[34m                   888\033[0m                       \u001b[31m 888                     888    888\033[0m          
      @@@@((((((((((((((((((((((((((((((@@@@      | \u001b[34m  .d8888b 888  888 88888b.   .d88b.  888d888\033[0m \u001b[31m 888888 888  888 888d888 888888 888  .d88b.\033[0m  
    @@@@(((((((((((@@@@((((((((@@@@((((((((@@     | \u001b[34m d88P"    888  888 888 "88b d8P  Y8b 888P"\033[0m   \u001b[31m 888    888  888 888P"   888    888 d8P  Y8b\033[0m 
   @@@@((((((@@((@@((@@((((((@@((@@(((((((((@@@   | \u001b[34m 888      888  888 888  888 88888888 888\033[0m     \u001b[31m 888    888  888 888     888    888 88888888\033[0m 
  @@@@(((((((@((@@((@@(@@(((@@(@@@(((((((((((@@@  | \u001b[34m Y88b.    Y88b 888 888 d88P Y8b.     888\033[0m     \u001b[31m Y88b.  Y88b 888 888     Y88b.  888 Y8b.\033[0m
 @@@@(((((((@@@@@@@((@@((((@@@(((((((((((((((@@@  | \u001b[34m  "Y8888P  "Y88888 88888P"   "Y8888  888\033[0m      \u001b[31m "Y888  "Y88888 888      "Y888 888  "Y8888\033[0m   
 @@@@@@((((((((((@@@@@@(@@@((@@@@@@(((((((@@(@@@  | \u001b[34m               888  \033[0m                       ____________________________________________                                           
 @@@@@@@(((((((((((@@@@(((@@@((((((((((((((@@@@@  | \u001b[34m          Y8b d88P  \033[0m                      < Cyber Turtle is the best capstone project! >                            
 @@@(((((((((((@@@(((@@((@@@((@@@(@@@(((((((@@@@  | \u001b[34m           "Y88P"   \033[0m                       --------------------------------------------                                   
  @@(((((((((@@(((((@@(((@@@((@@((((@@((((((@@@@  | \033[0;32m                               _____     ____ \033[0m   /
  @@@(((((((@@(((((@@(((((@@((((((((@@(((((@@@@   | \033[0;32m                              /      \  |  o | \033[0m /
   @@@((((((@@@@@@@@(((((((@@@@@@@@@((((((@@@@    | \033[0;32m                             |        |/ ___\| \033[0m 
     @@@(((((((((((((((((((((((((((((((((@@@@     | \033[0;32m                             |_________/\033[0m
       @@@@((((((((((((((((((((((((((((@@@@       | \033[0;32m                             |_|_| |_|_|\033[0m
         @@@@@@@((((((((@@@@((((((((@@@@@         |                                     
             @@@@@@@@@@@@@@@@@@@@@@@@             |                  GE Aviation - Cyber Threat Reporting Tool
                                                  
""".replace('(', color.BLUE + '(' + color.BASE))




if __name__ == "__main__":
    main()

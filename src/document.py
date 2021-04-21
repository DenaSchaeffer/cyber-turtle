'''
Written by: Jacob Scheetz, Justen Stall, Dena Schaeffer, Beth Hosek

Description
===================================
This Document class is defined to efficently handle and retrieve information from each document that is read into the program. As well as ease the formation of the tf-idf model created
to calculate the output of the program.

Class Attributes
===================================
name --> The title of a document (i.e. example-file.pdf)
	- type: string
path --> The absolute path to the document (i.e. C:\example\path\to\file.pdf)
	- type: string
wordcount --> a dictionary consisting of the key:pair values of the words in each file and the occurence of each word in that file, respectively. (i.e. "hacker":3)
	- to avoid repetition, the 300 most common english words are stripped from each file to keep the results meaningful
	- type: dictionary
relevance --> a relevance score generated by calculating a tf-idf model, by using the occurence of a word against a wordlist
	- type: float
'''


class Document:
	name: str
	path: str
	wordCount: dict 
	relevance: float
	tfidf: float
	text: str

	# def __init__(self, name, path, wordcount, relevance):
	# 	self.name = name
	# 	self.path = path
	# 	self.wordcount = wordcount
	# 	self.relevance = relevance

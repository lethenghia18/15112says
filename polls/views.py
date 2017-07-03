from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse 
import os
from django.conf import settings
from django.template import loader

# inspired by f16 15112 optional lecture code by Ananya and Sarah

# cdf and choice code taken from 
# http://stackoverflow.com/questions/4113307/pythonic-way-to-select-list-elements-with-different-probability
import random
import bisect
import collections

def cdf(weights):
    total = sum(weights)
    result = []
    cumsum = 0
    for w in weights:
        cumsum += w
        result.append(cumsum / total)
    return result

def choice(population, weights):
    assert len(population) == len(weights)
    cdf_vals = cdf(weights)
    x = random.random()
    idx = bisect.bisect(cdf_vals, x)
    return population[idx]

# readFile taken from 112 notes
def readFile(filename, mode="rt"):
    # rt = "read text"
    with open(filename, mode) as fin:
        return fin.read()

# return a dictionary of words mapped to another dictionary of the next word 
# with frequency
# example: {"I": {"work": 3, "am": 2}, "love": {"you": 10, "me": 1}}
def getCounts(text):
    counts = dict()
    text = text.lower()
    wordList = text.split()
    for i in range(len(wordList)-1):
        firstWord = wordList[i]
        secondWord = wordList[i+1] 
        if firstWord in counts:
            counts[firstWord][secondWord] = counts[firstWord].get(secondWord, 0) + 1
        else: 
            counts[firstWord] = {secondWord: 1}
    return counts

# return a dictionary of words mapped to another dictionary of the next word 
# with probability second word occurs after first word 
# example: {"I": {"work": 3/5, "am": 2/5}, "love": {"you": 10/11, "me": 1/11}}
def getProbabilities(counts): 
    probs = dict()
    for firstWord in counts: 
        Sum = 0 
        probs[firstWord] = dict()
        for secondWord in counts[firstWord]: 
            Sum += counts[firstWord][secondWord]
        for secondWord in counts[firstWord]:
            probs[firstWord][secondWord] = counts[firstWord][secondWord]/Sum
    return probs 

def markovChains(text):
    counts = getCounts(text)
    probs = getProbabilities(counts)
    return probs 

# return the next word, given probabilities each word will occur
def getNextWord(wordProbs):
    words = []
    probs = []
    for word in wordProbs:
        words.append(word)
        probs.append(wordProbs[word])
    return choice(words, probs)

def makeSentence(text): 
    first = "the"
    sentence = ["The"]
    probs = markovChains(text)
    while (first.find(".") == -1 and first.find("!") == -1 and first.find("?") == -1):
        wordProbs = probs.get(first, dict())
        if len(wordProbs) == 0: break 
        nextWord = getNextWord(wordProbs)
        first = nextWord
        sentence.append(nextWord)
    return " ".join(sentence)

# read the text, process it with markov chain, and return dictionary maps 
# name to sentences
def main(): 
    files = ["rudina.txt", "max.txt", "kyle.txt", "roman.txt", "aditri.txt", 
            "andrew.txt", "blair.txt", "corey.txt", "nanaki.txt", "nikolai.txt",
            "rishabh.txt", "xinhui.txt"]
    sentences = dict()
    for file in files: 
        text = readFile(os.path.join(os.path.dirname(os.path.dirname(__file__)),'static/' + file))
        sentences[file] = makeSentence(text)
    return sentences

def index(request):
    sentences = main()
    content = ""
    response = HttpResponse()
    for name in sentences: 
        content = name.replace(".txt", " says: ") + sentences[name]
        image = 'https://cs112.github.io/img/staff-%s.jpg' % name.replace(".txt","")
        if name == "rudina.txt": 
            response.write("<img src='%s' width='150' height='150' />" % image)
        else: 
            response.write("<img src='%s' width='80' height='80' />" % image)
        response.write("<p> %s </p>" % content)
    return response
    # return HttpResponse(image, content_type="image/jpg")



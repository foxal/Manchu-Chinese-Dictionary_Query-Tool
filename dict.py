# -*- coding: utf-8 -*-
##A script for querying words in 《滿漢大詞典》. Page number will be returned, and the page in dictionary pdf file will be opend. Searching history is stored in history.txt.
##By Yize
##files used by this script: numlist.csv, settings.ini, history.txt.
##dictmanchu_1爲《滿漢大詞典》所用字母經處理後對應的詞序。

dictmanchu_1 = {"a":1, "e":2, "i":3, "o":4, "u":5, "v":6, "n":7, "k":8, "g":9, "h":10, "b":11, "p":12, "s":13, "x":14, "t":15, "d":16, "l":17, "m":18, "c":19, "j":20, "y":21, "K":22, "G":23, "H":24, "r":25, "f":26, "w":27, "T":28, "D":29, "Z":30, "S":31, "C":32, "J":33, "Q":34}
def preprocess_1(word):
    """Prepare a word for function converttonum."""
    
    ##replace consonants for Chinese loan words with single letter.
    word = word.replace("k'","K")
    word = word.replace("g'","G")
    word = word.replace("h'","H")
    word = word.replace("ts'","T")
    word = word.replace("dz","D")
    word = word.replace("z","Z")
    word = word.replace("sy","S")
    word = word.replace("c'y","C")
    word = word.replace("jy","J")
    word = word.replace("ts","Q")
    
    ##identify gender for letter "k", "g", and "h".
    feminine = ["e", "i", "u"]
    vowel = ["a", "e", "i", "o", "u", "v"]
    i = 0
    while i < len(word):
        if word[i] == "k": ##letter "k"
            if i < len(word) - 1: ##not final k
                if word[i+1] in feminine:
                    word = word[:i] + "K" + word[i+1:]
                kbcspecial = ["Ku", "Gu", "Hu", "hv"] ##special cases precede "k" when the "k" is followed by a consonant.
                if (word[i+1] not in vowel) and (word[i-1] == "e" or (i >= 2 and word[i-2:i] in kbcspecial)): ##"k" after "ku", "gu", "hu", "hv" ,or "e" when followed by a consonant. 
                    word = word[:i] + "K" + word[i+1:]
            elif i == len(word) - 1: ##final "k"
                if word[i-1] == "i" or (word[i-1] == "e" and word[i-2] != "t"): ##final "k" preceded by "i" or "e", but not "te"
                    word = word[:i] + "K"
        if word[i] == "g": ##letter "g"
            if i < len(word) - 1: ##not final "g"
                if word[i+1] in feminine: 
                    word = word[:i] + "G" + word[i+1:]
                elif word[i+1] not in vowel and word[i-1] == "n": #letter "g" in "ng+consonant" case
                    word = word[:i] + "G" + word[i+1:]
            elif i == len(word) - 1 and word[i-1] == "n": ##final "g", i.e. "ng" at the final part of a word.
                word = word[:i] + "G"
        if word[i] == "h" and word[i+1] in feminine: ##letter "h"
            word = word[:i] + "H" + word[i+1:]
        i += 1
    
    return word
    
def converttonum(word,index=6,**dict):
    """Convert a word to number."""
    m_notation = len(dict)
    wordnum = 0
    ##convert
    for letter in word:
        ##ilegal character is treated as 0.
        if letter in dict:
            wordnum += dict[letter] * pow(m_notation,index)
        index -= 1
    return wordnum

import csv
import time
import subprocess
import ConfigParser

##read configures from settings.ini
config = ConfigParser.SafeConfigParser({'openpdf': 0, 'savehistory': 1, 'command': '"C:\Program Files (x86)\Foxit Software\Foxit Reader\Foxit Reader.exe" C:\Users\adminadmin\Documents\課程\满语初程\電子詞典製作\dict_python\manchudict.pdf /A page='})
config.read('settings.ini')
openpdf = config.get('Section1','openpdf')
cmd = config.get('Section1','command')
savehistory = config.get('Section2','savehistory')

##read numlist.csv to start searching.
print 'Search Manhan Dacidian:'
with open('numlist.csv', 'rb') as f:
    reader = csv.reader(f)
    ##while loop for repeated searching.
    while True:
        print 'Please input a word (press Enter to exit):'
        searchword = raw_input()
        searchwordnum = converttonum(preprocess_1(searchword),**dictmanchu_1)
        if searchwordnum == 0:
            exit()
        print 'Word represented by number:', searchwordnum
        ##search
        f.seek(0)
        pagenum = 0
        for row in reader: 
            if float(row[0]) > searchwordnum:
                pagenum = 16 + int(row[1]) - 1
                break
        print 'Word', '"', searchword, '"', 'is most probably on page', pagenum, '(page', pagenum - 16, 'by dictionary page).'
        ##show searching result.
        if pagenum != 0: ##word is found.
            ##write record (word, page number, and system time) to history.txt.
            if savehistory == '1':
                with open('history.txt', 'a') as fhistory: 
                    historyrecord = searchword + ',' + str(pagenum) + ',' + time.strftime("%d/%m/%Y")+ ' ' + time.strftime("%H:%M:%S") + '\n'
                    fhistory.write(historyrecord)
            ##open page in dictionary pdf file.
            if openpdf == '1':
                arg = cmd + str(pagenum)
                subprocess.call(arg)
        else: ##word is not found.
            print 'Word', searchword, 'is not found.'

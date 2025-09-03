from .. import helpers as h
import tamil

def VD_Rule_1(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    if letters_in_1stWord[-1] in h.vallinam_letters:
        letters_in_1stWord.remove(letters_in_1stWord[-1])
        wordPairList[0]="".join(letters_in_1stWord)
    if wordPairList[0] in h.Migaa_words_list:
        return wordPairList
    return wordPairList

def VD_Rule_2(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VD_Rule_2_check356Vetrumai(letters_in_1stWord,letters_in_2ndWord)
    return wordPair



def VD_Rule_2_check356Vetrumai(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] in h.vallinam_letters and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        first_length=len(letters_in_1stWord)-1
        firstWordWithoutMei = letters_in_1stWord[0:first_length]
        if (firstWordWithoutMei[-1] == u'ல்' or firstWordWithoutMei[-1] == u'ன்') and firstWordWithoutMei[-2] in h.UyirMeiLetters:
            mei_uyir_list = h.UyirMei_dict[firstWordWithoutMei[-2]]
            if mei_uyir_list[1] == u"ஆ" or mei_uyir_list[1] == u"இ":
                wordPairList[0] = ''.join(firstWordWithoutMei) 
        elif firstWordWithoutMei[-1] == u'டு' and firstWordWithoutMei[-2] in h.UyirMeiLetters:
            mei_uyir_list = h.UyirMei_dict[firstWordWithoutMei[-2]]
            if mei_uyir_list[1] == u"ஓ" or mei_uyir_list[1] == u"ஒ":
                wordPairList[0] = ''.join(firstWordWithoutMei)
        elif firstWordWithoutMei[-1] == u'து' and firstWordWithoutMei[-2] in h.UyirMeiLetters:
            mei_uyir_list = h.UyirMei_dict[firstWordWithoutMei[-2]]
            if mei_uyir_list[1] == u"ஆ" or mei_uyir_list[1] == u"அ":
                wordPairList[0] = ''.join(firstWordWithoutMei)
    return wordPairList


def VD_Rule_3(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VD_Rule_3_checkViyangol(letters_in_1stWord,letters_in_2ndWord)
    return wordPair


def VD_Rule_3_checkViyangol(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] in h.vallinam_letters and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        first_length=len(letters_in_1stWord)-1
        firstWordWithoutMei = letters_in_1stWord[0:first_length]
        if (firstWordWithoutMei[-1] == u'ய') and firstWordWithoutMei[-2] in h.UyirMeiLetters:
            mei_uyir_list = h.UyirMei_dict[firstWordWithoutMei[-2]]
            if mei_uyir_list[1] == u"இ":
                wordPairList[0] = ''.join(firstWordWithoutMei) 
        elif firstWordWithoutMei[-1] == u'ர்' and firstWordWithoutMei[-2] == u'ய' and firstWordWithoutMei[-3] in h.UyirMeiLetters:
            mei_uyir_list = h.UyirMei_dict[firstWordWithoutMei[-3]]
            if mei_uyir_list[1] == u"இ":
                wordPairList[0] = ''.join(firstWordWithoutMei)
        elif firstWordWithoutMei[-1] == u'க':
            wordPairList[0] = ''.join(firstWordWithoutMei)
    return wordPairList


def VD_Rule_4(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VD_Rule_4_vinayecham(letters_in_1stWord,letters_in_2ndWord)
    return wordPair


def VD_Rule_4_vinayecham(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] in h.vallinam_letters and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        first_length=len(letters_in_1stWord)-1
        firstWordWithoutMei = letters_in_1stWord[0:first_length]
        condition1 = firstWordWithoutMei[-1] == u'து' and (firstWordWithoutMei[-2] == u'ய்' or firstWordWithoutMei[-2] == u'ந்')
        condition2 = (firstWordWithoutMei[-1] == u'று' and firstWordWithoutMei[-2] == u'ன்') or (firstWordWithoutMei[-1] == u'டு' and firstWordWithoutMei[-2] == u'ண்')
        condition3 = firstWordWithoutMei[-1] == u'டி' and firstWordWithoutMei[-2] == u'ப'
        if (firstWordWithoutMei[-1] == u'று' and firstWordWithoutMei[-2] in h.UyirMeiLetters):
            if h.UyirMei_dict[firstWordWithoutMei[-2]][1] == u'ஆ':
                wordPairList[0] = ''.join(firstWordWithoutMei)   
        if (condition1 or condition2 or condition3):
            wordPairList[0] = ''.join(firstWordWithoutMei) 
    return wordPairList

def VD_Rule_5(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VD_Rule_5_question(letters_in_1stWord,letters_in_2ndWord)
    return wordPair


def VD_Rule_5_question(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] in h.vallinam_letters and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        first_length=len(letters_in_1stWord)-1
        firstWordWithoutMei = letters_in_1stWord[0:first_length]
        condition1 = firstWordWithoutMei[-1] == u'யா'
        condition2 = firstWordWithoutMei[-1] in h.UyirMeiLetters and (h.UyirMei_dict[firstWordWithoutMei[-1]][1] in [u'ஆ',u'ஓ'])
        if (condition1 or condition2):
            wordPairList[0] = ''.join(firstWordWithoutMei) 
    return wordPairList


def VD_Rule_6(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VD_Rule_6_IdaiAyutham(letters_in_1stWord,letters_in_2ndWord)
    return wordPair


def VD_Rule_6_IdaiAyutham(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] in h.vallinam_letters and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        first_length=len(letters_in_1stWord)-1
        firstWordWithoutMei = letters_in_1stWord[0:first_length]
        condition1 = firstWordWithoutMei[-1] in h.Kutriyalugaram and firstWordWithoutMei[-2] in h.idaiyinam_letters
        condition2 = firstWordWithoutMei[-1] in h.Kutriyalugaram and firstWordWithoutMei[-2] == tamil.utf8.aytham_letter
        if (condition1 or condition2):
            wordPairList[0] = ''.join(firstWordWithoutMei) 
    return wordPairList


def VD_Rule_7(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VD_Rule_7AdukkuIrattai(letters_in_1stWord,letters_in_2ndWord)
    return wordPair

def VD_Rule_7AdukkuIrattai(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] in h.vallinam_letters and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        first_length=len(letters_in_1stWord)-1
        firstWordWithoutMei = letters_in_1stWord[0:first_length]    
        if ((''.join(firstWordWithoutMei)) == (''.join(letters_in_2ndWord))):
            wordPairList[0] = ''.join(firstWordWithoutMei) 
    return wordPairList

def VD_Rule_8(wordList):
    corrected_list=[]
    for word in wordList:
        pos=-1
        charList = tamil.utf8.get_letters(word) 
        length=len(charList)
        for i in range(length):
            if((charList[i]==u'ற்' or charList[i]==u'ட்') and i!=length and charList[i+1] in h.vallinam_letters):
                pos=i+1  
        if(pos!=-1):
            charList.remove(charList[pos])
        corrected_list.append("".join(charList))
    return ' '.join(corrected_list)
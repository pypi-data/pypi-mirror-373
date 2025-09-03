from .. import helpers as h
import tamil

def VA_Rule_1(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    if wordPairList[0] in h.Migum_words_list and  letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList
    
    
def VA_Rule_2(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    charList = tamil.utf8.get_letters(wordPairList[0])
    if (charList[-1] in h.Van_Kutriyalugaram) and (charList[-2] in h.vallinam_letters) and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[wordPairList[1][0]]
        wordPairList[0] += Vmei_uyir_list[0]
    
    return wordPairList


def VA_Rule_3(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    charList = tamil.utf8.get_letters(wordPairList[0])
    if charList[-1] not in h.Van_Kutriyalugaram and charList[-1] in h.UyirMei_dict.keys() and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        split = h.UyirMei_dict[charList[-1]]
        if split[1] == u'உ':
            Vmei_uyir_list = h.UyirMei_dict[wordPairList[1][0]]
            wordPairList[0] += Vmei_uyir_list[0]
    elif (len(charList)==2) and (charList[1] in h.Van_Kutriyalugaram) and (charList[0] in h.Kuril_letters) and (letters_in_2ndWord[0] in h.VallinaUyirMeiLetters):
        Vmei_uyir_list = h.UyirMei_dict[wordPairList[1][0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList


def VA_Rule_4(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    charList = tamil.utf8.get_letters(wordPairList[0])
    split = h.UyirMei_dict[charList[-1]]
    if (split[1] == u'ஐ') and (letters_in_2ndWord[0] in h.VallinaUyirMeiLetters):
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
    elif (charList[-1] == u'கு') and (letters_in_2ndWord[0] in h.VallinaUyirMeiLetters):
        Vmei_uyir_list = h.UyirMei_dict[wordPairList[1][0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList


def VA_Rule_5(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    wordPair = VA_Rule_5_check_vinayechamRules(letters_in_1stWord,letters_in_2ndWord)
    return wordPair


def VA_Rule_5_check_vinayechamRules(letters_in_1stWord, letters_in_2ndWord):
    wordPairList = [''.join(letters_in_1stWord),''.join(letters_in_2ndWord)]
    if letters_in_1stWord[-1] == u'ய்' and letters_in_1stWord[-2] == u'போ' and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        #print("poi")
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
        #print(wordPairList)
       
    elif (letters_in_1stWord[-1] == u'ய்' or letters_in_1stWord[-1] == u'க') and letters_in_1stWord[-2] in h.UyirMei_dict.keys() and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        split = h.UyirMei_dict[letters_in_1stWord[-2]]
        if split[1] == u'ஆ':
            #print('aay and aaka')
            Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
            wordPairList[0] += Vmei_uyir_list[0]
    elif letters_in_1stWord[-1] in h.UyirMei_dict.keys() and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        split = h.UyirMei_dict[letters_in_1stWord[-1]]
        if split[1] == u'அ' or split[1] == u'இ':
            Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
            wordPairList[0] += Vmei_uyir_list[0]
    elif letters_in_1stWord[-1] == u'ன' and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        split = h.UyirMei_dict[letters_in_1stWord[-1]]
        if split[1] == u'எ' or letters_in_1stWord[-2] == u'எ':
            Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
            wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList


def VA_Rule_6(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    if (letters_in_1stWord[-1] in h.UyirMeiLetters) and (letters_in_2ndWord[0] in h.VallinaUyirMeiLetters):
        split = h.UyirMei_dict[letters_in_1stWord[-1]]
        if (split[1] == u'ஆ'):
            Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
            wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList


def VA_Rule_7(wordPairList):
    letters_in_1stWord = tamil.utf8.get_letters(wordPairList[0])
    letters_in_2ndWord = tamil.utf8.get_letters(wordPairList[1])
    if (len(letters_in_1stWord)==1) and (letters_in_1stWord[0] in h.oreluthuOrumozhi) and (letters_in_2ndWord[0] in h.VallinaUyirMeiLetters):
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList

def VA_Rule_8(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    if wordPairList[0] in h.Migum_words_list2 and  letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList


def VA_Rule_9(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    charList = tamil.utf8.get_letters(wordPairList[0])
    if (charList[-1] in h.Kutriyalugaram) and (charList[-2] in h.mellinam_letters) and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[wordPairList[1][0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList

def VA_Rule_10(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    charList = tamil.utf8.get_letters(wordPairList[0])
    if (charList[-1] in h.Kutriyalugaram) and (charList[-2] in h.Kuril_letters) and letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[wordPairList[1][0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList

def VA_Rule_11(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    if wordPairList[0] in h.urichol and  letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList
    
def VA_Rule_12(wordPairList):
    letters_in_2ndWord=tamil.utf8.get_letters(wordPairList[1])
    if wordPairList[0] in h.directions and  letters_in_2ndWord[0] in h.VallinaUyirMeiLetters:
        Vmei_uyir_list = h.UyirMei_dict[letters_in_2ndWord[0]]
        wordPairList[0] += Vmei_uyir_list[0]
    return wordPairList


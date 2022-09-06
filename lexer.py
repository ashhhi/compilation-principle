import json
from collections import defaultdict  #defaultdict可以一个key对应多个value
import os

#配置文件
readPath = 'lexer_config.json'
savePath = 'lexerOUTPUT.txt'
wordGrammerPath = "wordGrammer.txt"
numberGrammerPath = "numberGrammer.txt"

DIGIT="0123456789"
UPPER="ABCEDFGHIJKLMNOPQRSTUVWXYZ"
LOWER="abcdefghijklmnopqrstuvwxyz"

key_word_list = []
op_list = []
symbol_list = []

#读取Json文件
def readJson():
    f = open(readPath)
    List = json.load(f)
    for i in List.get('KEY_WORD'):
        key_word_list.append(i)
    for i in List.get('OP'):
        op_list.append(i)
    for i in List.get('SYMBOL'):
        symbol_list.append(i)

#状态类
class Status(object):
    def __init__(self,num,d):
        self.num = num
        self.d = d
    def advance(self,goAhead):
        flag = 0
        for value in self.d[str(self.num)]:
            if value[0] == goAhead:
                self.num = value[1]
                flag = 1
                break
        if flag == 1:
            return self
        else:
            return None

#DFA自动机判断是否符合词法
#text是要判断的元素 d是传入的wordTable或者numberTable
def DFA(text,d):
    flag = 0
    statu = Status(0,d)
    if len(d) < 10:     #判断该DFA是数字的还是标识字的
        fflag = 'word'
    else:
        fflag = 'number'
    for i in range(len(text)):
        goAhead = ''
        if fflag == 'word':
            if text[i] == '_':
                goAhead = '_'
            elif text[i] in UPPER or text[i] in LOWER:
                goAhead = 'alpha'
            elif text[i] in DIGIT:
                goAhead = 'digit'
        else:
            if text[i] in DIGIT:
                goAhead = 'digit'
            elif text[i] == '.':
                goAhead = '.'
            elif text[i] == 'E':
                goAhead = 'E'
            elif text[i] == '+':
                goAhead = '+'
            elif text[i] == '-':
                goAhead = '-'
            elif text[i] == 'i':
                goAhead = 'i'
        temp = statu.advance(goAhead)
        if temp == None:
            flag = 1
            break
        else:
            statu = temp
    if flag == 1:
        return False
    else:
        return True

#读取词法 并将NFA转换为DFA
def transformNFAtoDFA(path):
    d = defaultdict(list)
    t = [] #终结符
    f = open(path)
    text = []
    for l in f:
        text.append(l)
    #将文本存入defaultdict中
    for item in text:
        if item == '\n':
            continue
        item = item.split('\n')
        item = item[0].split(':')
        separate = item[1].split('|')
        for i in separate:
            latter = i.split(' ')
            d[str(item[0])].append([str(latter[0]),str(latter[1])])
    print(d)
    #子集法进行转换
    #1、算出每个状态的闭包，空在词法中以 $ 表示
    closure = defaultdict(list)
    for key in d.keys():
        for item in d[key]:
            if item[0] == '$':
                closure[str(key)].append(str(item[1]))
            else:
                if item[0] not in t:
                    t.append(item[0])
    #2、找状态
    DFA = defaultdict(list)    #存储每一个状态里对应的东西
    ADVANCE = defaultdict(list)    #存储状态转换线路
    stateNum = 0
    analyseNum = 0
    DFA[str(stateNum)].append('start')
    for item in closure['start']:
        DFA[str(stateNum)].append(item)
    while True:
        F = False
        for item in DFA[str(stateNum)]:
            if item in closure.keys():
                for value in closure[item]:
                    if value not in DFA[str(stateNum)]:
                        DFA[str(stateNum)].append(value)
                        F = True
        if F == False:
            break
    stateNum += 1
    while analyseNum != stateNum:
        for key in t:     #对每个终结符进行遍历
            temp = []
            for item in DFA[str(analyseNum)]:
                for item1 in d[str(item)]:
                    if item1[0] == key:
                        temp.append(item1[1])
            if len(temp) == 0:
                continue
            #找temp的闭包
            while True:
                F = False    #如果有新加入的元素就变True，否则一直为False跳出while循环
                for item in temp:
                    for p in closure[item]:
                        if p not in temp:
                            temp.append(p)
                            F = True
                if F == False:
                    break

            flag = False  #判断是否已经存在这个状态，False代表不存在，True代表存在
            num = 0
            for kk in DFA.keys():
                num = kk
                if len(DFA[kk]) != len(temp):
                    continue
                else:
                    cnt = 0
                    for i1 in temp:
                        if i1 not in DFA[kk]:
                            break
                        cnt += 1
                    if cnt == len(temp):
                        flag = True
                        break
            if flag == False:
                for i in temp:
                    DFA[str(stateNum)].append(i)
                ADVANCE[str(analyseNum)].append([str(key),str(stateNum)])
                stateNum += 1
            else:
                ADVANCE[str(analyseNum)].append([str(key), str(num)])
        analyseNum += 1
    print(DFA)
    print(ADVANCE)
    return ADVANCE


#将从输入中读取到的Token表存成一个txt文件
def outPutToken(text):
    readJson()
    numberTable = transformNFAtoDFA(numberGrammerPath)
    wordTable = transformNFAtoDFA(wordGrammerPath)
    text = ''.join(text)
    items = []
    temp = []
    flag = 0
    RR = 0
    for i in range(len(text)):
        if flag == 1:
            flag = 0
            items.append([''.join(temp), RR])
            temp = []
            continue
        if text[i] == '\n':
            if len(temp) != 0:
                items.append([''.join(temp), RR])
                temp = []
            RR += 1
            continue
        elif text[i] != '\t' and text[i] != ' ' and text[i] not in symbol_list and text[i] not in op_list:
            temp.append(text[i])
        elif text[i] in symbol_list:
            if len(temp) != 0:
                items.append([''.join(temp), RR])
            items.append([text[i], RR])
            temp = []
        elif text[i] in op_list:
            if len(temp) != 0:
                items.append([''.join(temp), RR])
                temp = []
            if text[i + 1] in op_list:
                if (text[i] + text[i + 1]) in op_list:
                    temp.append(text[i] + text[i + 1])
                    flag = 1
                    continue
            # elif items[len(items)-1][0] == '=':
            #     if text[i+1] in DIGIT:
            #         temp.append(text[i])
            #         continue
            else:
                items.append([text[i], RR])
        else:
            if len(temp) != 0:
                items.append([''.join(temp), RR])
            temp = []
        if i == len(text) - 1 and len(temp) != 0:
            items.append([''.join(temp), RR])
    print(items)
    f = open(savePath, 'w')
    for item in items:
        if item[0] in key_word_list:
            f.write("Type:关键字 Value:" + item[0] + " 行数:" + str(item[1]) + '\n')
        elif item[0] in op_list:
            f.write("Type:运算符 Value:" + item[0] + " 行数:" + str(item[1]) + '\n')
        elif item[0] in symbol_list:
            f.write("Type:限定符 Value:" + item[0] + " 行数:" + str(item[1]) + '\n')
        elif DFA(item[0], wordTable):
            f.write("Type:标识字 Value:" + item[0] + " 行数:" + str(item[1]) + '\n')
        elif DFA(item[0], numberTable):
            f.write("Type:常数量 Value:" + item[0] + " 行数:" + str(item[1]) + '\n')
        else:
            f.write("Type:错误量 Value:" + item[0] + " 行数:" + str(item[1]) + '\n')

if __name__ == '__main__':
    print(DFA('i',transformNFAtoDFA(wordGrammerPath)))
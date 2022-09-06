#导包
import copy
from collections import defaultdict  #defaultdict可以一个key对应多个value
from PyQt5 import uic
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from pythonds.basic.stack import Stack

from lexer import outPutToken

#定义FIRST集、FOLLOW集、项目族群
First = defaultdict(list)
Follow = defaultdict(list)
Closure = defaultdict(list)

#定义记录每个时候的状态的list（状态栈，数据站，输入缓冲区）用作ui界面显示
buffer_list = defaultdict(list)
in_list = defaultdict(list)
state_list = defaultdict(list)

List = []   #文法语句
Vt = ['$']     #终结符
V = []      #非终结符
ALL = []    #所有字符

#两个表
ACTION = defaultdict(list)
GOTO = defaultdict(list)

TokenPath = 'lexerOUTPUT.txt'
LanguagePath = 'Language.txt'

#分析词法分析器的结果Token
def lexerOut():
    d = defaultdict(list)
    TokenText = []
    f = open(TokenPath)
    for i in f:
        TokenText.append(i)

    for item in TokenText:
        # if item[5:8] == "关键字":
        #找到行数:
        index1 = 0
        for index in range(len(item)-1,-1,-1):
            if item[index] == ':':
                row = int(item[index+1:len(item)-1])
                index1 = index
                break
        #找到类型并转换为规则:
        if item[5:8] == "错误量":
            Type = '@'
        elif item[5:8] == "标识字":
            if item[15:index1 - 3] == 'print':
                Type = 'p'
            elif item[15:index1-3] == 'range':
                Type = 's'
            elif item[15:index1-3] == 'len':
                Type = 'l'
            else:
                Type = 'a'
        elif item[5:8] == "关键字":
            if item[15:index1-3] == 'def':
                Type = 'd'
            elif item[15:index1-3] == 'return':
                Type = 'r'
            elif item[15:index1-3] == 'if':
                Type = 'f'
            elif item[15:index1-3] == 'while':
                Type = 'w'
            elif item[15:index1-3] == 'break':
                Type = 'b'
            elif item[15:index1-3] == 'for':
                Type = 'o'
            elif item[15:index1-3] == 'in':
                Type = 'n'
            elif item[15:index1-3] == 'else':
                Type = 'e'
            elif item[15:index1-3] == 'end':
                Type = '#'
            elif item[15:index1-3] == 'True':
                Type = 'y'
            elif item[15:index1-3] == 'False':
                Type = 't'
            elif item[15:index1-3] == 'continue':
                Type = 'q'
        elif item[5:8] == "限定符":
            if item[15:index1-3] == ',':
                Type = '`'
            else:
                Type = item[15:index1-3]
        elif item[5:8] == "运算符":
            if item[15:index1-3] == '>=' or item[15:index1-3] == '<=' or item[15:index1-3] == '==' or item[15:index1-3] == '>' or item[15:index1-3] == '<':
                Type = 'c'
            else:
                Type = item[15:index1-3]
        elif item[5:8] == "常数量":
            Type = 'i'

        d[row].append([Type,item[15:index1-3]])
    return d

#读取文法文件
def readLanguage():
    LanguageText = ''
    f = open(LanguagePath)
    for i in f:
        LanguageText += i
    return LanguageText

#判断是不是为终结符，这里的大写字母不是终结符，其他的是
def isTerminal(item):
    if item>"Z" or item<"A":
        return True
    else:
        return False

#预处理，将文本文件的空格去除掉，并且以回车为分隔符分割为list形式
def preProcesser(text):
    str = ""    #str
    List = []   #list
    for i in text:
        if i == " ":
            continue
        else:
            str += i
    str = str.split('\n')   #list   ['E->E+T', 'E->T', 'T->T*F', 'T->F', 'F->(E)', 'F->i']

    # 把文法中E->A|B 切分为E->A和E->B
    str1 = []   #用来存储分离后的str
    for item in str:
        tempstr = ""
        temp = []
        for j in range(3,len(item)):
            if(item[j] == '|'):
                temp.append(tempstr)
                tempstr = ""
            elif j == len(item)-1:
                tempstr += item[j]
                temp.append(tempstr)
            else:
                tempstr += item[j]
        for k in temp:
            str1.append(item[0]+"->" +k)

    List.append(str[0][0]+"'->"+str[0][0])  #增广文法   ["E'->E", 'E->E+T', 'E->T', 'T->T*F', 'T->F', 'F->(E)', 'F->i']
    for i in str1:
        List.append(i)

    return List

#把文法编成defaultDict格式
def makeDefaultDictionary(List):
    d = defaultdict(list)
    for item in List:
        key = ""
        for j in range(0,len(item)):
            if item[j] != '-':
                key += item[j]
            else:
                j += 2
                break
        value = item[j:]
        d[key].append(value)
    return d

#求每个非终结符的FIRST集
def getFirst(d):
    first = defaultdict(list)
    for key in d.keys():
        first[key]
    #第一轮循环找到所有终结符开头的加入first集
    for key in d.keys():
        for value in d[key]:
            if value[0] in Vt:
                if value[0] not in first[key]:
                    first[key].append(value[0])
            else:
                continue
    while True:
        flag = False
        for key in d.keys():
            for value in d[key]:
                if value[0] in Vt:
                    continue
                else:
                    if len(first[value[0]]) != 0:
                        for liter in first[value[0]]:
                            if liter in first[key]:
                                continue
                            else:
                                first[key].append(liter)
                                flag = True
        if flag == False:
            break
    return first

#求一段字符串的FIRST集
def getStrFirst(str):
    mystr = ""
    flag = False
    for i in str:
        if i == '\'':
            continue
        if flag == True:
            mystr += i
        elif i == ',':
            flag = True

        elif i in Vt:
            return i
        else:
            if '0' not in First[i]:
                for value in First[i]:
                    mystr += value
                break
            else:
                for value in First[i]:
                    if value != '0':
                        mystr += value
    return mystr

#求每个非终结符的FOLLOW集
def getFollow(d):
    follow = defaultdict(list)
    for key in d.keys():
        follow[key]

    #只拿第一个key在后面加入美元结束符
    for firstkey in d.keys():
        follow[firstkey].append('$')
        break

    while True:
        flag = False
        for key in d.keys():
            for value in d[key]:
                for index in range(0,len(value)):
                    if value[index] in Vt:        #是终结符就查找下一个
                        continue
                    else:
                        if(index < len(value)-1):       #如果不是最后一个字符就进行
                            behind = index+1
                            if(value[behind] in Vt):         #如果后一个字符是终结符 直接加入follow集
                                if value[behind] not in follow[value[index]]:
                                    follow[value[index]].append(value[behind])
                                    flag = True
                            else:                                   #如果后一个字符不是终结符 把后一个字符的First集加入前面的Follow集中
                                while True:
                                    flag1 = False
                                    for item in First[value[behind]]:
                                        if item not in follow[value[index]] and item != '0':
                                            follow[value[index]].append(item)
                                            flag = True
                                    if '0' in First[value[behind]]:
                                        behind += 1
                                        flag1 = True
                                    if behind >= len(value)-1:  #如果后面的元素都可以为空，把key的Follow集加入index元素的Follow集中
                                        if len(follow[key]) != 0:
                                            for item in follow[key]:
                                                if item not in follow[value[index]]:
                                                    follow[value[index]].append(item)
                                                    flag = True
                                        break
                                    if flag1 == False:
                                        break

                        else:               #如果是最后一个字符，把key的Follow集加入index元素的Follow集中
                            if len(follow[key]) != 0:
                                for item in follow[key]:
                                    if item not in follow[value[index]]:
                                        follow[value[index]].append(item)
                                        flag = True
        if flag == False:
            break
    return follow

#填充每一个项目族
def fillClosure(closure,closureName,d):
    while True:
        flag = False
        for value in closure[closureName]:
            for index in range(0,len(value)):
                if value[index] == '.' and index < len(value)-3:
                    pre = index + 1
                    if value[pre] == '\'':
                        pre += 1
                    if isTerminal(value[pre]):              #如果.的下一个是终结符则不管
                        continue
                    else:                                       #如果.的下一个是非终结符则加入闭包
                        for value1 in d[value[pre]]:
                            strtemp = value[pre]+"->"+"."+value1+","+getStrFirst(value[pre+1:])
                            if strtemp not in closure[closureName]:
                                closure[closureName].append(strtemp)
                                flag = True
        if flag == False:
            break

#求项目族群
def closure(d):
    closure = defaultdict(list)

    global GOTO,ACTION
    GOTO = defaultdict(list)
    ACTION = defaultdict(list)

    closureName="I0"
    firstkey = ""
    #取开始状态
    for i in d.keys():
        firstkey = i
        break
    closure[closureName].append(firstkey+"->"+"."+d[firstkey][0]+",$")
    fillClosure(closure,closureName,d)

    #循环创建新的包
    num = 0     #从序号为0的状态开始，在while循环中每一次加一创建一个新的闭包
    newNum = 1
    while True:
        closureName = 'I'+ str(num)     #下一次要遍历的包的包名
        for liter in ALL:  # 遍历前进
            goFlag = False  #能否前进的标志
            newClosureName = 'I' + str(newNum)   #下一次创建的包名
            for value in closure[closureName]:  # 将符合条件的文法点右移
                index = 0
                while value[index] != '.':      #找到点的下标
                    index += 1
                indexdot = index
                while value[index] != ',':      #找到展望符的起点
                    index += 1
                if liter == value[indexdot+1]:
                    tempstr1 = value[:indexdot] + value[indexdot+1] + '.' + value[indexdot+2:]
                    if tempstr1 not in closure[newClosureName]:
                        closure[newClosureName].append(tempstr1)
                    goFlag = True

            if goFlag == False:
                continue
            fillClosure(closure, newClosureName, d)
            #判断该包是否已经存在
            fflag = True
            for i in range(0,newNum):
                flag = True
                if len(closure['I' + str(i)]) != len(closure[newClosureName]):
                    continue
                for value in closure[newClosureName]:
                    if value not in closure['I' + str(i)]:
                        flag = False
                        break
                if flag == True:        #包已经存在了

                    if liter in V:  # 如果是非终结符，加入GOTO表
                        if [str(i), liter] not in GOTO['I' + str(num)]:
                            GOTO['I' + str(num)].append([str(i), liter])
                    else:  # 如果是终结符，加入ACTION表
                        if ['s' + str(i), liter] not in ACTION['I' + str(num)]:
                            ACTION['I' + str(num)].append(['s' + str(i), liter])


                    closure.pop(newClosureName)
                    newNum -= 1
                    fflag = False
                    break
                else:
                    continue
            if fflag == True:        #说明新建了包，加入状态转换表
                if liter in V:  #如果是非终结符，加入GOTO表
                    if [str(newNum),liter] not in GOTO['I'+str(num)]:
                        GOTO['I'+str(num)].append([str(newNum),liter])
                else:            #如果是终结符，加入ACTION表
                    if ['s'+str(newNum),liter] not in ACTION['I'+str(num)]:
                        ACTION['I'+str(num)].append(['s'+str(newNum),liter])

            if goFlag == True:
                newNum += 1

        if num == newNum:
            break
        num += 1

    #补充ACTION表中的规约项和acc项
    for key in closure.keys():
        for value in closure[key]:
            index = 0
            for i in range(len(value)-1,0,-1):
                if(value[i] == ','):
                    index = i
                    break
            if value[index-1] == '.':   #','和'.'相邻的是可规约项
                temp = ""       #规约的语句
                index1 = 0      #要寻找的语句的List下标
                flag = False
                for i in value:
                    if i == '.':
                        break
                    temp += i
                for i in range(0,len(List)):
                    if temp == List[i]:
                        index1 = i
                        flag = True
                        break
                if(flag == True):
                    if index1 == 0:
                        if ["acc", value[len(value) - 1]] not in ACTION[key]:
                            ACTION[key].append(["acc", value[len(value) - 1]])
                    else:
                        for ii in range(index+1,len(value)):
                            if ['r'+str(index),value[ii]] not in ACTION[key]:
                                ACTION[key].append(['r'+str(index1),value[ii]])

    closure.pop(newClosureName)
    return closure

#ui界面类
class UI:
    def __init__(self,Language):
        qfile_stats = QFile("UI.ui")
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()
        self.ui = uic.loadUi("UI.ui")

        #文法和待识别字符串的修改
        #LR1分析器的参数
        self.Identify = ''
        self.Language = Language


        #编译器的参数
        self.Language2 = Language
        self.Code = ''

        self.ui.lineEdit.textChanged.connect(lambda :self.changeLanguage(0))
        self.ui.plainTextEdit.textChanged.connect(lambda :self.changeLanguage(1))
        self.ui.code.textChanged.connect(lambda :self.changeLanguage(1))

        self.lexerout = defaultdict(list)


        #递归用========================
        # 语义分析中出现过的变量名
        self.var = []
        #寄存器序号
        self.reg = 0
        #语义分析输出行数
        self.row = 0
        #标识符（变量名和常数）栈  运算符栈
        self.BSF_CONSTANT = Stack()
        self.SYMBOL = Stack()
        self.Priority = {'*':2,'/':2,'+':1,'-':1,'(':0,')':0}
        #==============================

        #标志是否已经语法分析过
        # self.flag = False
        #点击按钮开始进行计算处理
        self.ui.pushButton.clicked.connect(lambda :self.Parser(True,self.Identify))
        self.ui.pushButton_2.clicked.connect(lambda :self.preCalc(True))
        self.ui.pushButton_3.clicked.connect(self.delete)
        self.ui.pushButton_4.clicked.connect(self.LexerAndParser)
        self.ui.pushButton_5.clicked.connect(self.translate)

    def delete(self):
        self.ui.closure.clear()
        self.ui.first.clearContents()
        self.ui.first.setColumnCount(0)  # 控制表格有几列
        self.ui.first.setRowCount(0)  # 控制表格有几行

        self.ui.follow.clearContents()
        self.ui.follow.setColumnCount(0)  # 控制表格有几列
        self.ui.follow.setRowCount(0)  # 控制表格有几行

        self.ui.statetable.clearContents()
        self.ui.statetable.setColumnCount(0)  # 控制表格有几列
        self.ui.statetable.setRowCount(0)  # 控制表格有几行

        self.ui.identify.clearContents()
        self.ui.identify.setColumnCount(0)  # 控制表格有几列
        self.ui.identify.setRowCount(0)  # 控制表格有几行
        buffer_list.clear()
        in_list.clear()
        state_list.clear()
        # self.flag = False

    def changeLanguage(self,f):
        #改变文法
        if len(self.ui.plainTextEdit.toPlainText()) == 0:
            self.Language = self.Language2
        else:
            self.Language = self.ui.plainTextEdit.toPlainText()
        if len(self.ui.lineEdit.text()) != 0:
            self.Identify = self.ui.lineEdit.text()
        if len(self.ui.code.toPlainText()) != 0:
            self.Code = self.ui.code.toPlainText()

    def showDate(self):                                                 #将运行过程、First集、Follow集、项目族群显示在ui界面中
        #每一次show前先清除所有表格的数据
        self.ui.closure.clear()
        self.ui.first.clearContents()
        self.ui.first.setColumnCount(0)  # 控制表格有几列
        self.ui.first.setRowCount(0)  # 控制表格有几行

        self.ui.follow.clearContents()
        self.ui.follow.setColumnCount(0)  # 控制表格有几列
        self.ui.follow.setRowCount(0)  # 控制表格有几行

        self.ui.statetable.clearContents()
        self.ui.statetable.setColumnCount(0)  # 控制表格有几列
        self.ui.statetable.setRowCount(0)  # 控制表格有几行

        self.ui.identify.clearContents()
        self.ui.identify.setColumnCount(0)  # 控制表格有几列
        self.ui.identify.setRowCount(0)  # 控制表格有几行
        # print(self.ui.identify.item(1,1))

        global First, Follow, Vt, V, ALL, List, ACTION, GOTO, Closure

        #将项目集族写入图形界面
        for key in Closure.keys():
            self.ui.closure.append(key + ": ")
            for value in Closure[key]:
                self.ui.closure.append(value + " ")
            self.ui.closure.append('\n')

        #将Frist集写入图形界面
        maxFirst = 0            #得到最长的First集 便于设置表格列数
        for key in First.keys():
            if len(First[key]) > maxFirst:
                maxFirst = len(First[key])
        self.ui.first.setColumnCount(maxFirst)  # 控制表格有几列
        self.ui.first.setRowCount(len(V))  # 控制表格有几行
        for row in range(len(V)):
            current_list = First[V[row]]
            for column in range(len(current_list)):
                self.ui.first.setItem(row, column, QTableWidgetItem(current_list[column])   )
        self.ui.first.setVerticalHeaderLabels(V)    #设置行标签

        #将Follow集写入图形界面
        maxFollow = 0  # 得到最长的Follow集 便于设置表格列数
        for key in Follow.keys():
            if len(Follow[key]) > maxFollow:
                maxFollow = len(Follow[key])
        self.ui.follow.setColumnCount(maxFollow)  # 控制表格有几列
        self.ui.follow.setRowCount(len(V))  # 控制表格有几行
        for row in range(len(V)):
            current_list = Follow[V[row]]
            for column in range(len(current_list)):
                self.ui.follow.setItem(row, column, QTableWidgetItem(current_list[column]))
        self.ui.follow.setVerticalHeaderLabels(V)  # 设置行标签

        #将状态转换表(ACTION/GOTO)写入图形界面
        self.ui.statetable.setColumnCount(len(ALL))  # 控制表格有几列
        self.ui.statetable.setRowCount(len(Closure))  # 控制表格有几行
        rowLables = []
        ALL_reverse = Vt+V
        for i in range(0,len(Closure)):
            rowLables.append('I'+str(i))
        self.ui.statetable.setVerticalHeaderLabels(rowLables)  # 设置行标签
        self.ui.statetable.setHorizontalHeaderLabels(ALL_reverse)  # 设置列标签
        dd = {}
        for i in range(0,len(ALL_reverse)):
            dd[ALL_reverse[i]] = i
        for key in ACTION.keys():
            for value in ACTION[key]:
                self.ui.statetable.setItem(int(key[1:]), dd[value[1]], QTableWidgetItem(value[0]))
        for key in GOTO.keys():
            for value in GOTO[key]:
                self.ui.statetable.setItem(int(key[1:]), dd[value[1]], QTableWidgetItem(value[0]))

        if len(buffer_list) != 0:
            # 将语法分析过程写入图形界面
            rows = len(buffer_list)
            self.ui.identify.setColumnCount(3)  # 控制表格有几列
            self.ui.identify.setRowCount(rows)  # 控制表格有几行
            self.ui.identify.setHorizontalHeaderLabels(['状态栈','数据栈','输入缓冲区'])  # 设置列标签
            for i in range(0,rows):
                self.ui.identify.setItem(i, 0, QTableWidgetItem(str(state_list[i][0])))
                self.ui.identify.setItem(i, 1, QTableWidgetItem(str(in_list[i][0])))
                self.ui.identify.setItem(i, 2, QTableWidgetItem(str(buffer_list[i][0][::-1])))

    def preCalc(self,Only):
        global First,Follow,Vt,V,ALL,List,ACTION,GOTO,Closure
        print(self.Language)
        if Only == True:
            List = preProcesser(self.Language)  # ["E'->E", 'E->E+T', 'E->T', 'T->T*F', 'T->F', 'F->(E)', 'F->i']
        else:
            List = preProcesser(self.Language2)

        Dict = makeDefaultDictionary(List)

        V = []
        Vt = ['$']
        flag = False
        for key in Dict.keys():
            for value in Dict[key]:
                for index in range(0,len(value)):
                    if flag == True:
                        flag = False
                        continue
                    if isTerminal(value[index]):
                        if value[index] == '<' or value[index] == '>' or value[index] == '=':
                            if index < len(value)-1 and value[index+1] == '=':
                                Vt.append(value[index]+value[index+1])
                                flag = True
                            else:
                                Vt.append(value[index])
                        elif value[index] not in Vt:
                            Vt.append(value[index])
                    else:
                        if value[index] not in V:
                            V.append(value[index])

        ALL = V + Vt
        # 求First集
        First = getFirst(Dict)  # defaultdict(<class 'list'>, {"E'": ['(', 'i'], 'E': ['(', 'i'], 'T': ['(', 'i'], 'F': ['(', 'i']})


        # 求Follow集
        Follow = getFollow(Dict)  # defaultdict(<class 'list'>, {"E'": ['&'], 'E': ['&', '+', ')'], 'T': ['&', '+', '*', ')'], 'F': ['&', '+', '*', ')']})

        Closure = closure(Dict)
        for key in Closure.keys():
            print(key + str(Closure[key]))


        self.showDate()  # 将First集、Follow集、分析表显示在图形界面上

    #Only的含义是如果为True则只有LR1语法分析，False就是词法和语法分析都有，就是ui的第二个窗口，就不会显示分析过程，只会得到最终结果
    def Parser(self,Only,Identify):
        # if self.flag == False:
        if Only == True:
            self.preCalc(True)
        else:
            self.preCalc(False)
        global First,Follow,Vt,V,ALL,List,ACTION,GOTO,Closure
        buffer = Stack()  # 输入缓冲区
        buffer.push('$')

        #正向查找一下有无词法错误
        for i in range(0,len(Identify)):
            if Identify[i] == '@':
                key = ''
                value = ''
                kkk = 0
                fff = False
                for item in self.lexerout.keys():
                    for v in self.lexerout[item]:
                        if kkk == i:
                            key = item
                            value = v
                            fff = True
                            break
                        kkk += 1
                    if fff == True:
                        break
                self.ui.information.append("第" + str(key+1) + "行的 \"" + str(value[1]) + "\"词出现了词法错误")
                return False
        for i in range(len(Identify) - 1, -1, -1):
            if Identify[i] == ' ':
                continue
            buffer.push(Identify[i])
        In = Stack()  # 输入栈
        In.push('$')
        States = Stack()  # 状态栈
        States.push(0)

        buffer_list.clear()
        in_list.clear()
        state_list.clear()

        # 分析迭代次数
        buffer_list[0].append(copy.deepcopy(buffer.items))
        in_list[0].append(copy.deepcopy(In.items))
        state_list[0].append(copy.deepcopy(States.items))
        numstate = 1

        #记录当前程序跑到哪一个词，以便确定语法错误的地方
        cnt = 0

        #定义最多循环次数
        time = 10000
        while time:
            time -= 1
            flag = False
            state = 'I' + str(States.peek())
            current = buffer.peek()
            for value in ACTION[state]:
                if value[0] == 'acc' and buffer.size() == 1 and In.size() == 2:
                    flag = True
                    break
                if value[1] == current:
                    numLen = len(value[0])
                    if (numLen >= 3):
                        if numLen == 3:
                            num = 10 * int(value[0][1]) + int(value[0][2])
                        else:
                            num = 100 * int(value[0][1]) + 10 * int(value[0][2]) + int(value[0][3])
                    else:
                        num = int(value[0][1])
                    if value[0][0] == 's':
                        In.push(current)
                        buffer.pop()
                        States.push(num)
                        cnt += 1

                        #更新
                        buffer_list[numstate].append(copy.deepcopy(buffer.items))
                        in_list[numstate].append(copy.deepcopy(In.items))
                        state_list[numstate].append(copy.deepcopy(States.items))
                        numstate += 1

                    elif value[0][0] == 'r':
                        length = len(List[num]) - 3
                        while length:
                            In.pop()
                            States.pop()
                            length -= 1
                        In.push(List[num][0])
                        for value1 in GOTO['I' + str(States.peek())]:
                            if value1[1] == List[num][0]:
                                States.push(int(value1[0]))
                        # 更新
                        buffer_list[numstate].append(copy.deepcopy(buffer.items))
                        in_list[numstate].append(copy.deepcopy(In.items))
                        state_list[numstate].append(copy.deepcopy(States.items))
                        numstate += 1
                    break

            if flag == True:
                break

        if Only == True:
            self.showDate()  # 将First集、Follow集等显示在图形界面上
        if flag == True:
            return True
        else:
            # cnt += 1
            key = ''
            kkk = 0
            for item in self.lexerout.keys():
                if kkk+len(self.lexerout[item]) >= cnt:
                    key = item
                    break
                kkk += len(self.lexerout[item])
            if key != '':
                self.ui.information.append("第" + str(key + 1) + "行出现了语法错误")
            return False

    #集成词法分析和语法分析
    def LexerAndParser(self):
        outPutToken(self.Code)
        self.lexerout = lexerOut()
        self.ui.information.clear()
        text = ''
        for key in self.lexerout.keys():
            for value in self.lexerout[key]:
                text += value[0]
        if self.Parser(False,text) == False:
            print(111111)
            self.ui.information.append("=================编译错误=================\n")
            return False
        # else:
            # self.ui.information.append("pass\n")
        self.ui.information.append("=================成功编译！！！！=================")
        return True

    # 优先级：   */%:2  +-:1  （）:0
    #利用栈方法分析语义，第二个参数传的是上一层递归的优先级
    def Analyse(self,d):
        flag = False
        for I in range(0,len(d)+1):
            if flag == True:
                name = ''
                if (self.SYMBOL.isEmpty() == True and I == 1) or d[len(d)-1][1] == ')':
                    name = self.BSF_CONSTANT.peek()
                while self.SYMBOL.isEmpty() == False:
                    r1 = 0
                    r2 = 0
                    symbol = 0
                    if self.SYMBOL.isEmpty() == False:
                        symbol = self.SYMBOL.pop()
                    if self.BSF_CONSTANT.isEmpty() == False:
                        r1 = self.BSF_CONSTANT.pop()
                    if self.BSF_CONSTANT.isEmpty() == False:
                        r2 = self.BSF_CONSTANT.pop()
                    name = 'r' + str(self.reg)
                    self.reg += 1
                    s = "(" + str(self.row) + '):' + name + ' = ' + str(r1) + ' ' + str(symbol) + ' ' + str(r2)
                    self.row += 1
                    print(s)
                    self.ui.information2.append(s)
                    self.BSF_CONSTANT.push(name)
                if self.SYMBOL.isEmpty() == True:
                    self.BSF_CONSTANT.pop()
                    return name
            # 如果是运算符+-*/(
            if d[I][0] == '+' or d[I][0] == '-' or d[I][0] == '*' or d[I][0] == '/' or d[I][0] == '(':
                if self.SYMBOL.isEmpty() or d[I][0] == '(':
                    self.SYMBOL.push(d[I][1])
                else:       #如果不是空则判断优先级  若加入的优先级大于栈顶的优先级则push，否则pop栈直到加入优先级小于等于栈顶优先级
                    if self.Priority[d[I][1]]>self.Priority[self.SYMBOL.peek()]:
                        self.SYMBOL.push(d[I][1])
                    else:
                        while self.SYMBOL.isEmpty() == False and self.Priority[self.SYMBOL.peek()] > self.Priority[d[I][1]]:
                            r1 = 0
                            r2 = 0
                            symbol = 0
                            if self.SYMBOL.isEmpty() == False:
                                symbol = self.SYMBOL.pop()
                            if self.BSF_CONSTANT.isEmpty() == False:
                                r1 = self.BSF_CONSTANT.pop()
                            if self.BSF_CONSTANT.isEmpty() == False:
                                r2 = self.BSF_CONSTANT.pop()
                            name = 'r' + str(self.reg)
                            self.reg += 1
                            s = "("+str(self.row)+'):'+ name +' = '+str(r1) + ' ' +str(symbol)+ ' ' + str(r2)
                            print(s)
                            self.ui.information2.append(s)
                            self.row += 1
                            self.BSF_CONSTANT.push(name)
                        self.SYMBOL.push(d[I][1])

            #如果是右括号）
            elif d[I][0] == ')':
                while self.SYMBOL.peek() != '(':
                    r1 = 0
                    r2 = 0
                    symbol = 0
                    if self.SYMBOL.isEmpty() == False:
                        symbol = self.SYMBOL.pop()
                    if self.BSF_CONSTANT.isEmpty() == False:
                        r1 = self.BSF_CONSTANT.pop()
                    if self.BSF_CONSTANT.isEmpty() == False:
                        r2 = self.BSF_CONSTANT.pop()
                    name = 'r' + str(self.reg)
                    self.reg += 1
                    s = "(" + str(self.row) + '):' + name + ' = ' + str(r1) + ' ' + str(symbol) + ' ' + str(r2)
                    print(s)
                    self.ui.information2.append(s)
                    self.row += 1
                    self.BSF_CONSTANT.push(name)
                self.SYMBOL.pop()
                if I == len(d)-1:
                    flag = True


            #如果不是运算符:
            else:
                index = -1
                for i in range(0,len(self.var)):
                    if d[I][1] == self.var[i][1]:
                        index = i
                        break
                if index != -1:     #存在
                    self.BSF_CONSTANT.push(self.var[index][0])
                else:
                    name = 'r' + str(self.reg)
                    self.reg += 1
                    s = "(" + str(self.row) + '):' + name + ' = ' + d[I][1]
                    self.row += 1
                    print(s)
                    self.ui.information2.append(s)
                    self.var.append([name,d[I][1]])
                    self.BSF_CONSTANT.push(name)
                if I == len(d)-1:
                    flag = True

    #语义分析
    def translate(self):
        self.ui.information2.clear()
        #编译错误
        if self.LexerAndParser() == False:
            self.ui.information2.append("编译出现问题，无法进行语义分析\n")
            return False

        #编译成功
        #判断是否只是+-*/赋值运算的语法，如若不是，输出不能进行语义分析的信息
        lexerout = lexerOut()
        #判断是不是可分析的语法——加减乘除
        for key in lexerout.keys():
            for value in lexerout[key]:
                if value[0] != 'a' and value[0] != 'i' and value[0] != '='and value[0] != '+' and value[0] != '-' and value[0] != '*' and value[0] != '/' and value[0] != '(' and value[0] != ')':
                    self.ui.information2.append("对不起！！该语义分析器只能实现加减乘除四则运算的简单语义分析！！\n")
                    return False

        #清空所有栈
        self.BSF_CONSTANT = Stack()
        self.SYMBOL = Stack()
        self.var.clear()
        self.reg = 0
        self.row = 0


        for key in lexerout.keys():
            returnName = self.Analyse(lexerout[key][2:])
            # name = 'r' + str(self.reg)
            # self.reg += 1
            s = "("+str(self.row)+'):'+ lexerout[key][0][1] +' = '+ returnName
            self.row += 1
            self.var.append([returnName,lexerout[key][0][1]])
            print(s)
            self.ui.information2.append(s)

if __name__ == '__main__':
    language = readLanguage()
    app = QApplication([])
    Ui = UI(language)
    Ui.ui.show()
    app.exec_()
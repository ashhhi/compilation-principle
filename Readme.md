# 软件课程设计Ⅱ（Python迷你编译器）

## 1、项目文件介绍：

![image-20220502142312325](C:\Users\DELL\AppData\Roaming\Typora\typora-user-images\image-20220502142312325.png)

txt文件：

- Language.txt：定义语法分析中的二型文法
- lexerOUTPUT.txt：词法分析输出的Token令牌表
- numberGrammer.txt：数字的词法
- wordGrammer.txt：标识符的词法
- 二型文法文法说明：如题

json文件：

- lexer_config.json：定义了关键字、限定符、运算符

代码文件：

- UI.ui：定义了程序的代码界面
- lexer.py：词法分析的执行程序
- main：语法分析的执行程序，其中也可以直接调用lexer.py和UI.ui，为整个程序的main入口



## 2、项目启动：

​		整个项目通过“main.py”文件进行启动，会打开一个UI界面，该项目的一切操作都在UI界面中完成

## 3、两个界面：

### 3.1、LR(1)分析器界面

<img src="C:\Users\DELL\AppData\Roaming\Typora\typora-user-images\image-20220423160623375.png" alt="image-20220423160623375" style="zoom:50%;" />

​		左边上面为文法输入框，下面为待识别字符串输入框，右边为LR(1)分析过程显示框，点击分析语法可以得到First集、Follow集、项目族群和状态转换表，或者直接点击判断语句，会自动分析语法并显示出识别LR(1)分析识别过程。



### 3.2、编译器界面



<img src="C:\Users\DELL\AppData\Roaming\Typora\typora-user-images\image-20220423161100592.png" alt="image-20220423161100592" style="zoom:50%;" />

​		编译器界面分为代码输入框，以及编译结果和语义分析结果的两个结果显示框。当输入代码后点击编译按钮会在编译结果框中显示“编译成功”或“编译失败”，并打印出对应的报错信息。



## 4、代码解析：

###4.1、词法分析代码：

####4.1.1、输入文件

词法分析层的输入为：

- 编译器界面中的代码输入文本框中的内容
- 一个json文件（定义关键字、运算符和限定符）和两个txt文件（正规文法）

```json
//lexer_config.json文件
{
  "KEY_WORD": [
    "False","None", "True","and","as", "assert","break",
    "class","continue", "def","del","elif", "else","except",
    "finally", "for", "from","global","if","import","in","is",
    "lambda", "nonlocal","not","or","pass","raise", "return",
    "try","while","with","yield"
  ],
  "OP": [
    "+", "-", "*", "/", "+=", "-=", "*=", "/=",
    "++", "--", "&", "|", "~", "&&", "||",
    "<", ">", "=", "<=", ">=", "==", "!="
  ],
  "SYMBOL": [",", "(", ")", "[", "]", "{", "}",":"]
}
```

```txt
//numberGrammer.txt 数字的正规文法

start:$ int|+ int|- int|$ float|+ float|- float|$ science|+ science|- science|$ complex|- complex|+ complex

int:digit int|$ digit

float:digit float|$ digit|. float_next|digit int

science:digit science_first

science_first:. science_first_dot|E science_second
science_first_dot:digit science_first_dot|E science_second

science_second:digit end|digit science_second|. science_second_dot
science_second_dot:digit science_second_dot|digit end

complex:$ complex_second|digit complex_first

complex_first:. complex_first_dot|+ complex_second|- complex_second
complex_first_dot:digit complex_first_dot|+ complex_second|- complex_second

complex_first:E complex_first_science
complex_first_dot:E complex_first_science

complex_first_science:digit complex_first_science|. complex_first_science_dot|+ complex_second|- complex_second
complex_first_science_dot:digit complex_first_science_dot|+ complex_second|- complex_second

complex_second:digit complex_second|. complex_second_dot|i end|E complex_second_science
complex_second_dot:digit complex_second_dot|i end|E complex_second_science

complex_second_science:digit complex_second_science|. complex_second_science_dot|i end
complex_second_science_dot:digit complex_second_science_dot|i end
```

```txt
//wordGrammer.txt  标识符的正规文法
start:_ word|alpha word
word:digit word|digit end|alpha word|alpha end|_ word
```



#### 4.1.2、输出文件

```txt
//lexerOUTPUT.txt
//输入的代码不同对应的输出也不同，但都是如下所示的三元组Token令牌表

Type:标识字 Value:a 行数:0
Type:运算符 Value:= 行数:0
Type:常数量 Value:1 行数:0
Type:标识字 Value:c 行数:1
Type:运算符 Value:= 行数:1
Type:标识字 Value:a 行数:1
Type:运算符 Value:+ 行数:1
Type:标识字 Value:b 行数:1
Type:标识字 Value:print 行数:2
Type:限定符 Value:( 行数:2
Type:标识字 Value:b 行数:2
Type:限定符 Value:) 行数:2
```



#### 4.1.3、源代码

#####导包、定义配置文件路径和全局变量

​		defaultDict为本次课程设计使用的最主要的数据结构，他是Python内部自定的一个数据结构，底层实现为字典加列表，通过这个数据结构可以很容易地定义出词法中的DFA状态转换路线，或者后面语法分析中地项目族群，First集和Follow集等

```python
import json
from collections import defaultdict  #defaultdict可以一个key对应多个value

#配置文件
readPath = 'lexer_config.json'
savePath = 'lexerOUTPUT.txt'
wordGrammerPath = "wordGrammer.txt"
numberGrammerPath = "numberGrammer.txt"

DIGIT="0123456789"
UPPER="ABCEDFGHIJKLMNOPQRSTUVWXYZ_"
LOWER="abcdefghijklmnopqrstuvwxyz_"

key_word_list = []
op_list = []
symbol_list = []
```



##### 预处理

```python
#读取Json文件
def readJson():
#读取数据，并且从中得到DFA
def textSplit(path):
```



##### DFA

```python
#状态类
class Status(object):
        def __init__(self,num,d):
        self.num = num	#DFA对应的状态序号
        self.d = d		#d表示标识的是哪一个DFA，数字DFA还是标识字DFA
    def advance(self,goAhead):#前向传播，对应DFA图中的每一条线，goAhead为线上对应的终结符，通过goAhead找到下一个状态
```

```python
#DFA自动机判断是否符合词法
#text是要判断的元素 d是传入的wordTable或者numberTable
def DFA(text,d):
```

```python
#读取词法 并将NFA转换为DFA
def transformNFAtoDFA(path):
```

##### 输出

```python
#将从输入中读取到的Token表存成一个txt文件
def outPutToken(text):
```



### 4.2、语法分析和语义分析

#### 4.2.1、输入文件

- 词法分析中输出的“lexerOUTPUT.txt”文件
- Python语言的二型文法

```txt
//Language.txt

S->A|B

A->DA
A->D

D->da(a):B#|da(a):Br#

B->CB
B->C

C->G|P|R|U|N|O|q|b
G-> a = E|a = i|a = a|a = U
P->p ( E )
R->r E
U->a ( a )
N->f I:B e:B # |f I:B #|w I: B #
I->E c E|E c E|E c E|E c E|E c E|E|y|t
O->o a n s(i`i):B #|o a n a:B #|o a n s(i`l(a)):B #

E->E + T|T|E - T|T - E
T->T * F|T / F|F / T
T->F
F->(E)
F->i|a|U
```



#### 4.2.2、输出文件

​		输出在UI界面中，详情见3.2节



#### 4.2.3、源代码

##### UI类（语义分析）

​		语义分析镶嵌在UI类中，在语法分析后进行：

```python
class UI:
    #初始话参数和定义Qpushbutton按钮所对应的槽函数
    def __init__(self,Language):
        
    #清空UI显示页面
    def delete(self):
    
    #UI界面中每一次文本框中有文本改变，自动调用该方法进行重置底层数据结构
    def changeLanguage(self,f):    
        
    #将运行过程、First集、Follow集、项目族群显示在ui界面中
    def showDate(self):
    
    #预计算，计算出First集、Follow集、项目族群和ACTION、GOTO状态转换表，Only的含义是如果为True则只有LR1语法分析，False就是词法和语法分析都有，也就是ui的第二个窗口
    def preCalc(self,Only):
        
    #Only的含义同上，若为False就不会显示分析过程，只会得到最终编译结果：成功或者失败，Identify是待识别的字符串
    def Parser(self,Only,Identify):
        
    #集成词法分析和语法分析，若点击第二个窗口中的编译按钮将会调用此函数，此函数通过把代码一行一行地交给Parser函数处理得到返回结果
    def LexerAndParser(self):
        
    #优先级：  */  >  +-  >  ()
    #利用栈方法分析简单四则运算的语义，d参数是每一行语句对应的Token表
    def Analyse(self,d):
        
    #语义分析，若点击第二个窗口中的语义分析按钮将会调用此函数，此函数通过把代码一行一行地交给Analyse函数处理得到返回结果
    def translate(self):
```



##### 导包，定义配置文件路径和全局变量

```python
#导包，PyQt5为Python中内嵌的QT界面开发包
import copy
from collections import defaultdict  #defaultdict可以一个key对应多个value
from PyQt5 import uic
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from pythonds.basic.stack import Stack

#调用第一层的词法处理程序
from myDesign.lexerLayer.lexer import outPutToken
```

```python
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

#输入文件的对应路径
TokenPath = 'lexerOUTPUT.txt'
LanguagePath = 'Language.txt'
```



##### 预处理

```python
#分析词法分析器的结果Token
def lexerOut():
    
#读取文法文件
def readLanguage():
    
#判断是不是为终结符，这里的大写字母不是终结符，其他的是
def isTerminal(item):
    
#预处理，将文本文件的空格去除掉，并且以回车为分隔符分割为list形式
def preProcesser(text):

#把文法编程defaultDict格式
def makeDefaultDictionary(List):
```



##### First集和Follow集

```python
#求每个非终结符的FIRST集
def getFirst(d):

#求一段字符串的FIRST集
def getStrFirst(str):
    
#求每个非终结符的FOLLOW集
def getFollow(d):
```



##### 项目族群

```python
#填充每一个项目族
def fillClosure(closure,closureName,d):

#求项目族群，调用上面的fillClosure
def closure(d):
```



## 5、测试样例：

####5.1、LR(1)分析测试样例

- 文法：

S->aAcBe
A->b
A->Ab
B->d

- 待识别字符串：

abbcde

测试结果（仅展示了识别过程）:

![image-20220502141928190](C:\Users\DELL\AppData\Roaming\Typora\typora-user-images\image-20220502141928190.png)

#### 5.2、Python编译测试样例

```python
def swap(a):
    a = 1
    b = 2*a
    c = swap(b)
    if a == 2:
        print(c)
        end			
    for i in range(0,5):
        print(i)
        sum = i+sum
        end
    while a == b:
        print(a)
        if a==b:
           print(c+a)
           end
        end
    return 0
    end
```

测试结果：

![image-20220504020916049](C:\Users\DELL\AppData\Roaming\Typora\typora-user-images\image-20220504020916049.png)

#### 5.3、语义分析测试样例（仅能测试加减乘除四则运算）

```python
a = (1+2)*3+4
b = 3/3 + 1*2
c = a + b
```

![image-20220502141822253](C:\Users\DELL\AppData\Roaming\Typora\typora-user-images\image-20220502141822253.png)




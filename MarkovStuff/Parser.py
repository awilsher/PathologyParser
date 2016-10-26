import re,random,string

htmlRegex = re.compile(r'<.*?>')
paramRegex = re.compile(r'\\[^ ]*')
nlRegex = re.compile(r'\\PARD|\\PAR|<BR>')

class DataSet:
    def __init__(self):
        self.rows = []

    def addRow(self,row):
        self.rows.append(row)

    def summary(self):
        r = {}
        t = {}
        for x in self.rows:
            c = len(x.simpleParse[1])
            if c not in t:
                t[c] = [1,{}]
            else:
                t[c][0] += 1

            for y in x.simpleParse[1]:
                if y[1] not in t[c][1]:
                    t[c][1][y[1]] = 1
                else:
                    t[c][1][y[1]] +=1

            c = len(x.simpleParse[2])
            if c not in r:
                r[c] = [1,{}]
            else:
                r[c][0] += 1

            for y in x.simpleParse[2]:
                if y[1] not in r[c][1]:
                    r[c][1][y[1]] = 1
                else:
                    r[c][1][y[1]] +=1
                    
        return r,t
    def wordCounts(self):
        def addColumn(data,names,name):
            for x in data:
                x.append(0)
            j = len(names)
            names[name] = j
        data = []
        names = {}
        for x in self.rows:
            d = [0 for x in names]
            for y in x.wordCounts:
                if y not in names:
                    addColumn(data,names,y)
                    d.append(0)
                d[names[y]] = x.wordCounts[y]
            data.append(d)
        return data,names
        
        
resultTags = [x.strip() for x in '''NON-REACTIVE
NEGATIVE
NONREACTIVE
EQUIVOCAL
LOW_POSITIVE
NEAT
NON_REACTIVE
NR = NON-REACTIVE
BORDERLINE
TO FOLLOW
DETECTED
REACTIVE
LOW_REACTIVE
INDETERMINATE
PENDING
NON REAC
LOW STABLE
WEAKREACTIVE
LOW LEVEL
FTA TO FOLLOW
POSITIVE
AWAITING CONF
<POSITIVE 1/2
R128
NOT_DETECTED
REACTIVEMINIMAL
MINIMAL REACTIVE'''.split('\n')]

testTag = [x.strip() for x in '''ANTIBODIES TO TREPONEMA PALLIDUM
CMIA TOTAL ANTIBODY
FTA-ABS
F.T.A. ABSORPTION
F.T.A. ABS.
RAPID PLASMA REAGIN TEST
REAGIN ANTIBODY
RPR
RPR AB TITRE
RPR TITRE
SYPHILIS AB
SYPHILIS EIA TOTAL AB
SYPHILIS FTA-ABS
SYPHILIS SCREEN (CMIA)
SYPHILIS SEROLOGY (CMIA)
SYPHILIS TP
SYPHILIS (CMIA)
SYPHILIS (CMIA) SCREEN
TPHA
TPPA
TREPONEMA PALLIDUM IGG
TREPONEMAL AB (CMIA)
TREPONEMAL AB (EIA)
TREPONEMAL ANTIBODIES (ARCHITECT)
TREPONEMAL ANTIBODIES (CENTAUR)
TREPONEMAL ANTIBODY SCREEN
T_PALLIDUM IGG
T_PALLIDUM TOTAL AB
T_PALLIDUM TOTAL AB (CMEIA)
T_PALLIDUM TOTAL AB (EIA)
T.P.H.A.
T.P.P.A.
VDRL
TPALLIDUM DNA NAA
+ TPALLIDUM FTA-ABS
TPALLIDUM TOTAL AB EIA
EIA TOTAL AB
FTA
FTA ABSORPT
FTA ABSORPTION
SYPHILIS ANTIBODY
SYPHILIS ARCHITECT
SYPHILIS CMIA
SYPHILIS CMIA SCREEN
SYPHILIS EIA
SYPHILIS SCREEN
SYPHILIS SCREEN CMIA
SYPHILIS SEROLOGY CMIA
SYPHILIS-TP
SYPHILISEIA SCREEN
TOTAL AB
TPALLIDU TOTAL AB
TPALLIDUM FTA-ABS
TPALLIDUM IGG
TPALLIDUM TAL AB CMEIA
TPALLIDUM TOTAL AB
TPALLIDUM TOTAL AB CMEIA
TPALLIDUM TOTAL B CMEIA
TREPONE PALLIDUM IGG
TREPONEMA LIDUM IGG
TREPONEMA PALLIDU IGG
TREPONEMA PALLIDUM - PCR DEVELOPMENTAL
TREPONEMA PALLIDUM ANTIBODY
TREPONEMA PALLIDUM GG
TPPA TREPONEMA PALLIDUM PARTICLE AGGLUTINATION
TREPONEMAL AB
TREPONEMAL AB CMIA
TREPONEMAL AB EIA
TREPONEMAL ANTIBODIES ARCHITECT
TREPONEMAL ANTIBODIES CENTAUR
TREPONEMAL B CMIA'''.split('\n')]

wordIndex = {}

class DataRow:
    def __init__(self):
        self.data = []
        self.mainData = []
        self.simpleParse = []

    def setData(self,data):
        self.data = data
        self.mainData = data[-1]

    def formatRow(self):
        self.mainData = paramRegex.sub('',htmlRegex.sub('', nlRegex.sub('\n',self.mainData)))

    def processRow(self):
        result = []
        test = []
        for x in resultTags:
            if x in self.mainData:
                result.append((x,self.mainData.count(x)))
        for x in testTag:
            if x in self.mainData:
                test.append((x,self.mainData.count(x)))
        self.simpleParse = [self.mainData == '',test,result]

    def getWordCounts(self):
        #data = paramRegex.sub('',htmlRegex.sub('', nlRegex.sub(' | ',self.mainData)))
        data = self.mainData
        words = data.split()
        self.wordCounts = {}
        r = [0 for x in wordIndex]
        for x in words:
            if x not in wordIndex:
                j = len(wordIndex)
                wordIndex[x] = j
                r.append(0)
                if j % 1000 == 0:
                    print(j)
            r[wordIndex[x]] += 1
        outputFile.write(','.join([str(x) for x in r]) + '\n')

    def countWords(self):
        #data = paramRegex.sub('',htmlRegex.sub('', nlRegex.sub(' | ',self.mainData)))
        data = self.mainData
        words = data.split()
        self.wordCounts = {}
        for x in words:
            if x in self.wordCounts:
                self.wordCounts[x] += 1
            else:
                self.wordCounts[x] = 1
        
def loadFile(file,rowFunction=None):
    f = open(file,encoding='utf-8')
    d = f.read()
    f.close()
    d = d.split('\n')

    res = DataSet()
    for x in d:
        y = x.split(',',3)
        r = DataRow()
        r.setData(y)
        if rowFunction != None:
            rowFunction(r);
        res.addRow(r)
        
    return res

def dummyDataSet(numberOfFileTypes,records,tests,results):
    ruleWords = ['TEST','RESULT','SUB','TEST:','\n']
    ruleSpace = ['   ','  ','\n',':']
    l1 = len(ruleWords)-1
    l2 = len(ruleSpace)-1
    res = DataSet()

    templates = []
    for x in range(numberOfFileTypes):
        t = [random.randint(0,20),random.randint(0,20),
             random.randint(0,20),random.randint(20,100),[]]
        for x in range(10):
            if x > 2 and random.random()*x>0.2:
                break
            w = (ruleSpace[random.randint(0,l2)] if x > 0 else '')
            for y in range(10):
                if y > 0 and random.random()*y>0.2:
                    break
                w += ruleWords[random.randint(0,l1)]+ruleSpace[random.randint(0,l2)]
            t[4].append(w)
        print(t[4])
        templates.append(t)
    
    for x in range(records):
        t = random.choice(templates)
        v = ''
        sub = ''
        while len(sub) < t[1]:
            chars = "".join( [random.choice(string.ascii_letters) for i in range(random.randint(2,10))])
            s = "".join([' ' for i in range(random.randint(1,5))])
            sub += chars + s
        v += sub
        sub = ''
        i = -1
        s = tests
        for y in t[4]:
            sub += (random.choice(s) if i != -1 else '') + y
            if i >= 0:
                s = results
            i += 1
        v += sub
        sub = ''
        while len(sub) < t[3]:
            chars = "".join( [random.choice(string.ascii_letters) for i in range(random.randint(2,10))])
            s = "".join([' ' for i in range(random.randint(1,5))])
            sub += chars + s
        
        r = DataRow()
        r.setData([v])
        res.addRow(r)
        
    return res

def move(fromFile,toFile,start,length):
    f = open(fromFile,'rb')
    t = open(toFile,'wb')
    f.read(start)
    if length==-1:
        t.write(f.read()
                .replace(b'\xb5',b'u')
                .replace(b'\xb3',b'u')
                .replace(b'\xb0',b'u')
                .replace(b'\xc2',b'u')
                .replace(b'\xd5',b'u')
                .replace(b'\xdf',b'u')
                .replace(b'\x96',b'u'))
    else:
        t.write(f.read(length))
    t.close()
    f.close()

#move('syp.csv','small.csv',0,-1)    
#r = loadFile('small2.csv')


import db
import Parser as parser
import Tags
import Markov
import ModelBuilder


NEWLINE = 1
WORD = 2
SPACE = 3
TAG = 4
EOF = 5
SOF = 6

CUTOFF = 40
RULECUTOFF = 8

WINDOWSIZE = 2


tl = '''SYPHILIS AB
TREPONEMA PALLIDUM IGG
TREPONEMAL ANTIBODY SCREEN
T_PALLIDUM IGG
TREPONEMAL B CMIA'''.split('\n')

rl = '''NON-REACTIVE
NEGATIVE
NONREACTIVE
EQUIVOCAL
LOW_POSITIVE
NEAT'''.split('\n')

#tl = ['Test1','Sample Test','The other test']
#rl = ['POSITVE','Non Negative','NA','Mostky ok']

tests = Tags.TagSet('Tests')
tests.labels = [Tags.Tag(ModelBuilder.splitText(x.strip())) for x in tl]

results = Tags.TagSet('Results')
results.labels = [Tags.Tag(ModelBuilder.splitText(x.strip())) for x in rl]
        
def tagsFromFullRules(data,rules,nodes,tags,rowIndex=0):
    text = data.mainData
    words = splitText(text)
    for index,x in enumerate(rules):
        s = 0
        l = len(x[1])
        while s < l and x[1][s].getData()[1] != TAG:
            s += 1
        if s != 0 and s != l:
            i = boyerMoore([y.getData() for y in x[1][:s]],words)
            
            if i != -1:
                s2 = s+1
                while s2 < l and x[1][s2].getData()[1] != TAG:
                    s2 += 1

                j = -1
                if s2 > s+1:
                    j = boyerMoore([y.getData() for y in x[1][s+1:s2]],words,i)
                if j != -1:
                    ts = x[1][s].getData()[0]
                    if ts not in tags:
                        tags[ts] = {}
                    print(index,rowIndex)
                    tag = Tag(words[i+s:j])
                    if tag not in tags[ts]:
                        tags[ts][tag] = [tag,1]
                    else:
                        tags[ts][tag][1] += 1
            
def tagsFromPartRules(data,rules,nodes,tags,rowIndex=0):
    text = data.mainData
    words = splitText(text)
    for index,x in enumerate(rules):
        s = 0
        l = len(x[1])
        while s < l and x[1][s].getData()[1] != TAG:
            s += 1
        if s != 0 and s != l:
            i = boyerMoore([y.getData() for y in x[1][:s]],words)
            
            if i != -1:
                p = i+s+1
                while p < len(words) and (words[p][1] == WORD or (words[p][1] == SPACE and words[p][0] == ' ')):
                    p += 1 
                ts = x[1][s].getData()[0]
                if ts not in tags:
                    tags[ts] = {}
                print(index,rowIndex)
                if p != i+s+i:
                    tag = Tag(words[i+s:p])
                    if tag not in tags[ts]:
                        tags[ts][tag] = [tag,1]
                    else:
                        tags[ts][tag][1] += 1
                        
                continue
                print('head',i,index,rowIndex)
                s2 = s+1
                while s2 < l and x[1][s2].getData()[1] != TAG:
                    s2 += 1

                j = -1
                if s2 > s+1:
                    j = boyerMoore([y.getData() for y in x[1][s+1:s2]],words,i)
                if j != -1:
                    ts = x[1][s].getData()[0]
                    if ts not in tags:
                        tags[ts] = {}
                    print(index,rowIndex)
                    tag = Tag(words[i+s:j])
                    if tag not in tags[ts]:
                        tags[ts][tag] = [tag,1]
                    else:
                        tags[ts][tag][1] += 1
        elif s == 0:
            s2 = s+1
            while s2 < l and x[1][s2].getData()[1] != TAG:
                s2 += 1

            j = -1
            if s2 > s+1:
                j = boyerMoore([y.getData() for y in x[1][s+1:s2]],words,i)
            if j != -1:
                ts = x[1][s].getData()[0]
                if ts not in tags:
                    tags[ts] = {}
                print(index,rowIndex)
                p = j-1
                while p >= 0 and (words[p][1] == WORD or (words[p][1] == SPACE and words[p][0] == ' ')):
                    p -= 1
                if p != j-1:
                    tag = Tag(words[p+1:j])
                    if tag not in tags[ts]:
                        tags[ts][tag] = [tag,1]
                    else:
                        tags[ts][tag][1] += 1
                        
def traverse(node,indent,tested = {},prob=0):
    print('  ' * indent,prob,"'" + str(node.getData()[0]) + "'")
    if node in tested:
        return
    tested[node] = True
    m = -1
    mi = -1
    mi2 = -1
    for x in node.transitions:
        if node.transitions[x][1] > m:
            m = node.transitions[x][1]
            mi2 = mi
            mi = x
    if m != -1:
        traverse(node.transitions[mi][0],indent+1,tested,node.transitions[mi][1])
    if mi2 != -1:
        traverse(node.transitions[mi2][0],indent+1,tested,node.transitions[mi2][1])
    #for x in node.transitions:
#        traverse(node.transitions[x][0],indent+1,tested,node.transitions[x][1])

conn = db.getConnection()
r = db.loadDataFromDB(conn,query="id > 100000",orderBy="id",limit=25000)
print('load')
model = ModelBuilder.ModelBuilder([tests,results])
nodes = {}
i = 0
for x in r.rows:
    model.addData(x)
    i += 1
    if i % 250 == 0:
        print(i)

#print("Markov done")
model.calculateProbobilities()
fullRules,partRules = model.buildRules()
print(len(fullRules),len(partRules))
tags = {}
i = 0
for x in r.rows:
    model.getTagsFromFullRules(x,tags)
    i += 1
    if i % 250 == 0:
        print(i)

#print('Full rules')
if len(fullRules) < 30:
    print('Full rules')
    for x in fullRules:
        d = []
        for y in x[2]:
            b = y.getData()
            if b[1] == NEWLINE:
                d.append('NEWLINE')
            elif b[1] == EOF:
                d.append('EOF')
            elif b[1] == SOF:
                d.append('SOF')
            else:
                d.append(b[0])
        print(round(x[0]*x[1],3),d)
if len(partRules) < 30:
    print('Part rules')
    for x in partRules:
        d = []
        for y in x[1]:
            b = y.getData()
            if b[1] == NEWLINE:
                d.append('NEWLINE')
            elif b[1] == EOF:
                d.append('EOF')
            elif b[1] == SOF:
                d.append('SOF')
            else:
                d.append(b[0])
        print(round(x[0],3),d)

testNew = []
for x in tags[tests]:
    if tags[tests][x] > 1000:
        testNew.append(''.join([y[0] for y in x]))
resultsNew = []
for x in tags[results]:
    if tags[results][x] > 1000:
        resultsNew.append(''.join([y[0] for y in x]))

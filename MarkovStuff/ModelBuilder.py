import Tags
import Markov

NEWLINE = 1
WORD = 2
SPACE = 3
TAG = 4
EOF = 5
SOF = 6

CUTOFF = 40
RULECUTOFF = 8
WINDOWSIZE = 2

PRETHRESHOLD = 0.7
POSTTHRESHOLD = 0.7
DUELTAGCHANG = 0.2

#I'm sure this method is very slow, there must be a way
#to compile a regex to do this
#basically just tokenise on alphanumeric/non-alphanumeric boundaries
#ie the string "hello world!" becomes
#('hello',WORD),(' ',SPACE),('world',WORD),('!',SPACE)
#newlines are treated specially
def splitText(text):
    r = []
    t = ''
    state = NEWLINE
    for x in text:
        if x == '\n':
            if t != '':
                r.append((t,state))
                t = ''
            state = NEWLINE
            r.append((None,NEWLINE))
        elif state != WORD and x.isalnum():
            if t != '':
                r.append((t,state))
            t = x
            state = WORD
        elif state != SPACE and not x.isalnum():
            if t != '':
                r.append((t,state))
            t = x
            state = SPACE
        else:
            t += x
    if t != '':
        r.append((t,state))
    return r

#I think there are faster string searches out there
#this was just to prove that this worked but a faster method would speed things up a bit
def boyerMoore(search,text,start=0):
    if start < 0:
        start = 0
    m = len(search)
    n = len(text)
    if m > n: return -1
    skip = Tags.nullableDict(m)
    for k in range(m - 1): skip[search[k]] = m - k - 1
    k = m - 1+start
    while k < n:
        j = m - 1; i = k
        while j >= 0 and text[i] == search[j]:
            j -= 1; i -= 1
        if j == -1: return i + 1
        k += skip[text[k]]
    return -1


class ModelBuilder:
    def __init__(self,tagSets):
        self.model = Markov.MarkovModel()
        self.tagSets = tagSets
        self.fullRules = []
        self.partRules = []
        
    def addData(self,data):
        text = data.mainData
        words = splitText(text)
        tagIndex = []
        for x in self.tagSets:
            for y in x:
                i = boyerMoore(y.value,words)
                
                while i != -1:
                    words = words[:i] + [(x,TAG)] + words[i+len(y.value):]
                    tagIndex = [(k - len(y.value)+1 if k > i else k) for k in tagIndex] 
                    tagIndex.append(i)
                    i = boyerMoore(y.value,words,i)
        if tagIndex == []:
            return
        for i in tagIndex:
            tag = words[i]
            tagSet = tag[0]
            
            w = [words[i-2] if i > 1 else (None,SOF),
                 words[i-1] if i > 0 else (None,SOF),
                 tag]
            node = self.model.getNodeForValue(w[-1])
            preNode = self.model.getNodeForValue(w[0])
            
            for o in range(1,CUTOFF,1):
                node.setPrefix(tuple(w[:-1]))
                preNode.setSufix(tuple(w[1:]))
                w = w[1:]
                if i+o >= len(words):
                    w.append((None,EOF))
                else:
                    w.append(words[i+o])

                if w[-1][1] in (SOF,EOF,TAG):
                    break
                node = self.model.getNodeForValue(w[-1])
                preNode = self.model.getNodeForValue(w[0])

            w = [words[i-3] if i > 2 else (None,SOF),
                 words[i-2] if i > 1 else (None,SOF),
                 words[i-1] if i > 0 else (None,SOF)]
            node = self.model.getNodeForValue(w[-1])
            preNode = self.model.getNodeForValue(w[0])
            
            for o in range(4,CUTOFF+2,1):
                node.setPrefix(tuple(w[:-1]))
                preNode.setSufix(tuple(w[1:]))
                w = w[:-1]
                if i-o < 0:
                    w = [(None,SOF)] + w
                else:
                    w = [words[i-o]] + w

                if w[-1][1] in (SOF,EOF,TAG):
                    break
                node = self.model.getNodeForValue(w[-1])
                preNode = self.model.getNodeForValue(w[0])
    def calculateProbobilities(self):
        self.model.buildTransitionTable()

    def buildRules(self):
        fullRules = []
        partRules = []
        forwardRules = []
        reverseRules = []
        for x in self.tagSets:
            n = self.model.getNodeForValue((x,TAG))
            print(n)
            fr = n.forwardRules(self.model,POSTTHRESHOLD*0.5,1000,RULECUTOFF)
            rr = n.reverseRules(self.model,PRETHRESHOLD*0.5,1000,RULECUTOFF)
            
            temp = []
            for x in fr:
                if len(x[1]) > 1:
                    temp.append(x)
            fr = temp

            temp = []
            for x in rr:
                if len(x[1]) > 1:
                    temp.append(x)
            rr = temp
            
            added = False
            for reverse in rr:
                for forward in fr:
                    if n.shouldMerge(self.model,forward[1],reverse[1],POSTTHRESHOLD*0.5,-1):
                        fullRules.append([forward[0],reverse[0],reverse[1][:-1] + forward[1]])
            for rev in rr:
                if rev[0] > 0.0002 and len(rev[1]) > 1:
                    partRules.append(rev)
                    
            for forward in fr:
                if forward[0] > 0.0002 and len(forward[1]) > 1:
                    partRules.append(forward)

        self.fullRules = fullRules[:]
        self.partRules = partRules[:]
        return fullRules,partRules
    
    def getTagsFromFullRules(self,data,tags):
        text = data.mainData
        words = splitText(text)
        for index,x in enumerate(self.fullRules):
            segments = []
            s = []
            neighbourTags = False
            for y in x[2]:
                d = y.getData()
                if d[1] == TAG:
                    if s == []:
                        neighbourTags = True
                        break
                    segments.append(s)
                    segments.append([d])
                    s = []
                else:
                    s.append(d)
            if s == []:
                if len(segments) < 3:
                    neighbourTags = True
                else:
                    segments = segments[:-1]
            else:
                segments.append(s)
            if neighbourTags:
                continue

            l = len(segments)
            i = boyerMoore(segments[0],words)
            index = 2
            while index < l:
                if i == -1:
                    break
                iPlus = i + len(segments[index-2])
                j = boyerMoore(segments[index],words,iPlus)
                if j != -1 and i != -1 and j > i:
                    tagSet = segments[index-1][0][0]
                    value = tuple(words[iPlus:j])
                    if tagSet not in tags:
                        tags[tagSet] = {}
                    if value not in tags[tagSet]:
                        tags[tagSet][value] = 0
                    tags[tagSet][value] += 1
                i = j
                index += 2
        return tags

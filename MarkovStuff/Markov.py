TAG = 4

class MarkovModel:
    def __init__(self):
        self.nodes = {}
        self.transitions = {}
        self.backTransitions = {}

    def getNodeForValue(self,value):
        if value not in self.nodes:
            self.nodes[value] = MarkovNode()
            self.nodes[value].setData(value)
        return self.nodes[value]

    def buildTransitionTable(self):
        for x in self.nodes:
            self.nodes[x].calculated = False
        for x in self.nodes:
            self.nodes[x].calculate()
            
        for x in self.nodes:
            n = self.nodes[x]
            for y in n.prefixes:
                if y not in self.transitions:
                    self.transitions[y] = {}
                self.transitions[y][x] = n.prefixes[y][0]
            for y in n.sufixes:
                if y not in self.backTransitions:
                    self.backTransitions[y] = {}
                self.backTransitions[y][x] = n.sufixes[y][0]
        for x in self.transitions:
            c = 0
            for y in self.transitions[x]:
                c += self.transitions[x][y]
            if c != 0:
                c = 1.0/c
            for y in self.transitions[x]:
                self.transitions[x][y] = [self.transitions[x][y],c*self.transitions[x][y]]
        for x in self.backTransitions:
            c = 0
            for y in self.backTransitions[x]:
                c += self.backTransitions[x][y]
            if c != 0:
                c = 1.0/c
            for y in self.backTransitions[x]:
                self.backTransitions[x][y] = [self.backTransitions[x][y],c*self.backTransitions[x][y]]
            

class MarkovNode:
    def __init__(self):
        self.text = None
        self.tagSet = None
        self.prefixes = {}
        self.nearPrefix = {}

        self.sufixes = {}
        self.nearSufix = {}
        
        self.calculated = False

    def setData(self,data):
        if data[1] == TAG:
            self.tagSet = data
        else:
            self.text = data

    def getData(self):
        return self.tagSet if self.text == None else self.text

    def isEnd(self):
        return len(self.transitions)==0

    def setPrefix(self,prefix):
        if prefix not in self.prefixes:
            self.prefixes[prefix] = [1,0]
        else:
            self.prefixes[prefix][0] += 1
    def setSufix(self,sufix):
        if sufix not in self.sufixes:
            self.sufixes[sufix] = [1,0]
        else:
            self.sufixes[sufix][0] += 1
    def forwardRules(self,model,cutoff,countThreshold,maxLength,previous=None):
        if maxLength == 0:
            return [[1,[self]]]

        if previous == None:
            m = 0
            for x in self.nearPrefix:
                if m < self.nearPrefix[x][1]:
                    m = self.nearPrefix[x][1]
                    previous = x
        r = []
        v = self.getData()
        k = (previous,v)
        if k not in model.transitions:
            return [[1,[self]]]
        for x in model.transitions[k]:
            t = model.transitions[k][x][1]
            #if t >= cutoff:
            if t >= cutoff or (countThreshold != -1 and model.transitions[k][x][0] > countThreshold):
                sub = model.getNodeForValue(x).forwardRules(model,cutoff/t,countThreshold,maxLength-1,v)
                for y in sub:
                    r.append([y[0]*t,[self]+y[1]])
        if r == []:
            r = [[1,[self]]]
        return r

    def reverseRules(self,model,cutoff,countThreshold,maxLength,nextNode=None):
        if maxLength == 0:
            return [[1,[self]]]

        if nextNode == None:
            m = 0
            for x in self.nearSufix:
                if m < self.nearSufix[x][1]:
                    m = self.nearSufix[x][1]
                    nextNode = x
        r = []
        v = self.getData()
        k = (v,nextNode)
        if k not in model.backTransitions:
            return [[1,[self]]]
        for x in model.backTransitions[k]:
            t = model.backTransitions[k][x][1]
            #if t >= cutoff:
            if t >= cutoff or (countThreshold != -1 and  model.backTransitions[k][x][0] > countThreshold):
                sub = model.getNodeForValue(x).reverseRules(model,cutoff/t,countThreshold,maxLength-1,v)
                for y in sub:
                    r.append([y[0]*t,y[1]+[self]])
        if r == []:
            r = [[1,[self]]]
        return r

    def shouldMerge(self,model,forward,reverse,threshold,countThreshold):
        w = [reverse[-2].getData(),forward[0].getData(),forward[1].getData()]
        k = tuple(w[:-1])
        if k not in model.transitions or w[-1] not in model.transitions[k]:
            #print('key fail',w)
            return False
        if model.transitions[k][w[-1]][1] < threshold and (countThreshold == -1 or model.transitions[k][w[-1]][0] < countThreshold):
            return False
        k = tuple(w[1:])
        if k not in model.backTransitions or w[0] not in model.backTransitions[k]:
            #print('key fail back',w)
            return False
        if model.backTransitions[k][w[0]][1] < threshold and (countThreshold == -1 or model.backTransitions[k][w[0]][0] < countThreshold):
            return False
        return True

    def calculate(self):
        if self.calculated:
            return
        c = 0
        for x in self.prefixes:
            c += self.prefixes[x][0]
            np = x[-1]
            if np not in self.nearPrefix:
                self.nearPrefix[np] = [self.prefixes[x][0],0]
            else:
                self.nearPrefix[np][0] += self.prefixes[x][0]
        if c != 0:
            c = 1.0/c
        for x in self.prefixes:
            self.prefixes[x][1] = self.prefixes[x][0]*c
        for x in self.nearPrefix:
            self.nearPrefix[x][1] = self.nearPrefix[x][0]*c

        for x in self.sufixes:
            c += self.sufixes[x][0]
            np = x[0]
            if np not in self.nearSufix:
                self.nearSufix[np] = [self.sufixes[x][0],0]
            else:
                self.nearSufix[np][0] += self.sufixes[x][0]
        if c != 0:
            c = 1.0/c
        for x in self.sufixes:
            self.sufixes[x][1] = self.sufixes[x][0]*c
        for x in self.nearSufix:
            self.nearSufix[x][1] = self.nearSufix[x][0]*c
        
        self.calculated = True

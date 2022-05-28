class Pushdown:

    def __init__(self,graph,initial,final): #constructor normal
        self.graph = graph
        self.st_in = initial
        self.st_fin = final
        self.stack = ['$']
    
    @classmethod
    def fromFile(cls,filename):  #"constructor" direct din fisier
        f = open(filename,'r')
    
        N = int(f.readline()) #nefolosit
        graph = {} #folosesc un dictionar pentru a nu avea probleme cu starile
        nodes = f.readline().split() #citirea starilor
        
        for node in nodes:
            graph[node]=[]
        
        M = int(f.readline())
        
        for i in range(0,M): #citirea muchiilor
            line = f.readline().split() 
            edge = (line[1],line[2],line[3],line[4])
            graph[line[0]].append(edge) #in lista de adiacenta sunt tupluri de forma (stare,litera,pop,push)
        
        S = f.readline().split()[0] #citirea starii initiale
        
        nrF = int(f.readline()) #nefolosit
        F = [st for st in f.readline().split()] #citirea starilor finale
        
        f.close()

        return cls(graph,S,F)
    
    
    def parseWord(self,cuv):
        while len(self.stack) > 0:
            self.stack.pop(-1)
        self.stack.append('$')
        crt_node = self.st_in
        for i in range(0,len(cuv)):
            lit = cuv[i]
            for edge in self.graph[crt_node]:
                if (lit == edge[1] or edge[1]=='~') and self.stack[-1] == edge[2]:
                    if edge[1]!='~':
                        i+=1
                    self.stack.pop(-1)
                    if(edge[3]!='~'):
                        for sim in edge[3][::-1]:
                            self.stack.append(sim)
                    crt_node = edge[0]
                    break
            else:
                return None
        for edge in self.graph[crt_node]:
            if edge[1]=='~' and self.stack[-1] == edge[2]:
                if edge[1]!='~':
                    i+=1
                self.stack.pop(-1)
                if(edge[3]!='~'):
                    for sim in edge[3][::-1]:
                        self.stack.append(sim)
                crt_node = edge[0]
                break
        return crt_node

    
    def checkByFinal(self,cuv):
        crt_node = self.parseWord(cuv)
        if crt_node is not None and crt_node in self.st_fin:
            return True
        else:
            return False     
    
    
    def checkByEmpty(self,cuv):
        self.parseWord(cuv)
        if len(self.stack) == 0:
            return True
        else:
            return False


myDPDA = Pushdown.fromFile("input.txt")
cuv = 'abbacabba'
print(myDPDA.checkByFinal(cuv))
print(myDPDA.checkByEmpty(cuv))
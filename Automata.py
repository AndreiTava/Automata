class Automaton:

    def __init__(self,graph,initial,final): #constructor normal
        self.graph = graph
        self.st_in = initial
        self.st_fin = final
    
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
            try:
                edge = (line[1],line[2])
            except IndexError:            #modificare Lambda-NFA
                edge = (line[1], '')
            graph[line[0]].append(edge) #in lista de adiacenta sunt tupluri de forma (stare,litera)
        
        S = f.readline().split()[0] #citirea starii initiale
        
        nrF = int(f.readline()) #nefolosit
        F = [st for st in f.readline().split()] #citirea starilor finale
        
        f.close()

        return cls(graph,S,F)

    def checkCuv(self,cuv): #"metoda de baza" ce va fi supraincarcata de DFA si NFA
        return           #complet inutila in python, aici doar pentru estetica


class DFA(Automaton):

    def checkCuv(self, cuv,path=False):
        crt_node = self.st_in
        path_nodes=[]
        for lit in cuv:
            path_nodes.append(crt_node) #determinarea drumului
            for edge in self.graph[crt_node]:
                if lit == edge[1]:
                    crt_node = edge[0]
                    break
            else:
                return False #daca nu se ajunge la break(nu s-a gasit muchie cu litera data)
                            #cuvantul va fi automat invalid
        path_nodes.append(crt_node)
        if crt_node in self.st_fin:
            if path:
                return (True,path_nodes)
            else:
                return True
        else:
            return False
    @classmethod
    def fromNFA(cls, NFA):   #fara comentarii de data asta ca mi-e lene sa le scriu
        st_in = (NFA.st_in,) #si acum stiu ca explic direct la lab
        st_fin = []
        graph={}
        nodes_queue=[st_in]
        while len(nodes_queue)>0:
            edge_dict={}
            crt_node = nodes_queue.pop(0)
            for state in crt_node:
                for edge in NFA.graph[state]:
                    try: 
                        edge_dict[edge[1]].add(edge[0])
                    except KeyError:
                        edge_dict[edge[1]]=set([edge[0]])
            for new_state in edge_dict.values():
                if tuple(new_state) not in graph:
                    nodes_queue.append(tuple(new_state))
            if crt_node not in graph:
                graph[crt_node]=[(tuple(edge_dict[key]),key) for key in edge_dict.keys()]
                for state in crt_node:
                    if state in NFA.st_fin:
                        st_fin.append(crt_node)

        return cls(graph,st_in,st_fin)

    @classmethod
    def minimise(cls, DFA):
        st_in = None
        st_fin=[]
        graph={}
        st_non_fin = [st for st in DFA.graph if st not in DFA.st_fin]
        partition = [st_non_fin,DFA.st_fin]
        alphabet = {}
        for edge_list in DFA.graph.values():
            for edge in edge_list:
                alphabet[edge[1]]=True
        for dist_subset in partition:
            for letter in alphabet:
                for subset in partition:
                    in_states=[]
                    out_states=[]
                    for state in subset:
                        good= False
                        for edge in DFA.graph[state]:
                            if edge[1]==letter:
                                good=True
                                if edge[0] in dist_subset:
                                    in_states.append(state)
                                else:
                                    out_states.append(state)
                        if not good:
                            out_states.append(state)
                    if len(in_states) != 0 and len(out_states) != 0:
                        partition.remove(subset)
                        partition.extend([in_states,out_states])
        for subset in partition:
            subset=tuple(subset)
            if st_in is None and DFA.st_in in subset:
                st_in = subset
            for st in DFA.st_fin:
                if st in subset:
                    st_fin.append(subset)
                    break
            graph[subset]=[]
            for letter in alphabet:
                good = False
                for state in subset:
                    if good:
                        break
                    for edge in DFA.graph[state]:
                        if good:
                            break
                        if edge[1] == letter:
                            for oth_subset in partition:
                                if edge[0] in oth_subset:
                                    good=True
                                    graph[subset].append((tuple(oth_subset),letter))
                                    break
        return cls(graph, st_in, st_fin)                        



class NFA(Automaton):

    def checkCuv(self,cuv,path=False):
        nodes_queue=[self.st_in] #coada pentru bfs(implementata cu lista din python)
                        #scoaterea se face de la poz 0 iar inserarea la capat
                        #ineficient, dar simplu de implementat
        paths=[set() for _ in range(0,len(cuv))]
        nr_lit=-1
        for lit in cuv:
            nr_lit +=1
            add_queue = [] #lista pentru nodurile ce urmeaza inserate in coada
            while len(nodes_queue) > 0: #cat timp coada nu e goala
                crt_node=nodes_queue.pop(0) #daca modific 0 in -1 coada devine stiva si parcurgearea DFS
                for edge in self.graph[crt_node]:
                    if lit == edge[1]:
                        add_queue.append(edge[0])
                        paths[nr_lit].add((edge[0],crt_node)) #construirea drumurilor sub forma de tupluri
            nodes_queue.extend(add_queue) #la coada se alipesc noile noduri
        
        for node in nodes_queue:
            if node in self.st_fin:
                if path:
                    path_nodes=[node]
                    while nr_lit > -1: #reconstruirea unui drum valid
                        for node_pair in paths[nr_lit]:
                            if node_pair[0]==node:
                                nr_lit -=1
                                node=node_pair[1]
                                break
                        path_nodes.append(node)
                    path_nodes=path_nodes[::-1]
                    return (True,path_nodes)
                else:
                    return True
        return False

class LNFA(Automaton):

    def checkCuv(self, cuv, path=False):
        nodes_queue=[self.st_in] #coada pentru bfs(implementata cu lista din python)
                        #scoaterea se face de la poz 0 iar inserarea la capat
                        #ineficient, dar simplu de implementat
        l_inch = {}
        for st in self.graph.keys():  #fix pentru Lambda-cicluri
            l_inch[st]=False
        for lit in cuv:
            add_queue = [] #lista pentru nodurile ce urmeaza inserate in coada
            for st in l_inch.keys():
                l_inch[st]=False
            while len(nodes_queue) > 0: #cat timp coada nu e goala
                crt_node=nodes_queue.pop(0) #daca modific 0 in -1 coada devine stiva si parcurgearea DFS
                for edge in self.graph[crt_node]:
                    if edge[1] == '' and l_inch[edge[0]]==False:      #extindere pentru Lambda-NFA
                        nodes_queue.append(edge[0])
                        l_inch[edge[0]]=True
                    if lit == edge[1]:
                        add_queue.append(edge[0])
            nodes_queue.extend(add_queue) #la coada se alipesc noile noduri
        
        for st in l_inch.keys():
                l_inch[st]=False
        for node in nodes_queue:
            if node in self.st_fin:
                return True
            for edge in self.graph[node]: #extindere pentru Lambda-NFA
                    if edge[1] == '' and l_inch[edge[0]]==False:     
                        nodes_queue.append(edge[0])
                        l_inch[edge[0]]=True
        return False

f = open("output.txt")

# cuv = "100100"

# myNFA = NFA.fromFile("input.txt")
# verdict,path = myNFA.checkCuv(cuv,True)
# print(verdict)
# if verdict:
#     print("Path:")
#     print(*path,sep="\n")
# myDFA = DFA.fromNFA(myNFA)
# verdict,path = myDFA.checkCuv(cuv,True)
# print(verdict)
# if verdict:
#     print("Path:")
#     print(*path,sep="\n")
# minDFA = DFA.minimise(myDFA)
# verdict,path = minDFA.checkCuv(cuv,True)
# print(verdict)
# if verdict:
#     print("Path:")
#     print(*path,sep="\n")

cuv1 = "ababa"
cuv2 = "abca"
alexDFA = DFA.fromFile("input.txt")
print(alexDFA.checkCuv(cuv1,True))
print(alexDFA.checkCuv(cuv2,True))
alexMinDFA = DFA.minimise(alexDFA)
print(alexMinDFA.checkCuv(cuv1,True))
print(alexMinDFA.checkCuv(cuv1,True))
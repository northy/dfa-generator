from regexes import *

def genStateCode(states) :
    statecode = "" if len(states)==1 else "["
    for s in sorted(states) : statecode+="<"+s+">"
    statecode += "" if len(states)==1 else "]"
    return statecode

def writeNDFA(file, automaton, terminals, final) :
    terminalslist = list(terminals)
    terminalslist.sort()

    lines = []
    lines.append(','.join(['State']+terminalslist)+'\n')
    for k,v in automaton.items() :
        if k in final : l = ['*'+k]
        elif k in final and k=='S': l = ['->*'+k]
        elif k=='S' : l = ['->'+k]
        else : l = [k]
        for t in terminalslist :
            if t not in v or len(t)==0 : l.append('-')
            else : l.append('|'.join(v[t]))
        lines.append(','.join(l)+'\n')

    file.writelines(lines)

def writeDFA(file, automaton, terminals, final) :
    terminalslist = list(terminals)
    terminalslist.sort()

    lines = []
    lines.append(','.join(['State']+terminalslist)+'\n')
    for k,v in automaton.items() :
        if k in final and k=='<S>' : l = ['->*'+k]
        elif k in final : l = ['*'+k]
        elif k=='<S>' : l = ['->'+k]
        else : l = [k]
        for t in terminalslist :
            if t not in v or len(t)==0 : l.append('-')
            else :
                l.append(genStateCode(v[t]))
        lines.append(','.join(l)+'\n')

    file.writelines(lines)

def parseNDFA(lines) :
    terminals = set()
    ndfa = {}
    final = set()

    grammarCount = 0
    grammarFound = False

    for line in lines :
        if blank_line.match(line) :
            if (grammarFound) : grammarCount+=1
            grammarFound = False
            continue

        elif (production_match := production.match(line)) :
            #build NDFA for productions

            grammarFound = True

            rule = production_match.group('rule')
            if rule!='S' :
                rule = str(grammarCount)+rule
            if rule not in ndfa : ndfa[rule] = {}
            terminal_matches = terminal.findall(line)
            for t in terminal_matches :
                if t=='?' :
                    final.add(rule)
                    continue
                terminals.add(t)
                if t not in ndfa[rule] : ndfa[rule][t] = set()
                if rule+"end" not in ndfa :
                    ndfa[rule+"end"] = {}
                    final.add(rule+'end')
                ndfa[rule][t].add(rule+'end')
            tnt_terminal_matches = tnt_terminal.findall(line)
            tnt_nonterminal_matches = tnt_nonterminal.findall(line)
            tnt = []
            for i in range(len(tnt_terminal_matches)) :
                t = tnt_terminal_matches[i]
                nt = tnt_nonterminal_matches[i+1]
                if nt!='S' :
                    nt = str(grammarCount)+nt
                tnt.append([t, nt])

                terminals.add(t)
                if t not in ndfa[rule] : ndfa[rule][t] = set()
                ndfa[rule][t].add(nt)
            
            print("Parser found production:\nrule = ", rule, "\nterminal-nonterminals = ", ','.join([''.join(x) for x in tnt]), "\nterminals = ", ','.join(terminal_matches), sep='')

        elif (keyword_match := keyword.match(line)) :
            #build NDFA for keywords
            state = 'S'
            for i in range(len(line)) :
                newstate = line+str(i+1)
                t = line[i]
                terminals.add(t)
                if state not in ndfa : ndfa[state] = {}
                if t not in ndfa[state] : ndfa[state][t] = set()
                ndfa[state][t].add(newstate)
                state = newstate
            ndfa[state]={}
            final.add(state)
            print('Parser found keyword:', line)

        else :
            print("Invalid expression {}, quitting...".format(line))
            exit(1)

    return ndfa, terminals, final

def determinizeNDFA(ndfa,final) :
    terminals = set()
    dfa = {}
    final_new = set()

    q = [set('S')]
    visited = set()

    while len(q)>0 :
        states = q.pop(0)

        statecode = genStateCode(states)

        if statecode in visited :
            continue
        visited.add(statecode)

        isfinal = False

        for s in states :
            if s not in ndfa : continue
            if s in final : isfinal = True

            if statecode not in dfa : dfa[statecode] = {}

            for k,v in ndfa[s].items() :
                if len(v)==0 : continue
                if k not in dfa[statecode] :
                    dfa[statecode][k] = set()
                    terminals.add(k)
                dfa[statecode][k]=dfa[statecode][k].union(v)
        
        if statecode in dfa :
            for _,v in dfa[statecode].items() :
                q.append(v)
        
        if isfinal : final_new.add(statecode)

    return dfa, terminals, final_new

def addErrorStateDFA(fa, terminals, final) :
    final.add('<ErrorState>')
    fa['<ErrorState>'] = {}
    
    for t in terminals :
        for _,v in fa.items() :
            if t not in v :
                v[t] = set(['ErrorState'])
        fa['<ErrorState>'][t]=set(['ErrorState'])
    return fa, final

def removeUnreachableFA(ndfa,connectionsFromInitial) :
    #Remove unreachable states from FA
    print("Removing unreachable states from FA...")
    for k,v in list(ndfa.items()) :
        if k not in connectionsFromInitial :
            print("State",k,"is unreachable, removing...")
            del ndfa[k]
    return ndfa

def removeDeadFA(ndfa,final,dfa) :
    #Remove dead states from FA
    print("\nRemoving dead states from FA...")
    connectionsFromInitial = set()
    for k,v in list(ndfa.items()) :
        notDead = k in final
        connections = set([k])
        queue = [k]
        visited = set()
        i=0
        while i<len(queue) :
            cur = queue[i]
            if cur in visited :
                i+=1
                continue
            visited.add(cur)
            if cur in ndfa :
                for _,v1 in ndfa[cur].items() :
                    if dfa :
                        x = genStateCode(v1)
                        connections.add(x)
                        queue.append(x)
                        if x in final :
                            notDead = True
                    else :
                        for x in v1 :
                            connections.add(x)
                            queue.append(x)
                            if x in final :
                                notDead = True
            else :
                connections.discard(cur)
            i+=1
        if k=='S' or k=='<S>' :
            connectionsFromInitial = connections.copy()
        if not notDead :
            print("State",k,"is dead, removing...")
            connectionsFromInitial.discard(k)
            del ndfa[k]
            for _,v1 in ndfa.items() :
                for _,v2 in v1.items() :
                    v2.discard(k)
    return ndfa, connectionsFromInitial

def minifyFA(fa,final,dfa) :
    fa, connectionsFromInitial = removeDeadFA(fa, final,dfa)
    fa = removeUnreachableFA(fa, connectionsFromInitial)
    return fa

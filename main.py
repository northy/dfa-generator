import argparse, textwrap, os

from extra import *

def readArgs() :
    helpEpilog = ""
    parser = argparse.ArgumentParser(description="LFA 2020/1", add_help=True)
    parser.add_argument("-i","--input",help="input txt file", required=True, type=str, dest="input")
    parser.add_argument("-o","--output",help="output folder", default="output", type=str, dest="output")
    return parser.parse_args()

def main() :
    #parse arguments
    args = readArgs()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    input_file = open(args.input,'r')
    lines = input_file.read().splitlines()
    input_file.close()

    #Parse input file
    ndfa, terminals, final = parseNDFA(lines)

    #Export NDFA as csv
    print("Exporting nondeterministic finite automaton...",end='')
    ndfa_file = open(os.path.join(args.output,'ndfa.csv'),'w+')
    writeNDFA(ndfa_file, ndfa, terminals, final)
    ndfa_file.close()
    print(" Done!")

    #Minify NDFA
    ndfa = minifyFA(ndfa,final,False)

    #Export NDFA-minified as csv
    print("\nExporting nondeterministic finite automaton (minified)...",end='')
    ndfa_file = open(os.path.join(args.output,'ndfa-min.csv'),'w+')
    writeNDFA(ndfa_file, ndfa, terminals, final)
    ndfa_file.close()
    print(" Done!")

    #Determinize NDFA
    dfa, terminals, final = determinizeNDFA(ndfa, final)

    #Export DFA as csv
    print("\nExporting deterministic finite automaton...",end='')
    dfa_file = open(os.path.join(args.output,'dfa.csv'),'w+')
    writeDFA(dfa_file, dfa, terminals, final)
    dfa_file.close()
    print(" Done!")

    #Add error state to DFA
    dfa, final = addErrorStateDFA(dfa, terminals, final)

    #Export DFA-errorstate as csv
    print("\nExporting deterministic finite automaton (with error state)...",end='')
    dfa_file = open(os.path.join(args.output,'dfa-err.csv'),'w+')
    writeDFA(dfa_file, dfa, terminals, final)
    dfa_file.close()
    print(" Done!")

if __name__=="__main__" :
    main()

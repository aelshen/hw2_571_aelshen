'''
#==============================================================================
cky.py
/Users/aelshen/Documents/Dropbox/School/CLMS 2013-2014/Winter 2014/Ling 571-Deep Processing Techniques for NLP/hw2_571_aelshen/src/cky.py
Created on Jan 29, 2014
@author: Ahmad Elshenawy
#==============================================================================
'''

import nltk
import os
import sys
from cnf_convert import CNF
from collections import defaultdict
#==============================================================================
#--------------------------------Constants-------------------------------------
#==============================================================================
DEBUG = True

#==============================================================================
#-----------------------------------Main---------------------------------------
#==============================================================================
def main():
    if len(sys.argv) < 3:
        print("cky.py requires two arguments:"\
               + os.linesep + "\t(1)context free grammar file"\
               + os.linesep + "\t(2)input data file")
        sys.exit()
        
    grammar_file = sys.argv[1]
    sentences = open(sys.argv[2],'r')
    #cfg is converted
    grammar = CNF(grammar_file)
    
    CKY(sentences, grammar)
    
#==============================================================================    
#---------------------------------Functions------------------------------------
#==============================================================================

#Parse given data using the CKY algorithm
def CKY(data, cnf_grammar):
    lines_parsed = 0
    total_parses = 0
    #read each line of the input data
    for line in data:
        lines_parsed += 1
    
        print(os.linesep + "Sentence #" + str(lines_parsed) + ": " + line)
        sentence = line.strip()
        
        #tokenize the current sentence
        sentence = nltk.word_tokenize(sentence)
        
        #the (n+1)x(n+1) table needed for the cky algorithm
        table = [[None for x in xrange(len(sentence) + 1)] for x in xrange(len(sentence) + 1)]
        back_trace = defaultdict(set)
        
        for j in xrange( 1, len(sentence) + 1 ):
            word = "'" + sentence[j - 1] + "'"
            #list of tuples
            labels = []
            #get every preterminal that produces the current word
            for LHS in cnf_grammar.terminal_rules_by_daughter[word]:
                parent = Node(LHS, [word])
                labels.append(parent)
                back_trace[(j-1,j)].add( parent )
            #end LHS in cnf_grammar.terminal_rules_by_daughter[word]:
            table[j-1][j] = labels

            
            for i in range(j-2,-1,-1):
                k = i + 1
                LHS = []
                while k <= j - 1:
                    B = table[i][k][:]
                    C = table[k][j][:]
                    
                    
                    for left_child in B:
                        for right_child in C:
                            if left_child.label in cnf_grammar.nonterminal_rules_by_daughter:
                                RHS = (left_child.label, right_child.label)
                                #if a rule exists that produces this (left,right) pair
                                if RHS in cnf_grammar.nonterminal_rules_by_daughter[left_child.label]: 
                                    for label in cnf_grammar.nonterminal_rules_by_daughter[left_child.label][RHS]:
                                        #create an object to keep track of the parent, 
                                        #and the left and right children that led to it
                                        parent = Node(label, [left_child, right_child])
                                        #save to a list of all possible parents for this j
                                        LHS.append(parent)
                                        #add this parent object to the backtrace, 
                                        #using the start and stop (i.e. (i,j) ) tuple as a key
                                        #to keep track of the length of the span
                                        back_trace[(i,j)].add( parent )
                    k += 1
                #while k <= j - 1:
                table[i][j] = LHS
                
            #for i in range(j-2,-1,-1):
            
            
        #end for j in range( 1,len(sentence) ):
        
        #lines_parsed += 1
        count = 0
        #for any parses in the backtrace that cover the entire span of the sentence
        for trace in back_trace[(0, len(sentence) )]:
            #for any such span that begins with the start symbol of the grammar
            if trace.label == cnf_grammar.start_symbol:
                count += 1
                print("Parse #" + str(count) + ":")
                ParsePrint(trace)
        
        print(str(count) + " Total Parse(s) for Sentence#" + str(lines_parsed) + os.linesep)
    #end for line in data:



#Recursively follows the lineage of a parent object, printing in simple 
#bracketed form until a terminal is produced
def ParsePrint(trace, indent = ""):
    if len(trace.children) == 1:
        print(indent + "(" + trace.label + "\t" + trace.children[0] + ")")
        #ParsePrint(trace.children[0], indent + "   ")
        return
    else:
        print(indent + "(" + trace.label )
        ParsePrint(trace.children[0], indent + "   ")
        #print(indent + ")")
        ParsePrint(trace.children[1], indent + "   ")
        print(indent + ")")
    
    
#==============================================================================    
#----------------------------------Classes-------------------------------------
#==============================================================================
class Node:
    def __init__(self, label, children = []):
        self.label = label
        self.children = children
#==============================================================================    
#------------------------------------------------------------------------------
#==============================================================================
if __name__ == "__main__":
    sys.exit( main() )
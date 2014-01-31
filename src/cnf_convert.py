'''
#==============================================================================
cnf_convert.py
/Users/aelshen/Documents/Dropbox/School/CLMS 2013-2014/Winter 2014/Ling 571-Deep Processing Techniques for NLP/hw2_571_aelshen/src/cnf_convert.py
Created on Jan 28, 2014
@author: Ahmad Elshenawy
#==============================================================================
'''

import os
import sys
from collections import defaultdict
#==============================================================================
#--------------------------------Constants-------------------------------------
#==============================================================================
DEBUG = True

#==============================================================================
#-----------------------------------Main---------------------------------------
#==============================================================================
def main():
    if len(sys.argv) < 2:
        print("CNF_convert.py requires one argument:"\
               + os.linesep + "\t(1)grammar.cfg file")
    
    original_grammar = sys.argv[1]
    x = CNF(original_grammar)
    
    
    print "Hello, World!"
#==============================================================================    
#----------------------------------Classes-------------------------------------
#==============================================================================
class CNF:
    def __init__(self, original_grammar):
        self.start_symbol = None
        (self.cnf_rules,self.terminal_rules_by_daughter,self.nonterminal_rules_by_daughter)\
                                                         = self.ConvertGrammar(original_grammar)

        self.PrintGrammar(original_grammar)
    
    
    #Print out the cnf grammar, only ensuring the start symbol is printed first, 
    #then printing the remaining rules in whatever order they are stored in
    def PrintGrammar(self, original_grammar):
        output_file = open(original_grammar.split('.')[0] + '.cnf','w')
        for RHS in self.cnf_rules[self.start_symbol]:
            output_file.write(self.start_symbol + " -> " + " ".join(RHS) + os.linesep)
        output_file.write(os.linesep)
        for LHS in self.cnf_rules:
            if LHS == self.start_symbol:
                continue
            for RHS in self.cnf_rules[LHS]:
                output_file.write(LHS + "\t->\t" + " ".join(RHS) + os.linesep)
                
            output_file.write(os.linesep)
    
    
    #Convert an imported Context Free Grammar, 
    #and convert it into Chomsky Normal Form
    def ConvertGrammar(self, file):
        cnf_rules = defaultdict(set)
        broken_rules = []

        count = 1
        
        for line in open(file, 'r').readlines():
            if line[0] == "#" or not line.strip():
                continue
              
            LHS,RHS = line.strip().split("->")
            LHS = LHS.strip()
            RHS = RHS.split()
            if self.start_symbol == None:
                self.start_symbol = LHS
            
            #For terminal production rules, the preterminal (LHS) is 
            #mapped to a set of terminals (RHS)
            if len(RHS) == 1 and (RHS[0][0] == "'" and RHS[0][-1] == "'"):
                    cnf_rules[LHS].add( tuple([RHS[0]]) )
            #for nonterminal production rules, the nonterminal parent (LHS) 
            #is mapped to a set of tuples (RHS[i], RHS[i+1]...,RHS[n])
            elif len(RHS) >= 2:
                #this loop is responsible for eliminating any nonterminal rules
                #that have a leaf production (e.g. SQ -> MD NP VP '?' or SBAR -> 'that' S)
                for i in range( len(RHS) ):
                    item = RHS[i]
                    if item[0] == "'" and item[-1] == "'":
                        temp = item.strip("'").upper()
                        RHS[i] = temp
                        cnf_rules[temp].add(tuple([item]))
                #for any rules that have more than two productions, 
                #run through condensing RHS by creating new rules
                #e.g. S -> NP VP PUNC == S -> X1 PUNC, X1 -> NP VP
                if len(RHS) > 2:
                    while len(RHS) > 2:
                        temp = "X"+str(count)
                        count += 1
                        cnf_rules[temp].add( tuple(RHS[0:2]) )
                        RHS.pop(0)
                        RHS.pop(0)
                        RHS.insert(0, temp)
                cnf_rules[LHS].add( tuple(RHS) )
            else:
                #otherwise, we have unary nonterminal rules that need to be fixed
                #e.g. NP -> NOM
                cnf_rules[LHS].add( tuple([RHS[0]]) )
                broken_rules.append( tuple([LHS,RHS]) )
        #end for line in open(file, 'r').readlines():
        
        #run through all broken rules and make them fit with CNF
        while len(broken_rules) > 0:
            #remove first broken rule from the list
            LHS,RHS = broken_rules.pop(0)
            
            #if RHS has two parts, no fixing to be done
            if len(RHS) == 2:
                continue
            
            #if RHS is a terminal production, no fixing to be done
            if len(RHS) == 1 and (RHS[0][0] == "'" and RHS[0][-1] == "'"):
                continue
            
            #if unary and nonterminal
            if len(RHS) == 1 and not (RHS[0][0] == "'" and RHS[0][-1] == "'"):
                #remove the broken rule from saved rules
                cnf_rules[LHS].remove( tuple(RHS) )
                #for every RHS that the nonterminal child produces, 
                #add it as a child of LHS
                #e.g. NOM -> NN, NN -> 'case' ==> NOM -> 'case'
                for leaf in cnf_rules[RHS[0]]:
                    cnf_rules[LHS].add( leaf )
                    #ensures a check to make sure that the resulting rule is acceptable
                    broken_rules.append( tuple([LHS,leaf]) ) 

        #create an inverse dictionary for terminal rules such that 
        #each terminal production maps to a POS tag, 
        #create an inverse dictionary for nonterminal rules such that
        #the left daughter of the rule maps to a dictionary of tuples of 
        #(left daughter, right daughter), which maps to the parent of the rule
        terminal_rules_by_daughter = defaultdict(set)
        nonterminal_rules_by_daughter = defaultdict(lambda: defaultdict(set))
        for LHS in cnf_rules:
            for RHS in cnf_rules[LHS]:
                if len(RHS) == 1:
                    terminal_rules_by_daughter[RHS[0]].add(LHS)
                elif len(RHS) == 2:
                    nonterminal_rules_by_daughter[RHS[0]][RHS].add(LHS)
                    
        
                
                
        return cnf_rules, terminal_rules_by_daughter, nonterminal_rules_by_daughter
        


if __name__ == "__main__":
    sys.exit( main() )
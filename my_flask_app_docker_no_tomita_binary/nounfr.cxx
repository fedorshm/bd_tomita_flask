#encoding "utf-8"    
#GRAMMAR_ROOT S      
NF -> Noun<gnc-agr[1]> Adj<gnc-agr[1]>;
NF -> Adj<gnc-agr[1]> Noun<gnc-agr[1]>;
S -> NF;


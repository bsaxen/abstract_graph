#========================================================================
# File:   opZ2.py 
# Author: Benny Saxen
# Date:   2025-07-14
#========================================================================

import networkx as nx
from pyvis.network import Network
from copy import deepcopy
import random
import sys
from termcolor import colored




def generate_unique_random_pairs(n_pairs, min_val, max_val, filename):
    all_possible_pairs = [
        (a, b) for a in range(min_val, max_val + 1)
                for b in range(min_val, max_val + 1)
    ]
    
    if n_pairs > len(all_possible_pairs):
        raise ValueError("För många par för det givna intervallet – kan inte skapa så många unika.")

    selected_pairs = random.sample(all_possible_pairs, n_pairs)

    with open(filename, "w") as f:
        for a, b in selected_pairs:
            f.write(f"{a} {b}\n")
        f.close()

def read_graph_from_file(filename):
    G = nx.DiGraph()
    with open(filename, 'r') as f:
        for line in f:
            #print(line)
            if '#' not in line:
                u, v = map(int, line.strip().split())
                #print(u)
                #print(v)
                G.add_edge(u, v)
    return G


def operation_X(G: nx.DiGraph) -> nx.DiGraph:
    G = G.copy()
    changed = True
    removed = 0
    removedList = []

    while changed:
        #print("operation X")
        changed = False
        affected_nodes = list(G.nodes)
        #print(affected_nodes)
        #print('----------------------')
        for node in affected_nodes:
            #print('Node='+str(node))
            in_edges = list(G.in_edges(node))
            out_edges = list(G.out_edges(node))
            total_edges = len(in_edges) + len(out_edges)

            if total_edges == 1:
                #print('Node='+str(node))
                if len(out_edges) == 1:
                    #print('Out Killer ? ' + str(node))
                    #print(out_edges)
                    _, B = out_edges[0]
                    #print('B node='+str(B))
                    outgoing_from_B = list(G.out_edges(B))
                    if outgoing_from_B:
                        #print('Yes========== Remove outgoing from B:')
                        #print(outgoing_from_B)
                        G.remove_edges_from(outgoing_from_B)
                        changed = True
                        removed += 1
                        removedList.append(outgoing_from_B)
                        
                elif len(in_edges) == 1:
                    #print('In Killer ? ' + str(node))
                    #print(in_edges)
                    B, _ = in_edges[0]
                    #print('B node='+str(B))
                    incoming_to_B = list(G.in_edges(B))
                    if incoming_to_B:
                        #print('Yes ========= Remove incoming to B:')
                        #print(incoming_to_B)
                        G.remove_edges_from(incoming_to_B)
                        changed = True
                        removed += 1
                        removedList.append(incoming_to_B)
                        

    return G,removed,removedList

#========================================================================
def visualize_pyvis(G, filename="graph.html", title="Interactive Graph"):
    net = Network(directed=True, notebook=False)
    nodeTypeDict = {}
    # Add nodes with color based on edge directionality
    for node in G.nodes():
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)
        
        if in_deg == 0 and out_deg > 0:
            color = 'red'   # Only outgoing edges
            nodeType = 'F'
        elif in_deg > 0 and out_deg == 0:
            color = 'blue'  # Only ingoing edges
            nodeType = 'B'
        elif in_deg == 0 and out_deg == 0:
            color = 'yellow'  # Only ingoing edges
            nodeType = 'S'
        else:
            color = 'green' # Both ingoing and outgoing edges
            nodeType = 'M'

        net.add_node(node, label=str(node), color=color)
        nodeTypeDict[node] = nodeType
    
    # Add edges
    for source, target in G.edges():
        net.add_edge(source, target)

    net.show_buttons(filter_=['physics'])
    net.write_html(filename)
    #print(f"Graph saved to {filename}")
    #print(nodeTypeDict)
    return nodeTypeDict

#========================================================================
# MAIN
#========================================================================
def main(args):

    print(args)
    if len(args)  == 1:
        g = args[0]

        if g == '0':
            graphfile = 'g-random.txt'
            generate_unique_random_pairs(10, 1, 15, 'g-random.txt')
        else:
            graphfile = 'g-'+str(g)+'.txt'
        G_orig = read_graph_from_file(graphfile)
        all_edges = list(G_orig.edges)
        ntDict1 = visualize_pyvis(G_orig, "g-original.html", "Original Graph")
        famDict = {}
        for edge in all_edges:
            nodeA = edge[0]
            nodeB = edge[1]
            tA = ntDict1[nodeA]
            tB = ntDict1[nodeB]
            #print(str(nodeA) + '(A) ' +tA)
            #print(str(nodeB) + '(B) ' +tB)
            #print()
            if tA == 'F':
                if nodeA not in famDict:
                    famDict[nodeA] = []
                famDict[nodeA].append(nodeB)

            if tA == 'F' and tB == 'B':
                print('Member '+str(nodeB) + ' is unused')
            if tA == 'S' or tB == 'S':
                print('Node '+str(nodeB) + ' is single *******')
            if nodeA == nodeB:
                print('Edge '+str(nodeA) + ' is a self-reference *******')


        G_work = deepcopy(G_orig)
        G_mod,removed,rList = operation_X(G_work)
        print(":::::::::: Initial number of removed edges: " + str(removed))
        print(rList)

        all_edges = list(G_work.edges)
        print(all_edges)
        


        #for edge in all_edges:
        counter = 0
        for fam in famDict:
        
            print('------------------------------ family:' + str(fam))
            for mem1 in famDict[fam]:
                tList  = []
                selected = str(fam)+'->'+str(mem1)
                for mem2 in famDict[fam]:
                    if mem1 != mem2:  
                        edge = (fam,mem2)
                        tList.append(edge)

                if len(tList) > 0:
                    counter += 1
                    print(str(counter) + "============== Removed edge =====================")
                    print(tList)
                    print("selected: "+selected)
                    print("=================================================")
                                
                    #edgeList = [(10,1),(10,2)]
                    G_tmp = deepcopy(G_orig)
                    G_tmp.remove_edges_from(tList)

                    G_mod,removed,rList = operation_X(G_tmp)
                    #print(":::::::::: Initial number of removed edges: " + str(removed))
                    iteration = 0
                    while removed > 0:
                        iteration += 1
                        #print("ITERATION: " + str(iteration))
                        G_mod,removed,rList = operation_X(G_mod)
                        #print("Number of removed edges: " + str(removed))
                    name = 'g-no-'+str(counter)+'.html'
                    ntDict2 = visualize_pyvis(G_mod, name, "tmp Operation X")

                    for node in ntDict1:
                        identified = 0
                        t1 = ntDict1[node]
                        t2 = ntDict2[node]
                        #print(str(node) + ' ' +t1 + ' ' + t2)

                        if t1 == 'M' and t2 == 'F': # Member disconnected from family
                            print(colored('(M->F)Member '+str(node) + ' is dead','blue'))
                            identified = 1
                        if t1 == 'M' and t2 == 'B': # Member disconnected from all blockings
                            print(colored('(M->B)Member '+str(node) + ' is selected','green'))
                            identified = 2

                        if t1 == 'M' and t2 == 'S':
                            print(colored('(S) Member '+str(node),'yellow') + ' is single *************')
                            identified = 3

                        if t1 == 'B' and t2 == 'S':
                            print(colored('(S) Block '+str(node),'yellow') + ' is single *************')
                            identified = 3

                        if t1 == 'F' and t2 == 'S': # Empty family
                            print(colored('(F->S)Family '+str(node) + ' is empty','red'))
                            identified = 4

                        if t1 != t2:
                            #print("Node type changed: "+str(t1)+'=>'+str(t2))
                            if identified == 0:
                                print(colored("++++++++++++++++ ERROR",'red')+": unidentified node type transition")
#========================================================================
# MAIN
#========================================================================
if __name__ == "__main__":
    main(sys.argv[1:])
#========================================================================
# END of File
#========================================================================


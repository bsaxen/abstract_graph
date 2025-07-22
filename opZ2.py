#========================================================================
# File:   opZ2.py 
# Author: Benny Saxen
# Date:   2025-07-22
#========================================================================

import networkx as nx
from pyvis.network import Network
from copy import deepcopy
import random
import sys
from termcolor import colored

import os
import html
import glob

def delete_html_files(directory):
    html_files = glob.glob(os.path.join(directory, "*.html"))
    for file in html_files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")


def htmlDir(directory):
    # Kontrollera att det är en giltig katalog
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} är inte en giltig katalog.")

    # Skapa en lista med länkar till filer
    links = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            safe_filename = html.escape(filename)
            # Länk öppnas i ny flik med target="_blank"
            links.append(f'<li><a href="{safe_filename}" target="_blank">{safe_filename}</a></li>')

    # Generera HTML-innehåll
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Filer i {html.escape(directory)}</title>
    </head>
    <body>
        <h1>Filer i {html.escape(directory)}</h1>
        <ul>
            {''.join(links)}
        </ul>
    </body>
    </html>
    """

    # Spara som index.html i katalogen
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML-fil skapad: {index_path}")

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

# Leafs with outgoing edges is prioritzed

    G = G.copy()
    changed = True
    removed = 0
    removedList = []

    #print(G)

    while changed:
        changed = False
        affected_nodes = list(G.nodes)
        #print(affected_nodes)
        for node in affected_nodes:
            #print('Node='+str(node))
            in_edges = list(G.in_edges(node))
            out_edges = list(G.out_edges(node))
            total_edges = len(in_edges) + len(out_edges)
            #print("IN1")
            #print(in_edges)
            #print("OUT1")
            #print(out_edges)
            
            if total_edges == 1:
                #print('Node='+str(node))
                if len(out_edges) == 1:
                    _, X = out_edges[0]
                    outgoing_from_X = list(G.out_edges(X))
                    if outgoing_from_X:
                        #print('Yes========== Remove outgoing:')
                        #print(outgoing_from_X)
                        G.remove_edges_from(outgoing_from_X)
                        changed = True
                        removed += 1
                        removedList.append(outgoing_from_X)

    #print(G)
    changed = True
    while changed:
        changed = False
        affected_nodes = list(G.nodes)
        #print(affected_nodes)
        for node in affected_nodes:
            #print('Node='+str(node))
            in_edges = list(G.in_edges(node))
            out_edges = list(G.out_edges(node))
            total_edges = len(in_edges) + len(out_edges)
            #print("IN2")
            #print(in_edges)
            #print("OUT2")
            #print(out_edges)

            if total_edges == 1:
                #print('Node='+str(node))
                if len(in_edges) == 1:
                    X,_ = in_edges[0]
                    incoming_to_X = list(G.in_edges(X))
                    if incoming_to_X:
                        #print('Yes========== Remove ingoing:')
                        #print(incoming_to_X)
                        G.remove_edges_from(incoming_to_X)
                        changed = True
                        removed += 1
                        removedList.append(incoming_to_X)
                     
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
            color = 'yellow'  # No edges
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

#=======================================================================
def generateBoxView(familie_and_members, member_status, output_file="familjer.html"):
    html_head = """
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <title>Families with members</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }
            .familj {
                border: 2px solid #333;
                padding: 10px;
                margin-bottom: 20px;
                background-color: #fff;
                border-radius: 8px;
            }
            .familj-titel {
                font-weight: bold;
                margin-bottom: 10px;
            }
            .medlems-container {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .medlem {
                padding: 10px;
                border-radius: 4px;
                color: white;
                min-width: 100px;
                text-align: center;
            }
            .aktiv {
                background-color: green;
            }
            .inaktiv {
                background-color: gray;
            }
        </style>
    </head>
    <body>
        <h1>Familjeöversikt</h1>
    """

    html_body = ""

    for familj, medlemmar in familie_and_members.items():
        html_body += f'<div class="familj">\n'
        html_body += f'  <div class="familj-titel">{familj}</div>\n'
        html_body += f'  <div class="medlems-container">\n'

        for medlem in medlemmar:
            status_klass = "aktiv" if member_status.get(medlem, False) else "inaktiv"
            html_body += f'    <div class="medlem {status_klass}">{medlem}</div>\n'

        html_body += f'  </div>\n</div>\n'

    html_end = """
    </body>
    </html>
    """

    full_html = html_head + html_body + html_end

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"HTML-fil genererad: {output_file}")
#=======================================================================
def logHtml(log, output_file="log.html"):

    html_head = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Log</title>
    </head>
    <body>
    """

    html_body =  log


    html_end = """
    </body>
    </html>
    """
    full_html = html_head + html_body + html_end

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"HTML-fil genererad: {output_file}")
#========================================================================
def drawSymmetryMatrix(sDict):
    for key,oList in sDict.items():
        print(key,end='')
        for obj in oList:
            print(obj,end='')
        print(obj)
      
#========================================================================

def dict_to_colored_symmetric_html_matrix(data: dict, filename='matrix.html'):
    # Steg 1: Hämta alla unika noder
    nodes = sorted(set(data.keys()) | {v for values in data.values() for v in values})
    index = {node: i for i, node in enumerate(nodes)}
    size = len(nodes)

    # Steg 2: Skapa och fyll en matris
    matrix = [[0] * size for _ in range(size)]
    for key, neighbors in data.items():
        for neighbor in neighbors:
            i, j = index[key], index[neighbor]
            matrix[i][j] = 1  # Enkelsidig riktning (kan bli asymmetrisk)

    # Steg 3: Skapa HTML med färger
    html = '''
    <html><head><style>
    table, td, th { border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: center; }
    th { background-color: #f2f2f2; }
    .connected { background-color: #c8e6c9; }     /* grönt */
    .diagonal { background-color: #bbdefb; }      /* blått */
    .asymmetric { background-color: #ffcdd2; }    /* rött */
    </style></head><body>
    <h2>Symmetrisk Matris (med färgkodning)</h2>
    <table>
    '''

    # Rubriker
    html += '<tr><th></th>' + ''.join(f'<th>{node}</th>' for node in nodes) + '</tr>'

    # Rader
    for i in range(size):
        html += f'<tr><th>{nodes[i]}</th>'
        for j in range(size):
            value = matrix[i][j]
            cls = ""
            if i == j:
                cls = "diagonal"
            elif value == 1 and matrix[j][i] == 1:
                cls = "connected"
            elif value != matrix[j][i]:
                cls = "asymmetric"
            html += f'<td class="{cls}">{value}</td>'
        html += '</tr>'
    
    html += '</table></body></html>'

    # Steg 4: Spara filen
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Färgad HTML-matris sparad som {filename}")


#========================================================================
# MAIN
#========================================================================
def main(args):

    symmetryDict = {}

    log = ''
    delete_html_files("./")
    if len(args)  == 1:
        g = args[0]
        log +='Mode: '+ str(g)+'<br>'
        # Input graph
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

        s = str(rList)
        log += 'FWL:'+s+'<br>'
        # for edg in rList: 
        #     edg = str(edg)
        #     print(edg)
        #     log += edg
        print(rList)

        #all_edges = list(G_work.edges)
        #print(all_edges)
        objStatusDict = {}
        ntDict2 = visualize_pyvis(G_mod, "g-mod.html", "Modified Graph")
        for node in ntDict1:
            identified = 0
            t1 = ntDict1[node]
            t2 = ntDict2[node]
            #print(str(node) + ' ' +t1 + ' ' + t2)

            objStatusDict[node] = True
            if t1 == 'M' and t2 == 'F': # Member disconnected from family
                print(colored('(M->F)Member '+str(node) + ' is dead','blue'))
                identified = 1
                objStatusDict[node] = False
   
        generateBoxView(famDict, objStatusDict)

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
                    print(str(counter) + "============== WHAT IF =====================")
                    #print(tList)
                    symmetryDict[mem1] = []
                    print("selected A-B edge: "+selected)
                    log += '======== Family '+str(fam) + ' selected:'+selected+'<br>'
                    print("=================================================")
                                
                    #edgeList = [(10,1),(10,2)]
                    G_tmp = deepcopy(G_mod)
                    G_tmp.remove_edges_from(tList)

                    G_work,removed,rList = operation_X(G_tmp)
                    #print(":::::::::: Initial number of removed edges: " + str(removed))
                    iteration = 0
                    while removed > 0:
                        iteration += 1
                        print("ITERATION: " + str(iteration))
                        G_work,removed,rList = operation_X(G_work)
                        print("Number of removed edges: " + str(removed))
                    name = 'g-no-'+str(counter)+'.html'
                    ntDict2 = visualize_pyvis(G_work, name, "tmp Operation X")

                    for node in ntDict1:
                        if node not in famDict[fam]:
                            identified = 0
                            t1 = ntDict1[node]
                            t2 = ntDict2[node]
                            #print(str(node) + ' ' +t1 + ' ' + t2)

                            if t1 == 'M' and t2 == 'F': # Member disconnected from family
                                print(colored('(M->F) Member '+str(node) + ' is dead','blue'))
                                identified = 1
                                log += '(M->F) Member '+str(node) + ' is dead<br>'
                                symmetryDict[mem1].append(node)
                            if t1 == 'M' and t2 == 'B': # Member disconnected from all blockings
                                print(colored('(M->B)Member '+str(node) + ' is selected','green'))
                                identified = 2
                                log += '(M->B) Member '+str(node) + ' is selected<br>'
                            if t1 == 'M' and t2 == 'S':
                                print(colored('(S) Member '+str(node),'yellow') + ' is single *************')
                                identified = 3
                                log += '(S) Member '+str(node) + ' is single<br>'

                            if t1 == 'B' and t2 == 'S':
                                print(colored('(S) Block '+str(node),'yellow') + ' is single *************')
                                identified = 3
                                log += '(S) Block '+str(node) + ' is single<br>'

                            if t1 == 'F' and t2 == 'S': # Empty family
                                print(colored('(F->S) Family '+str(node) + ' is empty','red'))
                                identified = 4
                                log += '(F->S) Family '+str(node) + ' is empty<br>'

                            if t1 != t2:
                                #print("Node type changed: "+str(t1)+'=>'+str(t2))
                                if identified == 0:
                                    log += 'ERROR<br>'
                                    print(colored("++++++++++++++++ ERROR",'red')+": unidentified node type transition")


    dict_to_colored_symmetric_html_matrix(symmetryDict)
    logHtml(log,'log.html')
    htmlDir("./")

    print(symmetryDict)

    #drawSymmetryMatrix(symmetryDict)
   
#========================================================================
# MAIN
#========================================================================
if __name__ == "__main__":
    main(sys.argv[1:])
#========================================================================
# END of File
#========================================================================
import networkx as nx
import numpy as np

def run_louvain(nodes):
    """
    Nodes: lateral distances (list of length n)

    Ignore resolution param of louvain.

    Graph G = (V,E) and for x,y from V, xy is in E iff (|x-y|<40
    and). Note that 60 is a bit less than 3s given 22 readings per
    second.
    """
    
    communities = []
    modularity = 0
    
    n = len(nodes)
    edges = [(i,j) for i in range(n-1) for j in range(i+1, n)]# if abs(bnodes[i]-bnodes[j])<40] # and j-i<60

    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
            
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n-1):
        for j in range(i+1,n):
            d = abs(nodes[i]-nodes[j])
            if d < 40: # weight edge at 1 if nodes within 40cm of each other
                w = 1
            else:
                w = 0
            #else:
                # w = 1
                # w = 1/np.sqrt(d)
                # w = 1/d
                # w = 1-(1/np.sqrt(40-d))
                        
            G.add_edge(i,j, weight=w)
                
    if len(edges) == 0:
        print("Error: graph G has 0 edges. Cannot construct a valid partition.")
        communities = []
        modularity = 0
    else:
        communities = nx.community.louvain_communities(G)
        modularity = nx.community.modularity(G, communities)

    return (communities, modularity)

    
    
def get_partitions(ldata, press_starts, press_lengths):
    """
    Partion the list of lateral distances into parts that contain
    values which are pairwise close.

    For each press, work out before-press "events" and after-press
    "events".
    
    """
    bcomms = []
    bmod = []
    acomms = []
    amod = []

    for pi, ps in enumerate(press_starts):

        default_gap = 100
        bof_gap = ps
        prev_ps_gap = 100
        if pi > 0:
            prev_ps_gap = ps - press_starts[pi-1]
        prev_gap = min(default_gap, bof_gap, prev_ps_gap)

        eof_gap = len(ldata) - ps
        next_ps_gap = 100
        if pi + 1 < len(press_starts):
            next_ps_gap = press_starts[pi+1] - ps
        next_gap = min(default_gap, eof_gap, next_ps_gap)

        
        if press_lengths[pi] > 10: # definitely overtake

            bnodes = [ldata[ps-j][4] for j in range(prev_gap)]
            communities, modularity = run_louvain(bnodes)
            bcomms.append(communities)
            bmod.append(modularity)
            acomms.append([])
            amod.append(-1) # code for "not calculated"

        elif press_lengths[pi] < 9: # definitely oncoming

            anodes = [ldata[ps+j][4] for j in range(next_gap)]
            communities, modularity = run_louvain(anodes)
            bcomms.append([])
            bmod.append(-1) # code for "not calculated"
            acomms.append(communities)
            amod.append(modularity)

        else:
            # still need to append, as indices would get shifted
            bcomms.append([])
            bmod.append(-1)
            acomms.append([])
            amod.append(-1)
            print("ambiguous press length:", press_lengths[pi], flush=True)

    return (bcomms, acomms, bmod, amod)

def dispersion_score(L):
    """
    Input is a list L of N lateral distance values.

    Output is a score (out of N) of pts v = (i, l(i)) such that
    there's a ball B(v, rx, ry) with radiuses rx and ry around v such
    that no other u in L is inside B.
    """

    disp_score = 0
    rx = 5
    ry = 30
    
    for i, li in enumerate(L):
        inside_ball_count = 0
        for j, lj in enumerate(L):
            # only care about distinct pts
            if i != j:
                if abs(i-j) > rx or abs(li - lj) > ry:
                    continue
                else:
                    inside_ball_count += 1
        if inside_ball_count < 4:
            disp_score += 1

    return disp_score

def strip_and_split(part, lat_dists, threshold):
    """
    If the part consists of multiple "events" (has a few horizontal parts with too much time separation)
    then split the part into subparts. However, ignore subparts that are too small (<4 in length). Except if
    it's the first part on the very left of the interval (contains index 0). Then keep that - it might correspond
    to an event that overlaps with the button press.

    INPUT:
    part      - a list representing a part in a partition of vertices (indices corresponding to values in lat_dists
    lat_dists - a list of lateral distances associated with a certain button press
    threshold - number of lines between values in part that warrant a split into subparts

    OUTPUT:
    subparts  - a list of lists, each of which is a subpart of part
    """

    subparts = []
    part.sort() # ensure

    # split part into subparts each separated with >10 lines from another one
    sp = []
    for i in range(len(part)-1):
        sp.append(part[i])
        if i+1 == len(part)-1:
            if part[i+1]-part[i] > threshold:
                subparts.append(sp)
                subparts.append([part[i+1]])
                sp = []
            else:
                sp.append(part[i+1])
                subparts.append(sp)
        else:
            if part[i+1]-part[i] > threshold:
                subparts.append(sp)
                sp = []

    # discard subparts of length 3 or less, unless at the beginning (overlap with press)
    no_tiny_subparts = []
    for sp in subparts:
        if sp[0] == 0:
            no_tiny_subparts.append(sp)
            continue
        if len(sp) > 3:
            no_tiny_subparts.append(sp)

    return no_tiny_subparts

import os

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

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
    edges = [(i,j) for i in range(n-1) for j in range(i+1, n)]

    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
            
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n-1):
        for j in range(i+1,n):
            d = abs(nodes[i]-nodes[j])
            # weigh edge 1 if vertices apart <40cm and 15/22s
            if d < 40 and j-i<15: 
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

def get_ot_events(date_string, ldata, press_starts, bcomm, bmod):
    """
    Given a partition (list of parts) returned by get_partitions()
    return a list of overtaking (OT) events. Cleaned up and final.
    Together with their metadata.
    """

    ot_events = []

    partitions = bcomm # one for each button press (empty if even is OC)
    modularities = bmod

    for j, parts in enumerate(partitions):

        # skip oncoming cases
        if modularities[j] == -1:
            continue

        ps = press_starts[j]
        modularity = modularities[j]
        part_and_size_pairs = [(len(x), x) for x in parts]
        part_and_size_pairs.sort(reverse=True) # sorts pairs by 1st item, i.e. size
        press_gap = sum([s for s, p in part_and_size_pairs]) # length of interval we're looking at for this press
        lat_dists = [ldata[ps-x][4] for x in range(press_gap)]

        disp = dispersion_score(lat_dists)

        # plot the lateral distances in the interval (all blue)
        plt.scatter(range(len(lat_dists)), lat_dists, c='b')

        # ---- process the partition -----
        for s, p in part_and_size_pairs:

            lp = list(p)
            lp.sort() # should already be sorted

            # skip the maxed-out readings
            if min([lat_dists[x] for x in p]) > 450:
                continue

            # skip the readings stuck too low
            if max([lat_dists[x] for x in p]) < 50: 
                continue

            #subparts = mod.strip_and_split(lp, lat_dists, 8)
            #if len(subparts) == 0:
            #    continue
            #lp = subparts[0]
            #s = len(lp)

            # --- max clique method ----
            # Take the largest clique from the candidate part
            # and re-attach the vertices from that part which are
            # adjacent to a large portion of the clique

            G = nx.Graph()
            G.add_nodes_from(lp)
            G.add_edges_from([(lp[x],lp[y]) for x in range(s-1) for y in range(x+1, s) if abs(lat_dists[lp[x]]-lat_dists[lp[y]])<35 and lp[y]-lp[x]<15])
            mc = nx.approximation.max_clique(G)
            additional_vertices = set()
            for v in mc:
                v_ball = [lat_dists[v]-30, lat_dists[v]+30]
                for u in G.nodes:
                    if u in mc:
                        continue
                    # make sure the vertex we include with the clique doesn't have a very small degree
                    if lat_dists[u] > v_ball[0] and lat_dists[u] < v_ball[1] and G.degree(u) > 0.8*len(mc):
                        additional_vertices.add(u)

            ot = list(mc)+list(additional_vertices)

            # if we ended up with a part that's too small, go to the next one
            # unless it starts with index 0, then it could be overlapping with press: keep it
            if ot[0] > 0 and len(ot) < 4:
                continue

            # --- end of max clique ----

            ot_event = [date_string, ps, disp, modularity, len(ot), [lat_dists[x] for x in ot], ot]
            ot_events.append(ot_event)

            # re-color the lat dists in the "event" red
            plt.scatter(ot, [lat_dists[x] for x in ot], c='r')

            break # after getting to the OT event

        plt.ylim([0,700])
        plt.savefig(os.path.join("out", "mod", date_string+"_ld_"+str(press_starts[j])+"_"+"{:.6f}".format(modularity)+"_disp="+str(disp)+"_clique.png"))
        plt.clf()

    return ot_events

def get_partitions(ldata, press_starts, press_lengths):
    """
    Partion the list of lateral distances into parts that contain
    values which are pairwise close.

    For each press, work out a partition of the before/after-press interval
    into parts (communities) based on the relationship of the lateral
    distances (similar/not similar).
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
            print("ambiguous press length:", press_lengths[pi], "starts at:", press_starts[pi], flush=True)

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

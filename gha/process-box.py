import os
import matplotlib.pyplot as plt
import networkx as nx
from src import box, constants, util
from src import modularity as mod

bikeLogs = "samples/BikeLogs"
dflist = util.get_box_files(bikeLogs)
util.ensure_date_in_filenames(dflist)
dflist = util.get_box_files(bikeLogs)

for csv_file in dflist:
    print(csv_file, flush=True)
    csvr = util.read_csv(csv_file)
    ldata = box.make_ldata(csvr)  # CSV data as a list
    # presses
    press_starts, press_lengths = box.get_press_lengths_and_starts(ldata)
    date_string = csv_file.split("/")[-1][:8]

    """
    b_partitions, a_partitions, b_modularities, a_modularities = mod.get_partitions(ldata, press_starts, press_lengths)
    
    for j, b_parts in enumerate(b_partitions):
        
        if b_modularities[j] == -1: # it's an oncoming case
            continue

        ps = press_starts[j]
        pmod = b_modularities[j]
        part_and_size_pairs = [(len(x), x) for x in b_parts]
        part_and_size_pairs.sort(reverse=True) # sorts pairs by 1st item, i.e. size
        press_gap = sum([s for s, p in part_and_size_pairs])
        lat_dists = [ldata[ps-x][4] for x in range(press_gap)]
        dispersion_score = mod.dispersion_score(lat_dists)
                     
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

            # Split part into subparts >8 lines apart
            # Discard tiny subparts
            subparts = mod.strip_and_split(lp, lat_dists, 8)
            if len(subparts) == 0:
                continue
            lp = subparts[0]
            s = len(lp)
            
                
            # --- max clique method ----
            G = nx.Graph()
            G.add_nodes_from(lp)

            G.add_edges_from([(lp[x],lp[y]) for x in range(s-1) for y in range(x+1, s) if abs(lat_dists[lp[x]]-lat_dists[lp[y]])<40])
            mc = nx.approximation.max_clique(G)
            additional_vertices = set()
            for v in mc:
                v_ball = [lat_dists[v]-30, lat_dists[v]+30]
                for u in G.nodes:
                    if u in mc:
                        continue
                    # make sure the vertex we include with the clique doesn't have a very small degree
                    if lat_dists[u] > v_ball[0] and lat_dists[u] < v_ball[1] and G.degree(u) > 0.7*len(mc):
                        additional_vertices.add(u)
                
            ot = list(mc)+list(additional_vertices)
            ot_event = [date_string, ps, dispersion_score, pmod, len(ot), ot]
            ot_events.append(ot_event)
            
            plt.scatter(ot, [lat_dists[x] for x in ot], c='r')
            
            # --- end of max clique ----

            break # after getting to the OT event
            
        plt.ylim([0,700])
        plt.savefig(os.path.join("out", "mod", date_string+"_ld_"+str(press_starts[j])+"_"+"{:.6f}".format(pmod)+"_disp="+str(dispersion_score)+"_clique.png"))
        plt.clf()

util.write_to_csv_file(os.path.join("data", "ot_events.csv"), ot_events)

        """

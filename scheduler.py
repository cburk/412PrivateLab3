# As per john's post in Implementing a priority function:

sketch:

get_all_w_no_successors()


# I'm like 90% sure purpose of rank is to order priority queue
# readiness still = (FORALL preds p : S(p) + edge(p, this) < curRep)
bfs on no_succs:
    at each level, for each predecessor:
        if this_level_rank + edge_weight > predecessor_rank:
            pred_rank = t_l_r + e_w

# Still need some weirdness to account for double op tho?

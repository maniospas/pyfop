import pygrank as pg
import pyfop as pfp


@pfp.lazy
@pfp.autoaspects
def pagerank(alpha=0.85):
    print(alpha)
    return pg.PageRank(alpha=alpha)


_, graph, community = next(pg.load_datasets_one_community(["EUCore"]))
personalization = {node: 1. for node in community}
alg = pagerank()
outcome = alg.rank(graph, personalization)
print(outcome)
print(outcome(alpha=0.85))
print(outcome(alpha=0.95))

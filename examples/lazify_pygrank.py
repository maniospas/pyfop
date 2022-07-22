import pygrank as pg
import pyfop as pfp


@pfp.lazy
@pfp.autoaspects
def pagerank(alpha=0.85, preprocessor=None, tol=1.E-6):
    return pg.PageRank(alpha=alpha, preprocessor=preprocessor, tol=tol)


@pfp.lazy
@pfp.autoaspects
def heatkernel(t=3, preprocessor=None, tol=1.E-6):
    return pg.HeatKernel(t=t, preprocessor=preprocessor, tol=tol)


_, graph, community = next(pg.load_datasets_one_community(["citeseer"]))
personalization = {node: 1. for node in community}

ppr = pagerank().rank(graph, personalization)
pr = pagerank().rank(graph, None)
outcome = ppr.np() / pr.np()

preprocessor = pg.preprocessor(assume_immutability=True)
preprocessor(graph)


print(outcome(alpha=0.85, preprocessor=preprocessor))

#print([v for k,v in outcome(alpha=0.85).items()])
#print([v for k,v in outcome(alpha=0.95).items()])

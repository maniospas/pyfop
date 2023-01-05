from lib import *
from interface import Similarity
import numpy as np

x = np.array([1., 1., 1.])
y = np.array([1., 0., 1.])
print(Similarity(normalize, KLdivergence, norm=1, epsilon=Aspect())(x, y))
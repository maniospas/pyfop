import numpy as np


def tautology(x):
    return x


def normalize(x, norm=2):
    return x / (np.sum(x**norm))**(1./norm)


def dot(x, y):
    return np.sum(x*y)


def KL(x, y, epsilon=np.finfo(float).eps):
    return np.sum(x*np.log(x/(y+epsilon)+epsilon))

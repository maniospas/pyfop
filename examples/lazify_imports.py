import numpy as np
import pyfop as pfp

x = np.array([[1., 1., 1.], [2., 2., 2.]])
y = np.array([[1., 1., 1.], [2., 2., 2.]])

with pfp.Lazifier() as lazifier:
    lazifier.lazify(np.sum)
    lazifier.lazify(np.mean)
    r1 = np.sum(x, axis=pfp.Aspect())
    r2 = np.mean(y, axis=pfp.Aspect())
print((r1+r2).call(axis=0))

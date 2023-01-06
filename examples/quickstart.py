import pyfop as pfp


@pfp.lazy_no_cache
@pfp.autoaspects
def affine(x, scale=1, offset=0):
    print(offset)
    return x*scale + offset


@pfp.lazy_no_cache
def logpp(x, offset=pfp.Aspect(1, pfp.Priority.INCREASED)):
    import math
    return math.log(x+offset)/math.log(2)


@pfp.lazy_no_cache
def gm(x, y, affine=affine, logpp=logpp):
    return (affine(x)*logpp(y))**0.5

GM = gm(2, 8)
print(GM.get_input_context(scale=3))
#print(GM(scale=3))  # 12

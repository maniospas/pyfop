from pyfop import lazy, autoaspects


@lazy
@autoaspects
def offset(x, bias=0):
    return x + bias


y1 = offset(-1)
y2 = offset(2)
GM = (y1*y2)**0.5

print(GM(bias=1))   # 0
print(GM(bias=2))   # 2

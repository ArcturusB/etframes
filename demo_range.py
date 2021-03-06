import etframes
from pylab import *


ys = [1.4,1.5,2,2.5,4.8]
xs = range(len(ys))


scatter(xs,ys)

def minmax(data):
    return min(data), max(data)

etframes.add_range_frame(gca(),
                         xbounds=minmax(xs),
                         ybounds=minmax(ys),
                         show_ybounds=(False, True))

show()





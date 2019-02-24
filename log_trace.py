import matplotlib.pyplot as plt
from sortedcontainers import SortedDict
import sys
import numpy as np
from itertools import islice
import struct

def closest(sorted_dict, key):
    "Return closest key in `sorted_dict` to given `key`."
    assert len(sorted_dict) > 0
    keys = list(islice(sorted_dict.irange(minimum=key), 1))
    keys.extend(islice(sorted_dict.irange(maximum=key, reverse=True), 1))
    return min(keys, key=lambda k: abs(key - k))


def neigh( dic, center):
    found = False;
    prev = None
    next = None

    for i in dic:
        if found:
		next  = i
		return prev,next
	if i==center:
		#found
		found = True	
	else:			
		prev = i;
    return None, None	

if len(sys.argv) < 2:
    print "filename missing"
    sys.exit()

filename = sys.argv[1]
print filename

f = open(filename, "r")

cnt = 0
v = 0
i = 0
checksum = 0
cnt = 0
waitingHeader = True
pack = [0,0,0]
data = []
while True:
    try:
        b = ord( f.read(1) )
    except:
        break #acabou
    if (waitingHeader):
        if (b == 10):
            #valido
            v = 0
            i = 0
            checksum = 0
            waitingHeader = False
            cnt = 0
        if (b == 12):
            print "HEADER LOGIC"

    else:
        if (cnt == 0): 
            v = b
            checksum = checksum + b
        if (cnt == 1): 
            v = (v << 8) + b
            checksum = checksum + b
        if (cnt == 2): 
            i = b
            checksum = checksum + b
        if (cnt == 3): 
            i = (i << 8) + b
            checksum = checksum + b
        if (cnt == 4) : 
            #checksum
            waitingHeader = True
            v = v * 0.0008018066406 * 1000 #em mV
            i = i * 0.000005756948401 *1000    #em mA
            checksum = checksum & 255
            if (checksum == b):
                pack = [v,i]
                data.append( pack )
            pack = [v,i]
            data.append(pack)
        cnt = cnt + 1


p = []
i = []
v = []
for  cnt in range( 0, len(data) ):
    p.append( data[cnt][0] * data[cnt][1] / 1000 )
    v.append( data[cnt][0] ) 	
    i.append( data[cnt][1] )
t = []
tcnt = 0

for cnt in range (0, len(p)):
    t.append(tcnt)
    tcnt = tcnt + 0.0002 


fig, ax1 = plt.subplots()
ax1.grid(True)
ax1.plot(t, p, 'r-')
ax1.set_xlabel('Time (s)')
#ax1.tick_params('y', colors='b')
ax1.set_ylabel("Power (mW)")
#ax1.plot(il, vl_calc, 'b-')
fig.show()

fig, ax2 = plt.subplots()
ax2.grid(True)
ax2.plot(t, v, 'bx')
ax2.set_xlabel('Time(s)')
ax2.tick_params('y', colors='b')
ax2.set_ylabel("Current (mA")
ax2.plot(t, i, 'rx')
fig.show()
plt.show()

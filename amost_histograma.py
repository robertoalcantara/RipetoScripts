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
			#v = v * 0.0008018066406 * 1000 #em mV
			#i = i * 0.000005756948401  *1000 #em mA
			checksum = checksum & 255

			if (checksum == b):
				pack = [v,i]
				data.append( pack )
			pack = [v,i]
			data.append(pack)
		cnt = cnt + 1

#data2 = SortedDict()

'''
for x in data:
    v = x[0]
    i = x[1]
    if data2.get(i)==None:
        data2[i] = v
    else:
        data2[i] = (data2.get(i) + v) /2	

data = []
for i, v in data2.items():
	data.append( [v, i] )

vl = []
il = []
pl = []
for i in data:
    if i[0] < 0: continue
    il.append( i[1] )
    vl.append( i[0] )
    pl.append( i[1] * i[0] / 1000 )
    print (str(i[1]) + "," + str(i[0]))  #CSV OUTPUT Curve
'''

v = []
i = []
for d in data:
    if d[0]!=0:
        v.append(d[0])
    if d[1]!=0:
        i.append(d[1])
p = []
for d in data:
    p.append( (d[0] * d[1]) /1000 )
print len(data)
#bins_s = len(data)/1000



fig2,bx1 = plt.subplots()
bx1.grid(True)
bx1.plot(p, 'r-')
bx1.set_xlabel('Num Amostra')
#bx1.tick_params('y', colors='g')
#bx1.set_ylabel("ADC Code @ 83,28uA")
#bx1.set_ylabel("Codigo ADC @ 83,28 uA")
fig2.show()
plt.show()

'''
fig2,bx1 = plt.subplots()
bx1.grid(True)
bx1.plot(i, 'rx')
bx1.set_xlabel('Amostras')
#bx1.tick_params('y', colors='g')
#bx1.set_ylabel("ADC Code @ 83,28uA")
bx1.set_ylabel("Codigo ADC @ 83,28 uA")
#fig2.show()


fig2,bx1 = plt.subplots()
bx1.grid(True)
bx1.plot(v, 'bx')
bx1.set_xlabel('Amostras')
#bx1.tick_params('y', colors='g')
#bx1.set_ylabel("ADC Code @ 83,28uA")
bx1.set_ylabel("Codigo ADC @ 2501,24 mV")
#fig2.show()

plt.show()
'''

'''

#%matplotlib inline
binwidth=1

print min(i)
print max(i)
plt.hist(i, alpha=0.75, color='r', normed=True, bins=range(min(i)-3, max(i)+3 + binwidth, binwidth))
plt.ylabel('Probabilidade');
plt.xlabel('Codigo ADC @ 83,28 uA')
plt.grid(True)
plt.show()


print min(v)
print max(v)
plt.hist(v, alpha=0.75,  color='b',  normed=True, bins=range(min(v)-5, max(v)+5 + binwidth, binwidth))
plt.grid(True)
plt.ylabel('Probabilidade');
plt.xlabel('Codigo ADC @ 2501,24 mV')
plt.show()

'''













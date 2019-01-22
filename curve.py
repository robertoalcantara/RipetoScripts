import matplotlib.pyplot as plt
from sortedcontainers import SortedDict
import sys
import numpy as np
from itertools import islice

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


f = open("capture.bin", "r")

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
			v = v * 0.0008018066406 * 1000 #em mV
			i = i * 0.000005756948401  *1000 #em mA
			checksum = checksum & 255

			if (checksum == b):
				pack = [v,i]
				data.append( pack )
			pack = [v,i]
			data.append(pack)
		cnt = cnt + 1

data2 = SortedDict()

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
    # print (str(i[1]) + "," + str(i[0]))  #CSV OUTPUT Curve

coef = np.polyfit(il,vl,6)

vl_calc = np.polyval(coef,il)
pl_calc = np.array(il) * np.array(vl_calc) /1000

### curva calculada:
MAX_VOUT = 4998.9 #mV  DAC MAX 
MIN_VOUT = 0
VDAC_SIZE = 4096
VLSB_SIZE = MAX_VOUT / VDAC_SIZE


MAX_IOUT = 20 #mA
MIN_IOUT = 0
ILSB_SIZE = 0.00575694840124388 #mA

i_calc = np.arange(MIN_IOUT, MAX_IOUT, ILSB_SIZE)
v_calc = np.polyval(coef,i_calc)
aux = []
for x in v_calc: #cleanup
    if x<0:
        aux.append(0)
    else:
        aux.append(x)
v_calc = aux
p_calc = np.array(i_calc) * np.array(v_calc) /1000


i_ad = []
for i in i_calc:
    i_ad.append( int(i / ILSB_SIZE) ) 
v_ad = []
for v in v_calc:
    v_ad.append( int(v / VLSB_SIZE) )



'''
fig, ax1 = plt.subplots()
ax1.set_xlabel('Voltage (mV)')
ax1.plot(vl,il, 'bx')
ax1.tick_params('y', colors='b')
ax1.set_ylabel("Current (mA)")
ax1.grid(True)

ax2 = ax1.twinx()
ax2.tick_params('y', colors='r')
ax2.plot(vl,pl, 'r.')  
ax2.set_ylabel('Power (mW)' )
ax2.grid(False)

plt.show()
'''

fig, ax1 = plt.subplots()
ax1.grid(True)
ax1.plot(il,vl, 'bx')
ax1.set_xlabel('Current (mA)')
ax1.tick_params('y', colors='b')
ax1.set_ylabel("Voltage (mV)")
ax1.plot(il, vl_calc, 'b-')
ax2 = ax1.twinx()
ax2.tick_params('y', colors='r')
ax2.plot(il,pl, 'rx')
ax2.set_ylabel('Power (mW)' )
ax2.grid(False)
ax2.plot(il,pl_calc, 'r-')
fig.show()



fig2,bx1 = plt.subplots()
bx1.grid(True)
bx1.plot(i_calc, v_calc, 'g-')
bx1.set_xlabel('Current (mA) Calc')
bx1.tick_params('y', colors='g')
bx1.set_ylabel("Voltage (mV) Calc'")
bx2 = bx1.twinx()
bx2.tick_params('y', colors='r')
bx2.plot(i_calc,p_calc,'r-')
bx2.set_ylabel("Power (mW)")
bx2.grid(False)
fig2.show()


fig3,cx1 = plt.subplots()
cx1.grid(True)
cx1.plot(i_ad, v_ad, 'bx')
cx1.set_xlabel('Current Code')
cx1.tick_params('y', colors='b')
cx1.set_ylabel("Voltage Code'")
fig3.show()



plt.show()

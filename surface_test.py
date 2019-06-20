import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib import colors as mcolors

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
            v = v * 0.0008018066406 * 1000 #em mV
            i = i * 0.000005756948401 *1000    #em mA
            checksum = checksum & 255
            if (checksum == b):
                pack = [v,i]
                data.append( pack )
            pack = [v,i]
            data.append(pack)
        cnt = cnt + 1

print "LLL" + str(len(data))
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

coef = np.polyfit(il,vl,6) #6

vl_calc = np.polyval(coef,il)
pl_calc = np.array(il) * np.array(vl_calc) /1000

#calcular o erro
#print "--------------------"
#err_v = np.array(vl) - np.array(vl_calc)
#err_v[0] = 0 #amostra 0 eh especial pq representa a saida a vazio
#print "Erro medio: " + str ( err_v.mean() ) + "mV"
#print "Desvio padrao erro: " + str ( err_v.std() ) + "mV"
#print "-------------------"

### curva calculada:
MAX_VOUT = 4998.9 #mV  DAC MAX 
MIN_VOUT = 0
VDAC_SIZE = 4096
VLSB_SIZE = MAX_VOUT / VDAC_SIZE

RSENSE = 1.05 #OHM

MAX_IOUT = 20 #mA
MIN_IOUT = 0
ILSB_SIZE = 0.00575694840124388 #mA

LEN_SURFACE = 50

i_calc = np.arange(0, 4094, 1) #aqui eh 1 !!!
i_calc = np.array(i_calc) * ILSB_SIZE

time_shift = []

for a in range(0, LEN_SURFACE):
        
        coef = np.polyfit(il,vl,6) #6
        v_calc = np.polyval(coef, i_calc )
        aux = []
        cnt = 0
        for x in v_calc: #cleanup
            if x<0:
                aux.append(0)
            else: #adiciona offset do shunt
                v_ad = x + ( RSENSE * i_calc[cnt] ) #- (a*20)
                aux.append(v_ad)
            
            cnt = cnt + 1
        v_calc = aux
        p_calc = np.array(i_calc) * np.array(v_calc) /1000
        l = []
        d = dict() 
        for k in range(0,len(i_calc)):
            d[i_calc[k]] = v_calc[k]
        time_shift.append( d )

for a in range(0, len(i_calc)):
    print str(i_calc[a]) + "," +  str( v_calc[a])
     
'''
    ##teste fixo v_ad.append( 4095 )
#ivcurve = SortedDict()
#criar o arquivo do dump
fiv = open("ivcurve.bin", 'wb')

#verificar - 
for c in xrange(0, len(i_ad) ):
    #ivcurve[i_ad[c]] =  v_ad[v]
    #print(str(i_ad[c]) + "," + str(v_ad[c])) 
    i0, i1, dummy1, dummy = struct.pack("i", i_ad[c]) 
    v0, v1, dummy2, dummy = struct.pack("i", v_ad[c])
    fiv.write('\x0F')
    fiv.write(i1)
    fiv.write(i0)
    fiv.write(v1)
    fiv.write(v0)
    checksum = ord(i0) + ord(i1) + ord(v0) + ord(v1)
    fiv.write( struct.pack("i", checksum)[0] )
    #print "mem["+ str(i_ad[c]) + "] = " + str(v_ad[c])    

fiv.close()
'''
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
'''

'''
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
'''

'''
fig3,cx1 = plt.subplots()
cx1.grid(True)
cx1.plot(i_ad, v_ad, 'bx')
cx1.set_xlabel('Current Code')
cx1.tick_params('y', colors='b')
cx1.set_ylabel("Voltage Code'")
fig3.show()
'''

'''
fig4,dx1 = plt.subplots()
dx1.grid(True)
dx1.plot(i_calc, v_calc, 'g-')
dx1.set_xlabel('Current (mA) Calc')
dx1.tick_params('y', colors='g')
dx1.set_ylabel("Voltage (mV) Calc'")
fig4.show()

plt.show()
'''

#y vai ser a corrente
#z vai ser a tensao
#x vai ser o tempo

yg = []
zg = []
xg = []
#x_cnt = 0
#for i in time_shift:
#    yg.append( di[0] )
#    zg.append( i[1] )
#    xg.append(x_cnt)
#    x_cnt = x_cnt + 1
'''
def f(x, y):
    r = []
    indice_tempo = X[0]
    for i in range(0, LEN_SURFACE): #indice_tempo:
        r.append( time_shift[i].values() )
    return r 


y = range(0, LEN_SURFACE) #np.linspace(0, LEN_SURFACE, LEN_SURFACE) #T
x = i_calc #np.linspace(0, 1000, 250) #I

X, Y = np.meshgrid(x, y)
Z = f(X, Y)

fig = plt.figure()
ax = plt.axes(projection='3d')
#ax.contour3D(X, Y, Z, 50, cmap='binary')
ax.scatter3D(X, Y, Z, c=Z, cmap='Greens');
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z');

plt.show()
'''

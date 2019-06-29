import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

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
l = 0
checksum = 0
cnt = 0
waitingHeader = True
pack = [0,0,0]
data = []
LOGIC_SCALE = 50
data_trace = []
data_trace1 = []
data_trace2 = []
data_trace3 = []
data_logic = False

x = 0

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
            data_logic = False
            cnt = 0
        if (b == 12):
            #valido
            #print "LOGIC"
            data_logic = True
            waitingHeader = False
            #l = 0
            cnt = 0
            checksum = 0

    else:
        if data_logic == False: 
            if (cnt == 0): 
                v = b
                checksum = b
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
                i =  i * 0.00000092832880672904 *1000    #em mA
                #i = i * 0.000005756948401 *1000    #em mA
                checksum = checksum & 255
                #if (checksum == b):
                #    pack = [v,i]
                #    data.append( pack )

                pack = [v,i]
                data.append(pack)
                try:
                    data_trace.append( data_trace[len(data_trace)-1] ) #mantem o estado anterior do analizador
                    data_trace1.append( data_trace1[len(data_trace1)-1] )
                except:
                    data_trace.append(0)
                    data_trace1.append(0)
            cnt = cnt + 1
        else:
            #logic pack
            if (cnt==0):
                l = b
                checksum = b
            if (cnt==1):
                l = (l<<8) + b
                checksum = checksum + b
            if (cnt==2):
                l = (l<<8) + b
            if (cnt==3):
                pass #do nothing
            if (cnt==4):
                waitingHeader = True
                #checksum = checksum&255
                #if checksum ==
                #if l != 0 : 
                #    l=50
                #print l
                if l & 256:#
                    data_trace.append(LOGIC_SCALE)
                else:
                    data_trace.append(0)

                if l & 512: #bit
                    data_trace1.append(LOGIC_SCALE)
                else:
                    data_trace1.append(0)

                data.append(pack) #manter o estado anterior
            cnt = cnt + 1


print "Numero amostras: " + str(len(data))
data2 = SortedDict()


curve_idx = -1
aux = not data_trace1[0]
cnt_byte = 0
curves = []
for t in data_trace1:
    evento = False
    if t!=aux:
        evento = True
        aux = t
        curve_idx = curve_idx + 1
        cnt_byte_curve = 0;
        curves.append([])
        print "Curva " + str(curve_idx)
    
    curves[curve_idx].append( data[cnt_byte] )
  
    cnt_byte = cnt_byte+1   
    cnt_byte_curve = cnt_byte_curve+1       


#data2 = SortedDict()

#conta_ocorrencia = SortedDict()
#for x in curves[1005]:
#    v = x[0]
#    i = x[1]
#    if data2.get(i)==None:
#        data2[i] = v
    #    conta_ocorrencia[i] = 1
    #else:
    #    data2[i] = (data2.get(i) + v) /2
    #    conta_ocorrencia[i] = conta_ocorrencia[i] + 1;

CURVA = 3660

data = []
for k in curves:
    for x in k:
      v = x[0]
      i = x[1]
      data.append( [v,i] )

'''conta_ocorrencia = SortedDict()
for x in data:
    v = x[0]
    i = x[1]
    if data2.get(i)==None:
        data2[i] = v
        conta_ocorrencia[i] = 1
    else:
        data2[i] = v
        #data2[i] = (data2.get(i) + v) /2
        conta_ocorrencia[i] = conta_ocorrencia[i] + 1;    
'''
#data = []
#for i, v in data2.items():
#    if conta_ocorrencia[i] > 1: # 2 filtro para ruidos da amostragem
#        data.append( [v, i] )



print len(data)


vl = []
il = []
pl = []
for i in data: # curves[600]:
    if i[0] < 0: continue
    il.append( i[1] )
    vl.append( i[0] )
    pl.append( i[1] * i[0] / 1000 )
    # print (str(i[1]) + "," + str(i[0]))  #CSV OUTPUT Curve

print len(vl)

coef = np.polyfit(il,vl,4) #6

vl_calc = np.polyval(coef,il)
pl_calc = np.array(il) * np.array(vl_calc) /1000

#calcular o erro
print "--------------------"
err_v = np.array(vl) - np.array(vl_calc)
#nao necessario err_v[0] = 0 #amostra 0 eh especial pq representa a saida a vazio
print "V Erro medio: " + str ( err_v.mean() ) + "mV"
print "V Desvio padrao erro: " + str ( err_v.std() ) + "mV"
print "-------------------"

### curva calculada:
MAX_VOUT = 5004.5 #mV  DAC MAX
MIN_VOUT = 0
VDAC_SIZE = 4096
VLSB_SIZE = MAX_VOUT / VDAC_SIZE

RSENSE = 1.045 #OHM

MAX_IOUT = 20 #mA
MIN_IOUT = 0
#ILSB_SIZE = 0.00575337029108412  #mA
ILSB_SIZE = 0.00000092832880672904 *1000    #em mA

i_calc = np.arange(0, 4094, 1)
i_calc = np.array(i_calc) * ILSB_SIZE
v_calc = np.polyval(coef, i_calc )
aux = []
cnt = 0
for x in v_calc: #cleanup
    if x<0:
        aux.append(0)
    else: #adiciona offset do shunt - dobrado porque ele existe na captura e vai existir na reproducao
        v_ad = x + ( RSENSE * i_calc[cnt] * 2)
        v_ad = v_ad + 200 # offset ajuste
        aux.append(v_ad)
    cnt = cnt + 1


v_calc = aux
p_calc = np.array(i_calc) * np.array(v_calc) /1000
#calcula o codigo
i_ad = []
for i in i_calc:
    i_ad.append( int(i / ILSB_SIZE) )
v_ad = []

for v in v_calc:
    v_ad.append( int(v / VLSB_SIZE) )



#Ajuste da escala de tempo
time = []
tcnt = 0
for cnt in range (0, len(data)):
    time.append(tcnt)
    tcnt = tcnt + 0.00001976 #50.61 kHz





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
#ax2.plot(il,pl, 'rx')
ax2.set_ylabel('Power (mW)' )
ax2.grid(False)
ax2.plot(il,pl_calc, 'r-')
fig.show()


fig2,bx1 = plt.subplots()
bx1.grid(True)
bx1.plot(i_calc, v_calc, 'b-')
bx1.set_xlabel('Current (mA)')
bx1.tick_params('y', colors='b')
bx1.set_ylabel("Voltage (mV)")
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
'''
v = []
i = []
time = []
tcnt = 0
for x in data:
    v.append(x[0])
    i.append(x[1])

    time.append(tcnt)
    tcnt = tcnt + 0.00001976 #50.61 kHz
    if len(v)>100000:
        break


print len(time)
print len(v)
print len(i)

#i = np.array(i)
#v = np.array(v)
 
## Plot the surface.
#fig = plt.figure()
#ax=fig.gca(projection='3d')
# Make data.
#X = np.arange(0, time[ len(time)-1 ], 0.1)
#Y = np.arange(0, 2000, 0.1)
#X, Y = np.meshgrid(X, Y, sparse=True)
#R = np.sqrt(X**2 + Y**2)
#Z = np.sin(R)
#Z = i

#surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,  linewidth=1, antialiased=False)

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.scatter(time,i,v, marker="x")

#plt.xlim(0,3)
#plt.ylim(0,0.3)

# Customize the z axis.
#ax.set_zlim(-1.01, 1.01)
#ax.zaxis.set_major_locator(LinearLocator(10))
#ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
#fig.colorbar(surf, shrink=0.5, aspect=5)

#plt.show()











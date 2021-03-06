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
l = 0
checksum = 0
cnt = 0
waitingHeader = True
pack = [0,0,0]
data = []
LOGIC_SCALE = 3000
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
            print "LOGIC"
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
                #i = i * 0.000005756948401 *1000    #em mA
                i =  i * 0.00000092832880672904 *1000    #em mA

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
                print l
                if l & 256:#
                    data_trace.append(LOGIC_SCALE)
                else:
                    data_trace.append(0)

                if l & 512: #bit
                    data_trace1.append(LOGIC_SCALE)
                else:
                    data_trace1.append(0)

                data.append(pack) #manter o estado anterior
                #print l
            cnt = cnt + 1

        if len(data) == 308500:
            print "INTERROMPIDO POR LIMITACAO NO CODIGO! SINCRONIA"
            break
print len(data)
p = []
i = []
v = []
for  cnt in range( 0, len(data) ):
    p.append( data[cnt][0] * data[cnt][1] / 1000 )
    v.append( data[cnt][0] ) 	
    i.append( data[cnt][1] )
t = []
tcnt = 0


#calculo da corrente media
i_tot=0
for i_ins in  i:
    i_tot=i_tot + i_ins
i_med = i_tot / len(i)
print "Corrente Media: " + str(i_med) + "mA"


#calculo da potencia media
p_tot=0
for p_ins in  p:
    p_tot=p_tot + p_ins
p_med = p_tot / len(p)
print "Potencia Media: " + str(p_med) + "mW"

#Ajuste da escala de tempo
for cnt in range (0, len(p)):
    t.append(tcnt)
    tcnt = tcnt + 0.00001976 #50.61 kHz


fig, ax1 = plt.subplots()
ax1.grid(True)
ax1.plot(t, p, 'r-', alpha=0.75)
ax1.set_xlabel('Tempo (s)')
#ax1.tick_params('Logic', colors='b')
ax1.set_ylabel("Potencia (mW)")
#analisador logico:
ax1.plot(t, data_trace, 'b-')
ax1.plot(t, data_trace1, 'g-')
fig.show()




fig2, ax2 = plt.subplots()
ax2.grid(True)
#ax2.plot(t, v, 'bx')
ax2.set_xlabel('Tempo (s)')
ax2.tick_params('y', colors='g')
ax2.set_ylabel("Corrente (mA)")
ax2.plot(t, i, 'g-')
#ax2.plot(t, data_trace1, 'b-')


fig2.show()


fig3, ax3 = plt.subplots()
ax3.grid(True)
ax3.plot(t, v, 'b-')
ax3.set_xlabel('Tempo (s)')
ax3.tick_params('y', colors='b')
ax3.set_ylabel("Tensao (mV)")
ax3.plot(t, data_trace1, 'y-')
#ax3.plot(t, i, 'rx')
fig3.show()


plt.show()





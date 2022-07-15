import matplotlib.pyplot as plt
from sortedcontainers import SortedDict
import sys
import numpy as np
from itertools import islice
import struct



def parser(filename):
    data = []
    f = open(filename, "r")
    cnt = 0
    v = 0
    i = 0
    checksum = 0
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
                v = v * 0.0008021972656 * 1000 #em mV
                i = i * 0.00000575337029108412 *1000    #em mA
                checksum = checksum & 255
                if (checksum == b):
                    pack = [v,i]
                    data.append( pack )
                pack = [v,i]
                data.append(pack)
            cnt = cnt + 1
    return data


#main

if len(sys.argv) < 2:
    print "filename missing"
    sys.exit()
filename = sys.argv[1]


data = parser(filename)  
num_samples = len(data)
print("Numero de amostras brutas: " + str(num_samples) )

vl = np.zeros( num_samples )
il = np.zeros( num_samples )
#criando arrays numpy com as amostras
for cnt in xrange(0, num_samples):
    v = data[cnt][0]
    i = data[cnt][1]
    il[cnt] = i
    vl[cnt] = v

# segmentando os valores para criar as curvas individuais da superficie
# smartload em 6.4ms varre todas as possibilidades
# velocidade de amostragem = 50.610 Hz (19.76 us)
# NUM_SAMPLES_CURVE = 1.2ms / 19.76us
NUM_SAMPLES_CURVE = 64*100
#necessario retirar o excesso de amostras para dividir em partes iguais os dados brutos
excesso = num_samples % NUM_SAMPLES_CURVE
print("Excesso de amostras: " + str(excesso) )
vl = np.delete( vl, np.arange(num_samples-excesso, num_samples) ) 
il = np.delete( il, np.arange(num_samples-excesso, num_samples) ) 
num_samples = len(vl) #novo tamanho
print("Numero de amostras usadas: " + str(num_samples) )
#quebrar em multiplas curvas
vl = np.split(vl, num_samples/NUM_SAMPLES_CURVE)
il = np.split(il, num_samples/NUM_SAMPLES_CURVE) 

#para teste:
vl = vl[4]
il = il[4]
print ("Tamanho curva teste: "+ str(len(vl)) )
pl = il * vl /1000


#criando os coeficientes para esta curva
coef = np.polyfit(il,vl,6) #6

vl_calc = np.polyval(coef,il)
pl_calc = np.array(il) * np.array(vl_calc) /1000

#calcular o erro da curva
#print "--------------------"
#err_v = np.array(vl) - np.array(vl_calc)
##nao necessario err_v[0] = 0 #amostra 0 eh especial pq representa a saida a vazio
#print "V Erro medio: " + str ( err_v.mean() ) + "mV"
#print "V Desvio padrao erro: " + str ( err_v.std() ) + "mV"
#print "-------------------"

### curva calculada:
MAX_VOUT = 5004.5 #mV  DAC MAX 
MIN_VOUT = 0
VDAC_SIZE = 4096
VLSB_SIZE = MAX_VOUT / VDAC_SIZE
RSENSE = 1.045 #OHM
MAX_IOUT = 20 #mA
MIN_IOUT = 0
ILSB_SIZE = 0.00575337029108412  #mA

i_calc = np.arange(0, 4094, 1)
i_calc = np.array(i_calc) * ILSB_SIZE
v_calc = np.polyval(coef, i_calc )
#aux = []
#cnt = 0
#for x in v_calc: #cleanup
#    if x<0:
#        aux.append(0)
#    else: #adiciona offset do shunt - dobrado porque ele existe na captura e vai existir na reproducao
#        #v_ad = x + ( RSENSE * i_calc[cnt] * 2)
#        #v_ad = v_ad + 200 # offset ajuste
#        aux.append(v_ad)
#    cnt = cnt + 1
#v_calc = aux

p_calc = np.array(i_calc) * np.array(v_calc) /1000

#calcula o codigo
i_ad = []
for i in i_calc:
    i_ad.append( int(i / ILSB_SIZE) ) 
v_ad = []

for v in v_calc:
    v_ad.append( int(v / VLSB_SIZE) )


'''
#criar o arquivo do dump
fiv = open("ivcurve.bin", 'wb')

try:
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
except:
    print 'Possivelmente a curva estourou, verifique'

fiv.close()
'''
print ("Criando graficos")

fig, ax1 = plt.subplots()
ax1.grid(True)
ax1.plot(il,vl, 'bx')
ax1.set_xlabel('Current (mA)')
ax1.tick_params('y', colors='b')
ax1.set_ylabel("Voltage (mV)")
#ax1.plot(il, vl_calc, 'b-')

ax2 = ax1.twinx()
ax2.tick_params('y', colors='r')
ax2.plot(il,pl, 'rx')
ax2.set_ylabel('Power (mW)' )
ax2.grid(False)
#ax2.plot(il,pl_calc, 'r-')
fig.show()


#fig2,bx1 = plt.subplots()
#bx1.grid(True)
#bx1.plot(i_calc, v_calc, 'b-')
#bx1.set_xlabel('Current (mA)')
#bx1.tick_params('y', colors='b')
#bx1.set_ylabel("Voltage (mV)")
#bx2 = bx1.twinx()
#bx2.tick_params('y', colors='r')
#bx2.plot(i_calc,p_calc,'g-')
#bx2.set_ylabel("Power (mW)")
#bx2.grid(False)
#fig2.show()


#fig3,cx1 = plt.subplots()
#cx1.grid(True)
#cx1.plot(i_ad, v_ad, 'bx')
#cx1.set_xlabel('Current Code')
#cx1.tick_params('y', colors='b')
#cx1.set_ylabel("Voltage Code'")
#fig3.show()



plt.show()

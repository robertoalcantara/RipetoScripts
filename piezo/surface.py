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


def curve_process( data ):
        #print '.',
        #print data

        vl = []
        il = []
        pl = []
        for i in data:
            if i[1] < 0.001: # or i[1] > 2:
                continue
            il.append( i[1] )
            vl.append( i[0] )
            pl.append( i[1] * i[0] / 1000 )
            # print (str(i[1]) + "," + str(i[0]))  #CSV OUTPUT Curve
        if len( il ) < 20:
            print "Nao possui amostras suficiente. Curva ignorada!"
            return False, [], []
            #return True, np.arange(0, 4096, 1), np.arange(0, 4096, 1) 
        il.append( il[ len(il)-1 ])
        vl.append(0)
    

        coef = np.polyfit(il,vl,3) #6

        vl_calc = np.polyval(coef,il)
        pl_calc = np.array(il) * np.array(vl_calc) /1000

        #calcular o erro
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

        i_calc = np.arange(0, 4096, 1)
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
        #calcula o codigo:
        i_ad = []
        for i in i_calc:
            i_ad.append( int(i / ILSB_SIZE) )
        v_ad = []

        for v in v_calc:
            if v > 6000:
                print "tensao muito alta, possivelmente estourou. Curva de zeros."
                return True, np.arange(0, 4096, 1), np.arange(0, 4096, 1) 
            v_ad.append( int(v / VLSB_SIZE) )


        #Ajuste da escala de tempo
        time = []
        tcnt = 0
        for cnt in range (0, len(data)):
            time.append(tcnt)
            tcnt = tcnt + 0.00001976 #50.61 kHz
        print "Numero itens na curva: " + str( len(data) )

        show_graph( vl, il, pl, vl_calc, pl_calc, v_calc, i_calc, p_calc, v_ad, i_ad  )
        return True, v_ad, i_ad

def show_graph(vl, il, pl, vl_calc,pl_calc, v_calc, i_calc, p_calc, v_ad, i_ad ):
        fig, ax1 = plt.subplots()
        ax1.grid(True)
  
        ax1.plot(il,vl, 'bx')

        ax1.set_xlabel('Corrente (mA)')
        ax1.tick_params('y', colors='b')
        ax1.set_ylabel("Tensao (mV)")

        #ax1.plot(il, vl_calc, 'gx')
        ax2 = ax1.twinx()
        ax2.tick_params('y', colors='r')

        ax2.plot(il,pl_calc, 'rx')
        ax2.set_ylabel('Potencia (mW)' )
        ax2.grid(False)

        #ax2.plot(il, pl_calc, 'r-')
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


##################################################
# Main

if len(sys.argv) < 3:
    print "filename and curve delay missing.  filename NNN (em pulsos de clock)"
    sys.exit()

filename = sys.argv[1]
delay_curves = sys.argv[2] 

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

    if len(curves)==50:
        print "Atingido o limite de curvas"
        break

print "Numero de Curvas armazenadas: " + str(len(curves))

'''
#CSV file of surface
fcsv = open("ivsurface_txt.csv", 'wb')
for k in curves:
    ret, v_ad, i_ad = curve_process( k )
    if ret == False:
        continue #verificar o que fazer aqui
    
    for cnt in xrange(0,4094):
        l = str(v_ad[cnt]) + ',' + str(i_ad[cnt])
        if (cnt<4093):
            l = l+','

        fcsv.write(l)
'''
#meio estupido, mas vai... pegando o numero de curvas na superficie real (processada)

cnt = 0
for k in curves:
        ret, v_ad, i_ad = curve_process(k)
        if ret:
            cnt = cnt+1


fiv = open("ivsurface.bin", 'wb')
num0, num1, dummy1, dummy2 = struct.pack("i", cnt) # len(curves) )
fiv.write(num1)
fiv.write(num0)

num0, num1, num2, num3 = struct.pack("i", int(delay_curves))
fiv.write(num3)
fiv.write(num2)
fiv.write(num1)
fiv.write(num0)

for k in curves:
        ret, v_ad, i_ad = curve_process(k)
        if ret:
            for c in xrange(0, len(i_ad) ):
                i0, i1, dummy1, dummy = struct.pack("i", i_ad[c])
                v0, v1, dummy2, dummy = struct.pack("i", v_ad[c])
                fiv.write('\x0F')
                fiv.write(i1)
                fiv.write(i0)
                fiv.write(v1)
                fiv.write(v0)
                checksum = ord(i0) + ord(i1) + ord(v0) + ord(v1)
                fiv.write( struct.pack("i", checksum)[0] )                


fiv.close()

















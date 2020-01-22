
import matplotlib.pyplot as plt
import math
import numpy as np

file = 'PULSE_DATA_2019-11-14_10:09:37.dat'
f=open(file,"r")
lines=f.readlines()
signal=[]
#print(lines)

for x in lines[2:]:
	signal.append(x.split('\t')[1])
	#print(signal)

f.close()

fig1, ax1 = plt.subplots()
ax1.plot(signal , label = "PPG")
ax1.set ( title = 'PPG collected', xlabel = 'samples', ylabel = 'nU')
ax1.legend()
plt.show()

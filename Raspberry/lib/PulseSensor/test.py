import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

#import matplotlib.pyplot as plt 

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) #(clock=11, MISO=9, MOSI=10)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

print('Raw ADC Value: ', chan.value)
print('ADC Voltage: ' + str(chan.voltage) + 'V')

signal_raw = []
signal_volt = []

i=0
while True:
	signal_raw.append(chan.value)
	signal_volt.append(chan.voltage)
	time.sleep(0.0000008)
	

	#save signal to file
	f = open('signal_raw.txt', 'w')
	f.write(str(signal_raw))
	f.close()

	f = open('signal_volt.txt', 'w')
	f.write(str(signal_volt))
	f.close()


#plot 

#fig1, ax1 = plt.subplots()
#ax1.plot(signal_raw , label = "PPG_raw")
#ax1.set ( title = 'PPG collected', xlabel = 'samples', ylabel = 'nU')
#ax1.legend()
#plt.show()


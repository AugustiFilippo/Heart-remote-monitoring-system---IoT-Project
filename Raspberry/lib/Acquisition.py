import subprocess
import time

class MyAcquisition:

	def __init__(self):
		pass

	def run(self):
        #call the PulseSensor c program and acquire data from the sensor for 10$

		p = subprocess.Popen("./PulseSensor/pulseTimer_mine")
		time.sleep(10)
		p.kill()
                # I now have a PPG buffer saved into home/pi/Documents/PulseSen$
                # saved as buffer.PPG.dat


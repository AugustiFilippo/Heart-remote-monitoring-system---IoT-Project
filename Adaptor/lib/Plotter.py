import matplotlib.pyplot as plt
import os
import time
import ../lib/TSAMyMQTT as TSMQ
import ../lib.GetDataFromCatalog as GDFC
import json
# plt.ion()

class myPlotter(object):
	
	def __init__(self):
		self.figPath = '\data\PlotData'
		self.figFilename = '\plotPPG.txt'
		self.timeArrayName = '\plotPPGTime.txt'
		self.currDir = os.getcwd()
		
		
	def myOpen(self):

		f = open((self.currDir + self.figPath + self.figFilename),'r')
		self.PPGSignal = f.read()[1:-1]
		self.PPGSignal = self.PPGSignal.split(',')
		self.PPGSignal = [ int(x) for x in self.PPGSignal]
		f.close()

		# f = open((self.currDir + self.figPath + self.timeArrayName),'r')
		# self.timeArray = f.read()[1:-1]
		# self.timeArray = self.timeArray.split(',')
		# self.timeArray = [ int(y) for y in self.timeArray]
		# f.close()
			
	def myPlot(self):
	
		print("printing the last acquired 10s of signal")
		
		y = self.PPGSignal[-10*125:-1] #self.timeArray
		
		fig = plt.figure(1)
		ax = fig.add_subplot(111)
		line1, = ax.plot(y, '-b')

		line1.set_ydata(y)
		fig.canvas.draw()
		# plt.draw()
		# plt.show(block = False)
		# plt.pause(30)
			
	def mySaveFig(self):
		plt.savefig( './img/PPG-signal.png')
		plt.close()
		
if __name__ == '__main__':
	
	doctorID = "DOCTOR1"
	
	f = open("./data/ThingSpeakAdaptor_config.json")
	config = json.loads( f.read())
	WSC_URL = config["WebServiceCatalog"]["url"]
	PlotterGDFC = GDFC.GetDataFromWSCatalog(WSC_URL)
	msgBrIP, msgBrPORT = PlotterGDFC.get_msgbroker()
	
	currentCatalog = json.loads(PlotterGDFC.get_all_info())
	DoctorsPatients = currentCatalog['Doctors'][doctorID].keys() #list of all patients the Doctor can see
	patientID = "PATIENT1" #this line simulates the choice of the doctor among many patients
	PPGsamplesTopic = currentCatalog["Patients"][patientID]["samples"]
	HRTopic = currentCatalog["Patients"][patientID]["Heart rate"]
	IBITopic = currentCatalog["Patients"][patientID]["Inter-beat-interval"]
	
	MP = myPlotter() 
	
	MQclient = TSMQ.MyClient(PPGsamplesTopic, HRTopic,IBITopic, None , None, clientID = 'Plotter', broker = msgBrIP, port = msgBrPORT, keepalive = 60, isSubscriber = True, subTopics = [PPGsamplesTopic])
		
	MQclient.start() #connection to broker and subscribing	
	

	time.sleep(2)
	MP.myOpen()
	MP.myPlot()
	MP.mySaveFig()
	

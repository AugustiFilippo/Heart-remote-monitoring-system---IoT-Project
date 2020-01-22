import json
import lib.Acquisition as ACQ
import numpy as np
import os
import time
from datetime import datetime
import lib.SenMLTransform as SM
import lib.MyMQTT as MQTT
import lib.GetDataFromCatalog as GDFC

#------------------------------------------------------------------------------
# Initializing the instance of MQTT Publisher
#- ThingSpeakAdaptor settings to access to WebService Catalog
f = open("./data/config.json")
config = json.loads( f.read())
WSC_URL = config["WebServiceCatalog"]
RaspGDFC = GDFC.GetDataFromWSCatalog(WSC_URL)
msgBrIP, msgBrPORT = RaspGDFC.get_msgbroker()

deviceID = config["device info"]["Photopletysmography RaspberryPi"]["deviceID"]
PatientID = config["device info"]["Photopletysmography RaspberryPi"]["PatientID"]
PPGsamplestopic = config["microservices offered"]["PPG signal"]["topic"]
HRtopic = config["microservices offered"]["Heart rate"]["topic"]
IBItopic = config["microservices offered"]["Inter-beat-interval"]["topic"]

RaspPublisher = MQTT.MyClient( deviceID, msgBrIP, msgBrPORT, 60)
RaspPublisher.start() #connection and loop start

while 1:
	# --------------------------------------------------------------------------
	#Acquisition: assign a timestamp to the acquisition in order to be able to
	#             create a timestamp for each sample basing on the sampling freq

	#get timestamp
	# current date and time.
	now = datetime. now()
	t_zero = datetime. timestamp(now)
	print("Acquisition basetime timestamp =", t_zero)
	Acq = ACQ.MyAcquisition()
	Acq.run()

	# --------------------------------------------------------------------------
	#read the acquisition  file and for each line create a timestamp
	dirname =  os.getcwd()
	filename = dirname + "/PulseSensor/PULSE_DATA/buffer_PPG.dat"
	print("opening file...%s" %filename)

	myFileObject = open(filename,'r')
	
	#transfrom in SenML format each sample
	sML = SM.SenMLTransf(baseName = "FA_PPG_sensor" , baseTime = t_zero)
	
	#create timestamp for each line
	sML.createEventsArray(fileObject = myFileObject)
	myFileObject.close()
	
	#sML.createTimeStamps(t_zero = 0) #all the dt are deltas from baseTime
	PPGSenML = sML.transf(arrayName = "PPG signal") 
	HRSenML = sML.transf(arrayName = "Heart rate")
	IBISenML = sML.transf(arrayName = "Inter-beat-interval")
	#print ("PPGSenML: ",PPGSenML)
	print ("\nSending PPG signal as a SenML message: ", json.dumps(PPGSenML)[0:300],"...\n")
	print ("\nSending HR value as a SenML message: ",HRSenML, "\n")
	print ("\nSending IBI value as a SenML message: ",IBISenML, "\n")
	#-----------------------------------------------------------------------------
	#send through MQTT
	RaspPublisher.MyPublish(PPGsamplestopic, json.dumps(PPGSenML), myRetain = True)
	RaspPublisher.MyPublish(HRtopic, json.dumps(HRSenML),myRetain = False)
	RaspPublisher.MyPublish(IBItopic, json.dumps(IBISenML), myRetain = False)

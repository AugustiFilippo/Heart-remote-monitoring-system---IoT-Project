import json
import time
import TSAMyMQTT
import GetDataFromCatalog as GDFC
import cherrypy
import socket
import os

def get_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()
	return IP
	
def myManager(IBI, HR):
	global inputField
	
	if (inputField == 'Inter-beat-interval'):
		# print ('\n\n inputField after : ', inputField)
		IBI.starter()
		try:
			HR.myStop()
		except:
			pass
		
	elif (inputField == 'Heart rate'):
		HR.starter()
		try:
			IBI.myStop()
		except:
			pass

class MyAdaptor(object):

	def __init__(self, doctorID, patientID, msgBrIP, msgBrPORT, chan_field_names, field_assignments, QoS, TSurl, APIKEY, currentCatalog, PPGsamplesTopic, HRTopic, IBITopic):
		""" chan_field_names must be one of the two "Heart rate", "Inter-beat-interval" """
		
		global updateFlag
		global inputField
		updateFlag = True
		
		#- ThingSpeakAdaptor main settings
		self.QoS = QoS # security level of information transfer
		self.chan_field_names =  chan_field_names 
		# print ("\nList of mqtt topics to be subscribed to : ", self.chan_field_names)
		self.field_assignments = field_assignments #assignments
		# print('\n List of the "mqtt topics - to - ThingSpeak field" assignments:', self.field_assignments)
		self.keepAlive = 60
		
		#- Address to ThingSpeak
		self.url_thingspeak = TSurl
		self.APIKEY = APIKEY
		
		self.patientID = patientID
		
		self.PPGsamplesTopic = PPGsamplesTopic
		self.HRTopic = HRTopic
		self.IBITopic = IBITopic
		
		self.msgBrIP =  msgBrIP
		self.msgBrPORT = msgBrPORT
		
		# get current Catalog 
		self.CatalogDict = currentCatalog  
		self.catalogDevices = currentCatalog['devices'] 
		self.catalogMs = currentCatalog['microservices'] #key of microservice is the name of the microsrvice, such as "PPG signal", "Heart rate" or "iBI"
		# print ("\n microservices already present in the Catalog: " , self.catalogMs)
		
		self.Adaptor_SubTopics = [] 

		if inputField in self.catalogMs:
				# print ('OK')
				self.Adaptor_SubTopics.append(self.CatalogDict["microservices"][inputField]["topic"]) 

	def starter(self):
		

		# input("choose which of the two Thingspeak charts you want to update: \n\t- type 'field1' to update 'Heart rate' chart \n\t- type 'field2' to update 'Inter-beat-interval' chart: ")
		# Init and start ThingSpeakAdaptor
		print (" ThingSpeak Adaptor subscribing to topics: %s \nSubscribing..." %self.Adaptor_SubTopics)
		
		#create instance of mqtt Subscriber and start it
		self.ThSpSub = TSAMyMQTT.MyClient(self.PPGsamplesTopic, self.HRTopic,self.IBITopic, self.APIKEY, self.url_thingspeak, self.patientID, self.msgBrIP, self.msgBrPORT, self.keepAlive, isSubscriber = True, subTopics = self.Adaptor_SubTopics, QoS = self.QoS, field_assignments = self.field_assignments, chan_to_update = inputField)
		self.ThSpSub.start() #connection to broker and subscribing	
	
		# self.tsa = TSA.ThingSpeakAdaptor( self.PPGsamplesTopic, self.HRTopic, self.IBITopic, self.APIKEY, self.url_thingspeak, self.patientID, self.msgBrIP, self.msgBrPORT, self.keepAlive, self.Adaptor_SubTopics, self.QoS, self.APIKEY, self.url_thingspeak, self.field_assignments, updateField)
		 
	def myStop(self):
		self.ThSpSub.stop()
		# self.tsa.myStop()
		
if __name__ == '__main__':
	
	global updateFlag #represent the permission of updating the ThingSpeak field
	global inputField #after inizialization represents the choice of the doctor about the field to uodate on ThingSpeak ( HR o IBI )
	
	doctorID = "DOCTOR1"
	
	f = open("./data/ThingSpeakAdaptor_config.json")
	config = json.loads( f.read())
	WSC_URL = config["WebServiceCatalog"]["url"]
	TSAdaptGDFC = GDFC.GetDataFromWSCatalog(WSC_URL)
	msgBrIP, msgBrPORT = TSAdaptGDFC.get_msgbroker()
	
	currentCatalog = json.loads(TSAdaptGDFC.get_all_info())
	DoctorsPatients = currentCatalog['Doctors'][doctorID].keys() #list of all patients the Doctor can see
	patientID = "PATIENT1" #this line simulates the choice of the doctor among many patients
	PPGsamplesTopic = currentCatalog["Patients"][patientID]["samples"]
	HRTopic = currentCatalog["Patients"][patientID]["Heart rate"]
	IBITopic = currentCatalog["Patients"][patientID]["Inter-beat-interval"]
	
	#- ThingSpeakAdaptor settings loading from Catalog
	TSurl = currentCatalog["microservices"]["ThingSpeak Adaptor"]["update url"]
	patientAPIKEY = currentCatalog["Patients"][patientID]["ThingSpeak API KEY"]
	TSQoS = currentCatalog["microservices"]["ThingSpeak Adaptor"]["QoS"]
	chan_field_names = currentCatalog["microservices"]["ThingSpeak Adaptor"]["chan_field_names"]
	field_assignments = currentCatalog["microservices"]["ThingSpeak Adaptor"]["field_assignments"]
	
	#creation of MyAdaptor instances and initializing
	inputField = "Heart rate" #default
	HR = MyAdaptor(doctorID, patientID, msgBrIP, msgBrPORT, chan_field_names, field_assignments, TSQoS, TSurl, patientAPIKEY, currentCatalog, PPGsamplesTopic, HRTopic, IBITopic)
	HR.starter() #field_assignments["Heart rate"])
	HR.myStop()
	
	inputField = "Inter-beat-interval"
	IBI = MyAdaptor(doctorID, patientID, msgBrIP, msgBrPORT, chan_field_names, field_assignments, TSQoS, TSurl, patientAPIKEY, currentCatalog, PPGsamplesTopic, HRTopic, IBITopic)
	IBI.starter()
	IBI.myStop()
	
	count = 1
	
	while True:
	
		time.sleep(2)
		currentCatalog = json.loads(TSAdaptGDFC.get_all_info())
		updateFlag = currentCatalog["Doctors"][doctorID][patientID]["updateFlag"]
		
		if count == 1 and updateFlag == 'True':
			myManager(IBI, HR)
			
		else:
			if updateFlag == 'False':
				HR.myStop()
				IBI.myStop()
				count = 1
				continue
			
			doctorFieldChoice = currentCatalog["Doctors"][doctorID][patientID]["inputField"]

			print ('\n\ndoctorFieldChoice: ', doctorFieldChoice, '\tinputField : ', inputField)
			
			if doctorFieldChoice == inputField :
				continue
			else: 
				print ('NOT doctorFieldChoice ==inputField')
				
				inputField = doctorFieldChoice
				myManager(IBI, HR)
		
		count +=1

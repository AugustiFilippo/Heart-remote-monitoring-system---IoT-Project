import paho.mqtt.client as MQTT
import time
import json
from datetime import datetime
import requests
import matplotlib.pyplot as plt
import os

class MyClient:
	
	def __init__(self, PPGsamplesTopic, HRTopic,IBITopic, patientAPIKEY, TSurl,clientID, broker, port = None, keepalive = 60, isSubscriber = False, subTopics = '', pubTopic = "", QoS = 0, field_assignments = None, chan_to_update = None):
		
		self.broker = broker
		self.port = port
		self.keepAlive = keepalive
		self.clientID = clientID
		self.subTopics = subTopics # can be either a single topic or a list of multiple topics
		self.pubTopic = pubTopic
		self.QoS = QoS
		self.isSubscriber = isSubscriber
		self.userdata = None
		self.DATA = {}
		self.connected_flag = 0 
		self.field_assignments = field_assignments
		self.chan_to_update = chan_to_update
		self.PPGsamplesTopic = PPGsamplesTopic
		self.HRTopic = HRTopic
		self.IBITopic = IBITopic
		self.APIKEY = patientAPIKEY
		self.TSurl = TSurl
		# print ("\n\n\n\n\n\n\n\n chan to update inside MYMQTT: ", self.chan_to_update, "\n\n\n\n\n\n\n\n")
		self.PPGSignal = []
		self.timeArray = []
		# create an instance of paho.mqtt.client
		#set of clean_session to false to create a transitory client
		self._client = MQTT.Client(clientID, clean_session = False) 

		# register the callback
		self._client.on_connect = self.myOnConnect
		self._client.on_message = self.myOnMessage #Received
		self._client.on_publish = self.myOnPublish
		self._client.on_subscribe = self.myOnSubscribe

	def myOnConnect (self, _client, userdata, flags, rc):
		print ("Connected to %s with result code: %d" %(self.broker, rc))
		self.connected_flag = 1
		
	def myOnMessage(self, _client, userdata, msg):
		#""" the received message is a SenML format message with an 'e' array of ultiple events:
		#the data have to be extracted and directed to the proper ThingSpeak channel"""
		
		topic = msg.topic
		print ("topic", topic)
		text=str(msg.payload.decode("utf-8","ignore"))
		data=json.loads(text) #decode json data
		
		if msg.topic == self.HRTopic or msg.topic == self.IBITopic:
			# if the resource is a valid resource, it publishes value in the proper field and channel in ThingSpeak
			toBePrinted = text
			print("data received", toBePrinted)
			chan_name = data['e']['n']
			fieldNum = self.field_assignments[chan_name]

			value = data['e']['v']
			
			# timestamp creation
			tmp = data ['bt'] 
			# print ("\n\ntmp :", tmp)
			# print(datetime.utcfromtimestamp(int(tmp)))
			MsgTimeStamp = datetime.fromtimestamp(int(tmp))
			print ("MsgTimeStamp : ", MsgTimeStamp)
			# time.sleep(2)
			
			# print(fieldNum)
			# print(value)
			self.myUpload(fieldNum,value,MsgTimeStamp)
			
		elif msg.topic == self.PPGsamplesTopic:
			toBePrinted = text[0:200]
			print("data Received",toBePrinted,"...")
			self.SenMLPlot(data)

	def myOnPublish(self, _client,userdata, mid):
		# Tells us that the Publishing is gone correct
		print('Publishing concluded')

	def myOnSubscribe(self, _client,userdata, mid , granted_qos):
		# Tells us that the Publishing is gone correct
		print('Subscribing concluded')

	def MyPublish (self, msg):
		# if needed, you can do some computation or error-check before
		# publishing
		print ("publishing '%s' with topic '%s'" % (msg, self.pubTopic))
		# publish a message with a certain topic
		self._client.publish(topic = self.pubTopic, payload = msg, qos =  self.QoS, retain = False)

	def MySubscribe (self):
	
		# if needed, you can do some computation or error-check before
		# subscribing
		
		for subTopic in self.subTopics:
			print ("subscribing to %s" % (subTopic))
			# subscribe for a topic
			self._client.subscribe(subTopic, 0)#self.QoS)
			# time.sleep(3)

	def start(self):
		#manage connection to broker
		print ("connecting to:", self.broker, self.port)
		self._client.connect(self.broker, self.port, self.keepAlive)
		self._client.loop_start()

		if self.isSubscriber == True :
			while self.connected_flag == 0:
				time.sleep(0.5)
				print("waiting the connection ")
			
			self.MySubscribe()

		# self._client.loop_forever()

	def stop(self):
		if (self.isSubscriber):
			#remember to unsuscribe if it is working also as subscriber
			for subTopic in self.subTopics:
				self._client.unsubscribe(subTopic)

		self._client.loop_stop()
		self._client.disconnect()
		
	def myUpload(self,fieldNum, value, MsgTimeStamp):
		""" fieldNum is a string containing the field number
		value is the 'e' data extracted from the SenML message and must be a number"""
		
		if fieldNum == self.field_assignments[self.chan_to_update]:
			p = { 'api_key' : self.APIKEY, str(fieldNum): int(value) }#, "created_at": MsgTimeStamp} #"2014 - 12 - 31 23:59:59"}
			r = requests.get ( self.TSurl, params = p)
			# time.sleep(2)
			if r.status_code == 200: 
				print ( str(datetime.datetime.now()) + "- "+ " uploaded on ThingSpeak")
			else:
				print ("Error while uploading" )
				print ("Status code: " + str(r.status_code) )			
	
	def SenMLPlot(self, SenMLMessage):
		msgEvents = SenMLMessage['e']
		
		# timestamp creation
		t_zero = SenMLMessage ['bt']
		# print ("msgEvents:", msgEvents)
		for elem in msgEvents:
			self.PPGSignal.append(int(elem['v']))
			self.timeArray.append(int(elem['t']))
		
		currDir = os.getcwd()
		print (" Saving buffer into " + currDir + '\data\PlotData\plotPPG.txt')
		
		f = open((currDir +'\data\PlotData\plotPPG.txt'),'w')
		f.write(str(self.PPGSignal))
		f.close()
		
		f = open((currDir +'\data\PlotData\plotPPGTime.txt'),'w')
		f.write(str(self.timeArray))
		f.close()
		
		
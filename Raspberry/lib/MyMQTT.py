import paho.mqtt.client as MQTT
import time

class MyClient:

	def __init__(self,clientID, broker, port = None, keepalive = None, isSubscriber = False, subTopic = '', pubTopic = ""):
		self.broker = broker
		self.port = port
		self.keepAlive = keepalive
		self.clientID = clientID
		self.subTopic = subTopic
		self.pubTopic = pubTopic
		self.isSubscriber = isSubscriber
		self.userdata = None
		self.DATA = {}
		self.connected_flag = 0 

		# create an instance of paho.mqtt.client
		#set of clean_session to false to create a transitory client
		self._client = MQTT.Client(clientID) 

		# register the callback
		self._client.on_connect = self.myOnConnect
		self._client.on_message = self.myOnMessage
		self._client.on_publish = self.myOnPublish
		self._client.on_subscribe = self.myOnSubscribe

	def myOnConnect (self, _client, userdata, flags, rc):
		print ("Connected to %s with result code: %d" %(self.broker, rc))
		self.connected_flag = 1
			
	def myOnMessage(self, _client ,userdata, message):
		# A new message is received
		print("topic: %s \t\tmessage received: " %str(message.topic) ,str(message.payload.decode("utf-8")))

		# print ("Received __ Topic: " + msg.topic + " QoS: "+ str(msg.qos) + "Message: "+msg.payload)
		# update Data
		#self.DATA[msg.topic]=msg.payload

	def myOnPublish(self, _client,userdata, mid):
		# Tells us that the Publishing is gone correct
		print('Publishing concluded')

	def myOnSubscribe(self, _client,userdata, mid , granted_qos):
		# Tells us that the Publishing is gone correct
		print('Subscribing concluded')

	def MyPublish (self, topic, msg, myRetain = False):
		# if needed, you can do some computation or error-check before
		# publishing
		if len(msg)>300:
			toBePrinted = msg[0:300]
		else:
			toBePrinted = msg

		print ("\nPublishing '%s' with topic '%s'\n" % (toBePrinted, topic))
		# publish a message with a certain topic
		self._client.publish(topic, payload = msg, qos =  2, retain = myRetain)

	def MySubscribe (self):
		# if needed, you can do some computation or error-check before
		# subscribing
		print ("\nsubscribing to %s\n" % (self.subTopic))
		# subscribe for a topic
		self._client.subscribe(self.subTopic, 2)

	def start(self):
		#manage connection to broker
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
			self._client.unsubscribe(self.subTopic)

		self._client.loop_stop()
		self._client.disconnect()



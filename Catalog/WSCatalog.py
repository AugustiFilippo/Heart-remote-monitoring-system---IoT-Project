import cherrypy
import json
import time
import os
import io
import socket


def get_ip():
	""" gets the IP of the Web service host	"""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		#try to connect to a private network
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		#otherwise connect to a localhost 
		IP = '127.0.0.1' #localhost IP
	finally:
		s.close() # close connection
	return IP

class Searcher(object):
	""" This object allows to browse and check the elements of the Catalog"""
	def __init__(self):
		pass
			
	def all_devices(self):
		Catalog = cherrypy.session['Catalog']
		print(" Catalog",Catalog)
		# print ("\n\n result of searcher \n\n :", list(Catalog["devices"].keys()))
		return {'devices' : list(Catalog["devices"].keys())}
		
	def all_microservices(self):
		Catalog = cherrypy.session['Catalog']
		print("global Catalog",Catalog)
		return {'microservices': list(Catalog['microservices'].keys())}
	
	
class deviceManager(object):
	def __init__(self):
		pass

	def add_device(self, ReqData ): # must be of the type {deviceKey : deviceField}
		""" 
		deviceKey must be the key by which the device is wanted to be recognized
		deviceField must be a dictionary composed as follows 
		{"deviceID": "..."
		"resource" : ...,
		"endpoints" : ...,
		"sensors" : ... 
		}
		"""
		
		# print ("\n\n list(ReqData.items()) \n\n ", list(ReqData.items()))
		deviceKey, deviceField = list(ReqData.items())[0]

		# print ("deviceKey", deviceKey)
		# print ("deviceField", deviceField)
		#retrieve Catalog from session
		Catalog = cherrypy.session['Catalog']
		
		# print ("list(Catalog['devices'].keys())", list(Catalog['devices'].keys()))
		if deviceKey not in list(Catalog['devices'].keys()):
			Catalog['devices'][deviceKey] = deviceField
		# print (" \n\n Catalog with added device :\t\t", Catalog)
		Catalog["number_of_devices"] += 1
		cherrypy.session ['Catalog'] = Catalog # Update the session
	
	def remove_device(self, deviceName):
		""" deviceName must be the "deviceID" key """
		del Catalog["devices"][deviceName]
	
	def add_microservice(self,ReqData):
	
		""" microservice must be a dict composed as follows
			{"PPG signal": {
				"microserviceID": "PPG signal",
				"endpoints": {
							"topic": "/PPG/sensor/samples",
							"msgbroker": "test.mosquitto.org"
							},
				"Protocol": "MQTT",
				"hostDeviceID": "PPG_RaspPi"
				}
			}
		"""
		# print ("\n\n list(ReqData.items()) \n\n ", list(ReqData.items()))

		msKey, msField = list(ReqData.items())[0]
		# print ("msKey", msKey)
		# print ("msField", msField)
		#retrieve Catalog from session
		Catalog = cherrypy.session['Catalog']
		
		# print ("list(Catalog['microservices'].keys())", list(Catalog['devices'].keys()))
		if msKey not in list(Catalog['microservices'].keys()):
			Catalog['microservices'][msKey] = msField
			print (" \n\n Catalog with added device :\t\t", Catalog, "\n\n")
			
					
class JsonManager(object):
	
	def __init__(self):
		pass
	
	def write(self,CatalogDict,path):
		""" CatalogDict: a dictionary containing the updated Catalog
			path: Catalog path
		"""
		# global semafor
		#aspetta finchè non si ha il semaforo
		# while not semafor:
			# pass
		
		# semafor=False # reset variable
		f=open(path,'w')
		f.write(json.dumps(CatalogDict))
		f.close()
		# semafor=True
		
	
	def read(self,path):
		""" path: Catalog path
		"""
		# global semafor
		#aspetta finchè non si ha il semaforo
		# while not semafor:
			# pass
		# semafor=False
		
		f = open(path,'r')
		CatalogDict = json.loads(f.read()) #dict
		f.close()
		# semafor=True
		return CatalogDict
		
@cherrypy.expose
class CatalogWebService(object):
	def __init__(self):
		self.jm = JsonManager()
		self.s = Searcher()
		self.dm = deviceManager()
	
	def POST(self,*uri,**params):
		""" Allows to send the current Catalog inside the request body in order to be saved into the session 
		and modified through the initial talking between the IoT devices
		"""

		ReqData = cherrypy.request.body.read() #the info to be added to the Catalog are passed into the request body
		# print ("\n Request body content (ReqData)", ReqData)
		ReqData = json.loads(ReqData) #dict

		Catalog = self.jm.read(CatalogPath) # retrieve the updated Catalog
		cherrypy.session['Catalog'] = Catalog # the current Catalog is saved into the current request session

		# print ("cherrypy.session['Catalog'] : ",cherrypy.session['Catalog'])
		# print ("uri[0].lower() :", uri[0].lower())
		
		if uri[0].lower() == 'register' and len(uri)==2: 
			
			if uri[1] == 'newdevice':
				#add device to Catalog
				self.dm.add_device(ReqData) #ReqData must be the device dictionary
				Catalog["last_edit"] = time.time()
				self.jm.write(Catalog,CatalogPath)
				return ('\nRegistration Completed, updated Catalog %s\n' %Catalog)
				time.sleep(10)
				print ("\n\n")
				
			elif uri[1] == 'newmicroservice':
				#add ms to Catalog
				self.dm.add_microservice(ReqData) #ReqData must be the microservice dictionary
				Catalog["last_edit"] = time.time()
				self.jm.write(Catalog,CatalogPath)
				return ('\nRegistration Completed, updated Catalog %s\n' %Catalog)
		else:
			raise cherrypy.HTTPError(404)
			
				

	def GET(self, *uri, **params):
		"""
		The GET request must be formulated as follow:
			- WSCatalogUrl + '/msgbroker'
			- WSCatalogUrl + '/devices'
			- WSCatalogUrl + '/microservices'
			**following parameters can be added to the request
		"""
		Catalog = self.jm.read(CatalogPath) # retrieve the updated Catalog as dict
		cherrypy.session['Catalog'] = (Catalog)
		# print ("cherrypy.session['Catalog'] : ",cherrypy.session['Catalog'])
		# print ("uri[0].lower() :", uri[0].lower())
		# print ("if cherrypy.session['Catalog']", (cherrypy.session['Catalog'] is not None ))
		
		if (cherrypy.session['Catalog'] is not None) and len(uri)==1 and uri[0].lower() == 'all' :
			return json.dumps(Catalog)#cherrypy.session['Catalog'])
			
		if (cherrypy.session['Catalog'] is not None) and len(uri)==1 and uri[0].lower() == 'devices':
			""" if the request is of the type /devices 
			"""
			devices = self.s.all_devices() #list of all devices already registered
			
			""" if parameters are added to the "devices" request, the spec_device function is called
				in this case the request is of the type /devices?p1='deviceID'
			"""
			if params == {}:
				print ( "result of all_devices:" , json.dumps(devices))
				return json.dumps(devices)

			elif len(params)==1 and (list(params.keys()) in ['deviceID','resources']):
				devices = self.s.spec_device(params)
				if len(devices['devices'])>0:
					return json.dumps(devices)
				else:
					raise cherrypy.HTTPError(404)	# not found			
			else:
				raise cherrypy.HTTPError(400)
		
		elif (cherrypy.session['Catalog'] is not None) and len(uri)==1 and uri[0].lower()=='microservices':
			""" if the request is of the type /microservices 
			"""
				
			microservices = self.s.all_microservices() #list of all microservice already registered
			if params == {}:
				print ( "result of all_microservice:" , json.dumps(microservices))
				return json.dumps(microservices)

			elif len(params) == 1 and (list(params.keys())[0] in ['microserviceID','topic']):
				microservices = self.s.spec_microservice(params)
				if len(microservices['microservices'])>0:
					return json.dumps(microservices)
				else:
					raise cherrypy.HTTPError(404)	# not found			
			else:
				raise cherrypy.HTTPError(400)

		elif (cherrypy.session['Catalog'] is not None) and len(uri)==1 and uri[0].lower()=='msgbroker' and params=={}:
			""" if the request is of the type /msgbroker 
			"""
			# print ("\n\n  json.dumps({'msgbroker':Catalog['msgbroker']}) \n\n",  json.dumps({'msgbroker':Catalog['msgbroker']}))
			# print (" type ", type({'msgbroker':Catalog['msgbroker']}))
			return json.dumps({'msgbroker':Catalog['msgbroker']})
			
		else:
			raise cherrypy.HTTPError(401)
			
	def PUT(self,*uri,**params):
				
		ReqData = cherrypy.request.body.read() #the info to be added to the Catalog are passed into the request body
		ReqData = json.loads(ReqData) #dict
		print ("\n Request body content (ReqData)", ReqData)

		Catalog = self.jm.read(CatalogPath) # retrieve the updated Catalog
		cherrypy.session['Catalog'] = Catalog # the current Catalog is saved into the current request session
		
		if (cherrypy.session['Catalog'] is not None) and len(uri)==3 and uri[0].lower() == 'setflag': 
			doctorID = uri[1]
			patientID = uri[2]
			flagToUpdate = list(ReqData.keys())[0]
			flagValue = list(ReqData.values())[0]
			Catalog['Doctors'][doctorID][patientID][flagToUpdate] = flagValue
			self.jm.write(Catalog,CatalogPath)
			print ('\n%s updated, %s : %s\n' %(str(flagToUpdate), "Doctors: {" + str(doctorID) + ': {' + str(patientID)+ ': {' +str(flagToUpdate) + ':' , flagValue + '}}}'))
		else:
			raise cherrypy.HTTPError(400)

			
	def DELETE(self,*uri,**params):
		if 'Catalog' not in list(cherrypy.session.keys()):
			raise cherrypy.HTTPError(401)
			
		if cherrypy.session['Catalog'] and len(uri)==1 and uri[0].lower()=='delete' and len(params)==1 and list(params.keys())[0]=='deviceID':	
			
			devices = self.s.all_devices
			check = [params['deviceID'] == dev['deviceID'] for dev in devices] # flag

			if True in check:
				self.dm.remove_device(params)
				Catalog["last_edit"] = time.time()
				self.jm.write(Catalog,path)
			else:
				raise cherrypy.HTTPError(404)
				
		elif cherrypy.session['Catalog'] and len(uri)==1 and uri[0].lower()=='clean' and len(params)==1 and list(params.keys())[0]=='age':
				
				Catalog["number_of_devices"]=0
				Catalog['devices'] = {}
				Catalog['microservices'] = {}
				Catalog["last_edit"]=time.time()
				self.jm.write(Catalog,path)
			
		else:
			raise cherrypy.HTTPError(400)					

if __name__== "__main__":
	
	f = open("data/WSCatalog_config.json")
	conf = json.loads(f.read())
	f.close()
	
	# init database path
	global CatalogPath
	CatalogPath = conf["CatalogPath"]

	# init semafor for access to database file
	# global semafor
	# semafor=True

	# init database variable
	jm = JsonManager()
	global Catalog
	Catalog = jm.read(CatalogPath)

	# Web Service configuration
	config = {
		'global': {
			#'server.socket_host':  '192.168.43.208',
			'server.socket_host': get_ip(),
			'server.socket_port': 9090,
		},
		'/': {
				'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
				'tools.sessions.on': True,
				'tools.response_headers.on': True,
				'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
				'tools.staticdir.on': True,
				'tools.staticdir.dir': '',
			}
		}
	
	# Start Web Service
	time.sleep(1)
	print ("\nCatalog at the starting time :\n\n", json.dumps(Catalog), "\n")
	# cherrypy.session['Catalog'] = ""#json.dumps(Catalog)
	time.sleep(3)
	cherrypy.quickstart(CatalogWebService(), '/', config = config)
	
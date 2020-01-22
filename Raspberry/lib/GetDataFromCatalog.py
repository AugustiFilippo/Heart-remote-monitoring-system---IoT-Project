import requests
import json

class GetDataFromWSCatalog:
	"""- GetDataFromWSCatalog: REST client for WebService Catalog"""
	
	def __init__(self,WSCatalogUrl):
		self.WSCatalogUrl = WSCatalogUrl #WSCatalog url
		self.s = requests.Session()
		self.microservices = {}
	
	def get_msgbroker(self):
		# get message broker from WebServiceCatalog
		r = self.s.get(self.WSCatalogUrl + '/msgbroker') 
		msgbr = json.loads(r.text)['msgbroker']
		return msgbr['IP'],msgbr['PORT']
			
	def get_microservices(self):
		# get microservices list from WebServiceCatalog
		r=self.s.get(self.WSCatalogUrl + '/microservices')
		self.microservices = json.loads(r.text)['microservices']
		return self.microservices
		
	def get_devices(self):
		# get microservices list from WebServiceCatalog
		r = self.s.get (self.WSCatalogUrl + '/devices')
		# print  (self.WSCatalogUrl + '/devices')
		devices = json.loads(r.text)['devices']
		return devices
		
	def get_all_info(self):
		r = self.s.get (self.WSCatalogUrl + '/all')
		CatalogDict = r.text #json.loads(r.text)
		return CatalogDict
		
	def get_ServerURL(self, microserviceID):
		""" server microserviceID of this project: "ThingSpeakPPG" """
		url = None
		while url is None:
			microservices = self.get_microservices()
			for ms in list(microservices).keys(): 
				if microservices[ms][microserviceID] == microserviceID:
						url = microservices[ms]['endpoints']
			if url is None:			
				print (" address not found")
			else:
				print (" address found")
		return url

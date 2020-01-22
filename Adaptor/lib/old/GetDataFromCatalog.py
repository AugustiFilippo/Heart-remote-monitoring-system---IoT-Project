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
		print ("\n\nBROKER \n\n", msgbr)
		return msgbr['IP'],msgbr['PORT']
			
	def get_microservices(self):
		# get microservices list from WebServiceCatalog
		r=self.s.get(self.WSCatalogUrl + '/microservices')
		self.microservices = json.loads(r.text)['microservices']
		return self.microservices
		
	def get_devices(self):
		# get microservices list from WebServiceCatalog
		r = self.s.get (self.WSCatalogUrl+'/devices')
		print  (self.WSCatalogUrl + '/devices')
		devices = json.loads(r.text)['devices']
		return devices
	
	def get_all_info(self):
		r = self.s.get (self.WSCatalogUrl + '/all')
		CatalogDict = (r.text)
		return CatalogDict
		
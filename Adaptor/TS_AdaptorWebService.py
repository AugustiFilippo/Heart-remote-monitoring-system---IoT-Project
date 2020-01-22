import json
import time
import lib.GetDataFromCatalog as GDFC
import cherrypy
import socket
import os
import requests
import subprocess as sp

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

@cherrypy.expose
class AdaptorWebService(object):
	
	def __init__(self,doctorID, patientID):
		self.Adaptor_SubTopics = []
		self.doctorID = doctorID
		self.patientID = patientID
		
		f = open("./data/ThingSpeakAdaptor_config.json")
		conf = json.loads(f.read())
		f.close()
		
		self.WSC_url = conf["WebServiceCatalog"]["url"]
		
		global updateFlag
		global inputField

	@cherrypy.expose
	def index(self):
		return open("webpages/homepage.html").read()
	
	@cherrypy.expose
	def TSupdateHR(self):
		global Proc
		self.setUpdateFlag(True) #allow updating
		
		inputField = 'Heart rate'
		self.setFlags( "inputField", inputField)
		
		ans=open("webpages/HR.html").read()
		
		return ans

		while updateFlag == True:
			time.sleep(1)
		
		
		ans=open("webpages/Homepage.html").read()
		return ans

		
	@cherrypy.expose
	def TSupdateIBI(self):

		self.setUpdateFlag(True) #allow updating

		inputField = 'Inter-beat-interval'
		self.setFlags( "inputField", inputField)

		ans=open("webpages/IBI.html").read()
		return ans
		
		while updateFlag == True:
			time.sleep(1)
			
		ans= open("webpages/Homepage.html").read()
		return ans
		
		
	@cherrypy.expose
	def stopTSAdaptor (self):
		self.setUpdateFlag(False)
		ans = open('webpages/Homepage.html').read()
		return ans
	
	@cherrypy.expose
	def PPG_Plot(self):
		
		sp.call(['runPlotter.bat'])
		ans = open("webpages/PlotWS.html").read()
		return ans
		
	@cherrypy.expose
	def description(self):
		ans = open("webpages/description.html").read()
		return ans
		
	def setUpdateFlag(self, bool):
		updateFlag = str(bool)	
		self.setFlags( "updateFlag", updateFlag)
		
	def setFlags(self, flagToUpdate, flagValue):
		r = requests.put(self.WSC_url + '/setflag/' + self.doctorID + '/' + self.patientID, data = json.dumps({flagToUpdate:flagValue}))
		
		
if __name__ == '__main__':
	
	#initialization of paraneters
	global updateFlag
	global inputField
	updateFlag = True
	inputField = 'Inter-beat-interval'
	doctorID = "DOCTOR1"
	patientID = "PATIENT1"
	
	ADWS = AdaptorWebService(doctorID,patientID)
	
	Proc = sp.Popen(['runTSAdaptor1.bat'])

	cwd = os.getcwd()
	conf = {
		'global': {
				'server.socket_host': get_ip(),
				'server.socket_port':8080,
				"tools.staticfile.filename" : "/webpages/PlotWS.html"

			},
		"/img": {
				"tools.staticdir.on": True,
				"tools.staticdir.dir": "C:/Users/filip/OneDrive/torino/IoT/project/FA/codes/Adaptor/img"
			}
		}
	#"tools.staticdir.dir":  "C:/Users/filip/OneDrive/torino/IoT/project/FA/codes/Adaptor/img"
	#print ("\n\n test dir:", os.path.join(cwd,  "/Users/filip/OneDrive/torino/IoT/project/FA/codes/Adaptor/img") )
	
	cherrypy.quickstart( ADWS , '/', conf)

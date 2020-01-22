import requests
import json
import time
import datetime
import lib.GetDataFromCatalog as GDFC

conf = "data/config.json"
f = open(conf)
config = json.loads(f.read())
f.close()

# print("\nconfig loaded")
WSC_url = config["WebServiceCatalog"] #get the webservice Catalog url
# print("\nWSC_url:",WSC_url)
WSC = GDFC.GetDataFromWSCatalog(WSC_url) 
# print("WSC.WSCatalogUrl, type:   " , type(WSC.WSCatalogUrl))

catalogDevices = WSC.get_devices()
catalogMs = WSC.get_microservices()
print ("\n devices already in the Catalog" , catalogDevices)
print ("\n microservices already in the Catalog" , catalogMs)

# ------------------------------------------------------------------------
#get the device info from RaspberryPi conf file  
deviceID = config["device info"]["Photopletysmography RaspberryPi"]["deviceID"]
deviceKey, deviceValue = list(config["device info"].items())[0]
data = {deviceKey : deviceValue} #key = device Name that I gave it, to be copied as device key into Catalog

# print ("deviceKey: ", deviceKey)
# print ("deviceValue: ", deviceValue)

#put those device info on the WS Catalog
print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - "+"loading the device info to the Web Service Catalog ...")
time.sleep(2)

if deviceKey in catalogDevices:
	""" The check on the presence of the devices inside the catalog is done also here to avoid extra computational work"""
	print("device '%s' already registered" %deviceKey)
else:
	print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"- "+"Registering " + deviceKey + " as a device on WebService Home Catalog")
	r = requests.post(WSC_url+"/register/newdevice", data = json.dumps(data))
	print("The device '%s' is now registered into the Catalog" %deviceKey)

# ------------------------------------------------------------------------
#get the microservices offered info from RaspberryPi conf file  
RpiMs = config["microservices offered"]
# print ("\n\nRpiMs: ", list(RpiMs.items()))

#put those microservices info on the WS Catalog
print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - "+"loading the device microservices info to the Web Service Catalog ...")

for ms in list(RpiMs.items()):
	MsKey, MsValue = ms
	print (" \n\nUploading of %s microservice info in progress... " %MsKey )
	data = {MsKey : MsValue} # key = microservice Name that I gave it, to be copied as microservice key into Catalog

	# print ("\nMsKey: ", MsKey)
	# print ("MsValue: ", MsValue)

	if MsKey in catalogMs:
		""" The check on the presence of the microservices inside the catalog is done also here to avoid extra computational work"""
		print("microservice %s already registered" %MsKey)
	else:
		print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"- "+"Registering " + MsKey + " as a microservice on WebService Home Catalog")
		r = requests.post(WSC_url+"/register/newmicroservice", data = json.dumps(data))
		print("The microservice '%s' is now registered into the Catalog" %MsKey)

print (" \n\nUploaded Catalog:", WSC.get_all_info())

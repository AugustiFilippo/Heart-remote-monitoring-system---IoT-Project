import numpy as np
import time

class SenMLTransf():
	"""This class takes as input an array containing the lines of
	the PPG_output file from the Acquisition.py module and converts
	it into a SenML format file containing only the requested information among:
	- PPG signal samples
	- Heart beat
	- Inter beat interval (IBI)
	the Heart beat and the IBI are mediated over a second period because
	 more information is not significative
	 """
	def __init__(self,baseName,baseTime):
		self.baseName = baseName
		self.baseTime = baseTime
		self.resource = "Not defined";
		self.unit = "Not defined" #unit of measure of the selected signal to be transferred
		self.PPGSignal = []
		self.HeartRate = []
		self.IBI = []

	def createEventsArray(self, fileObject):
		#print (fileObject.read())
		lines = fileObject.readlines()
		self.lines = lines[2:-1]
		time.sleep(10)
		#insert each value into the self structure
		for line in self.lines:
			line_split = line.split('\t')
			self.PPGSignal.append(line_split[1])
			self.HeartRate.append(float(line_split[3]))
			self.IBI.append(float(line_split[2]))

		# Mediate the values of the HR and IBI over the total acquisition time
		#it isn't indeed important to have a different value of HR every second

		self.HeartRate = np.mean(self.HeartRate)
		self.IBI = np.mean(self.IBI)

	def transf(self, arrayName):
		"""arrayName can be either PPGSignal, HeartRate or IBI (inter beat interval"""
		
		# if self.times_array is None: 
			# raise NameError ("Warning: create times_array first")
			
		#unit and resource defining
		if arrayName == 'PPG signal':
			self.unit = 'nU'
			array = self.PPGSignal #set the array of interest as PPG signal
			self.resource = "Photopletysmography"
			
			#timestamps creation
			self.createTimeStamps(0,len(array))
			#events creation
			"""
			events is the array sent as a value of the key "e" inside
			the SenML dict
			"""
			events = [] #initializing the array
	
			for x in range(1,len(array)):
				"""the elements of the array are dictionaries containing
				a single sample"""
	
				events.append ({'n': self.resource, 'u': self.unit, 't': self.times_array[x], 'v': array[x] })
		
		elif arrayName == 'Heart rate':
			self.unit = 'bpm'
			array = self.HeartRate #no need to create a subdictionary because we have averaged the samples of the acquisition
			self.resource = "Heart rate"
			events = {'n': self.resource, 'u': self.unit, 't': self.baseTime , 'v': array }
				
		elif  arrayName == 'Inter-beat-interval':
			self.unit = 's'
			array = self.IBI #no need to create a subdictionary because we have averaged the samples of the acquisition
			self.resource = "Inter-beat-interval"
			events = {'n': self.resource, 'u': self.unit, 't': self.baseTime , 'v': array }
		else:
			raise NameError("Warning arrayName can be either 'PPG signal', 'Heart rate' or 'Inter-Beat-Interval' ")

		#SenML creation
		SenMLDict = {'bn' :self.baseName, 'bt': self.baseTime,  'e' :  events}
		return SenMLDict


					
	def createTimeStamps(self, t_zero, length):
		"""t_zero is the starting time"""
		#create timestamp for each line
		global fs
		fs = 125 #sapling frequency
		dt = 1/fs #inter - samples interval
		# length = len(self.lines)
		self.times_array = np.linspace (start = t_zero, stop = (t_zero +dt*(length-1)), num = length)
		#print ("times_array", times_array)




from PyQt4 import QtGui,QtCore
import time,sys

class communicationHandler(QtCore.QObject):
	sigStat = QtCore.pyqtSignal(str,bool)
	sigPlot = QtCore.pyqtSignal(object)
	sigGeneric = QtCore.pyqtSignal(str,object)
	sigError = QtCore.pyqtSignal(str,str)
	def __init__(self, parent=None,**kwargs):
		super(self.__class__, self).__init__(parent)
		self.I = kwargs.get('interface',None)
		self.I.set_sine(1000)
		self.evalGlobals = {k: getattr(self.I, k) for k in dir(self.I)}
		
		self.timer = QtCore.QTimer()
		self.buflen = 0
		self.trigPre = 0 # prescaler for trigger waiting for the oscilloscope
		self.channels_enabled=[0,0,0,0]

	@QtCore.pyqtSlot(str,object,object)
	def process(self,name,args,kwargs):
		name = str(name)
		#print (name,args,kwargs)
		try:
			if name == 'capture1':                          #blocking call . Acquire data , and immediately signal to plot
				x,y = self.I.capture1(*args,**kwargs)
				self.sigStat.emit('acquired data',False)
				self.sigPlot.emit([x,y])
			elif name == 'capture2':
				x,y,x2,y2 = self.I.capture2(*args,**kwargs)
				self.sigPlot.emit([x,y,x2,y2])
			elif name == 'capture_action':
				x,y = self.I.capture_action(*args,**kwargs)
				self.sigPlot.emit([x,y])
			elif name == 'capture_traces':	                #non - blocking call. Start acquisition , and fetch data when it's ready.
				self.I.capture_traces(*args,**kwargs)
				self.buflen = args[0]
				self.channels_enabled=kwargs.get('chans',[0,0,0,0])
				self.timer.singleShot(args[1]*args[2]*1e-3+10+self.trigPre*20,self.fetchData)
			elif name == 'fetchData':	                #non - blocking call. Start acquisition , and fetch data when it's ready.
				n=0
				try:
					while(not self.I.oscilloscope_progress()[0]):
						time.sleep(0.1)
						print ('correction required',n)
						n+=1
						if n>15:
							raise Exception

					t=time.time()
					for a in range(self.buflen):
						if self.channels_enabled[a]:
							self.I.__fetch_channel__(a+1)
					#print ('traces...ordered',time.time()-t)
					X = self.I.achans[0].get_xaxis()*1e-6
					if self.buflen==1:self.sigPlot.emit([X,self.I.achans[0].get_yaxis()])
					elif self.buflen==2:self.sigPlot.emit([X,self.I.achans[0].get_yaxis(),X,self.I.achans[1].get_yaxis()])
					elif self.buflen==3:self.sigPlot.emit([X,self.I.achans[0].get_yaxis(),X,self.I.achans[1].get_yaxis(),X,self.I.achans[2].get_yaxis()])
					elif self.buflen==4:self.sigPlot.emit([X,self.I.achans[0].get_yaxis(),X,self.I.achans[1].get_yaxis(),X,self.I.achans[2].get_yaxis(),X,self.I.achans[3].get_yaxis()])

				except Exception as e:
					self.sigError.emit('fetching : ',e.message)
			elif name == 'HX711':
				res = self.I.HX711.read(*args)
				self.sigGeneric.emit(name,res)


			else:
				if name in self.evalGlobals:
					res = self.evalGlobals[name](*args,**kwargs)
					self.sigGeneric.emit(name,res)
				else:
					self.sigError.emit(name,' : unknown function')
		except Exception as e:
			self.sigError.emit(name,e.message)

	def fetchData(self):
			self.process('fetchData',[],{})

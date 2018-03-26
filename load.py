# -*- coding: utf-8 -*-
import sys
import re
import ttk
import Tkinter as tk
import requests
import os
import csv
import uuid
from urllib import quote_plus
from  math import sqrt,pow,trunc
from ttkHyperlinkLabel import HyperlinkLabel
import datetime
import webbrowser
import threading


from config import applongname, appversion
import myNotebook as nb
from config import config
import csv

this = sys.modules[__name__]
this.s = None
this.prep = {}
this.debuglevel=1
this.version="4.1.0"

window=tk.Tk()
window.withdraw()

# Lets capture the plugin name we want the name - "EDMC -"
myPlugin = "USS Survey"


class Reporter(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload = payload

    def run(self):
        try:
            requests.get(self.payload)
            debug(self.payload)
        except:
            print("["+myPlugin+"] Issue posting message " + str(sys.exc_info()[0]))

class ussSelect:

	def __init__(self,frame):
		debug("Initiating USS Select")
		self.frame=frame
		UssTypes = [
			"Ceremonial Comms",
			"Combat Aftermath",
			"Convoy Dispersal",
			"Degraded Emissions",
			"Distress Call",
			"Encoded Emissions",
			"High Grade Emissions",
			"Mission Target",
			"Non Human Signal",
			"Trading Beacon",
			"Weapons Fire"
		]
		self._IMG_VISITED = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'/tick3.gif')
		
		listbar = tk.Frame(frame)
		self.container=listbar
		listbar.grid(row = 6, column = 0,columnspan=2)
		self.system="Test"
		self.usstime="Test"
		
		
		self.typeVar = tk.StringVar(listbar)
		self.typeVar.set(UssTypes[8]) # default value
		popupTypes = tk.OptionMenu(listbar, self.typeVar, *UssTypes)
		self.typeVar.trace('w', self.changeType)
		popupTypes.grid(row = 0, column = 0)
		
		self.Threats = [
			"Threat 0",
			"Threat 1",
			"Threat 2",
			"Threat 3",
			"Threat 4",			
			"Threat 5",			
			"Threat 6",
			"Threat 7",
			"Threat 8",
			"Threat 9",			
		]
		
		self.threatVar = tk.StringVar(listbar)
		self.threatVar.set(self.Threats[0]) # default value
		popupThreats = tk.OptionMenu(listbar, self.threatVar, *self.Threats)
		
		popupThreats.grid(row = 0, column = 1)
		transmit = tk.Button(listbar, anchor=tk.W, image=this._IMG_VISITED, command=self.transmit)
		transmit.grid(row = 0, column = 2)
		self.container.grid_remove()
		
	def transmit(self):
		debug(self.typeVar.get())
		debug(self.threatVar.get())
		self.submitTime=datetime.datetime.now()
		d=self.submitTime-self.cruiseTime
		self.deltaSeconds=d.seconds
		url=self.getUrl()
		Reporter(url).start()
		
	def getUrl(self):
		url="https://docs.google.com/forms/d/e/1FAIpQLSeOBbUTiD64FyyzkIeZfO5UMfqeuU2lsRf3_Ulh7APddd91JA/formResponse?usp=pp_url"
		url+="&entry.306505776="+self.system
		url+="&entry.167750222="+self.cruiseStamp
		url+="&entry.1559250350="+self.typeVar.get()
		url+="&entry.1031843658="+self.threatVar.get()[7]
		url+="&entry.1519036101="+self.cmdr
		url+="&entry.1328849583="+str(self.deltaSeconds)
		
		return url
		
	def changeType(self,*args):
		sel = self.typeVar.get();
		if sel == "Ceremonial Comms":
			self.threatVar.set(self.Threats[0]) # default value
		if sel == "Combat Aftermath":
			self.threatVar.set(self.Threats[0]) # default value
		if sel == "Convoy Dispersal":
			self.threatVar.set(self.Threats[3]) # default value
		if sel == "Degraded Emissions":
			self.threatVar.set(self.Threats[0]) # default value
		if sel == "Distress Call":
			self.threatVar.set(self.Threats[2]) # default value
		if sel == "Encoded Emissions":
			self.threatVar.set(self.Threats[0]) # default value
		if sel == "High Grade Emissions":
			self.threatVar.set(self.Threats[0]) # default value
		if sel == "Mission Target":
			self.threatVar.set(self.Threats[3]) # default value
		if sel == "Non Human Signal":
			self.threatVar.set(self.Threats[5]) # default value			
		if sel == "Trading Beacon":
			self.threatVar.set(self.Threats[1]) # default value
		if sel == "Weapons Fire":			
			self.threatVar.set(self.Threats[1]) # default value		

	def journal_entry(self,cmdr, system, station, entry):
		self.system=system
		self.cmdr=cmdr
		if entry['event'] == "SupercruiseEntry" or entry['event'] == "FSDJump":
			self.container.grid()
			self.cruiseTime=datetime.datetime.now()
			ts=entry["timestamp"][0:-1]
			timestamp=str(ts[0:3])+"/"/+str(ts[5:6])+"/"+str(ts[8:9])+" "+ts[11:18]
			self.cruiseStamp=timestamp
		if entry['event'] == "SupercruiseExit":
			self.container.grid_remove()		
			
class CanonnReport:

	def __init__(self,label):
		debug("Initiating Cannon Report")
		
		self.label=label
		self.threat=0
		self.probe=0
		self.sensor=0
		self.scout=0
		self.cyclops=0
		self.basilisk=0
		self.medusa=0
		self.cobra=0
		
	def setThreat(self,threat):
		self.threat=threat
		self.setReport()
				
	def incProbe(self):
		self.probe+=1
		self.setReport()
		
	def incCobra(self):
		self.cobra+=1
		self.setReport()		
				
	def incSensor(self):
		self.sensor+=1
		self.setReport()
		
	def incScout(self):
		self.scout+=1		
		self.setReport()
		
	def incCyclops(self):
		self.cyclops+=1		
		self.setReport()
		
	def incBasilisk(self):
		self.basilisk+=1		
		self.setReport()
		
	def incMedusa(self):
		self.medusa+=1	
		self.setReport()
		
	def setSpace(self):
		self.probe=0
		self.sensor=0
		self.scout=0
		self.cyclops=0
		self.basilisk=0
		self.medusa=0
		self.cobra=0
		self.setReport()
		
	def hyperLink(self,event):
		url=self.getUrl("viewform")
		webbrowser.open(url)
		self.hide()
		
	def getThings(self,report,thing,quantity):
		if quantity==1:
			return report+" 1 "+thing
		if quantity > 1:
			return report+" "+str(quantity)+" "+thing+"s"
		return report
		
	def hide(self):
		this.BASILISK.grid_remove()
		this.CYCLOPS.grid_remove()
		this.MEDUSA.grid_remove()
		this.PROBE.grid_remove()
		this.SCOUT.grid_remove()
		this.SENSOR.grid_remove()
		this.SPACE.grid_remove()
		this.TRANSMIT.grid_remove()
		this.COBRA.grid_remove()
		this.canonnReportDesc.grid_remove()
		
	def transmit(self):
		debug("Transmitting",2)
		url=self.getUrl("formResponse")
		Reporter(url).start()
		self.hide()
		
	def ussDrop(self,cmdr, system, station, entry):
		if entry['USSType'] == "$USS_Type_NonHuman;":
			self.uss_type=entry['USSType']
			self.threat=str(entry['USSThreat'])		
			self.system=system
			self.commander=cmdr
			self.setSpace()
			this.BASILISK.grid()
			this.CYCLOPS.grid()
			this.MEDUSA.grid()
			this.PROBE.grid()
			this.SCOUT.grid()
			this.SENSOR.grid()
			this.SPACE.grid()
			this.TRANSMIT.grid()
			this.COBRA.grid()
			this.canonnReportDesc.grid()			
	
	
	def getUrl(self,action):
		url="https://docs.google.com/forms/d/e/1FAIpQLSdspuO9LP1byQFx4oeMNq9FT4eo34mgqpQTo-6oYZOXoX0PtA/"+action+"?usp=pp_url"
		url+="&entry.1699877803="+quote_plus(self.commander)
		url+="&entry.758432443="+quote_plus(self.system)
		url+="&entry.740257661="+str(self.threat)
		url+="&entry.1192850048="+str(self.probe)
		url+="&entry.500127414="+str(self.sensor)
		url+="&entry.639490147="+str(self.scout)
		url+="&entry.265020225="+str(self.cyclops)
		url+="&entry.598670618="+str(self.basilisk)
		url+="&entry.950835942="+str(self.medusa)	
		url+="&entry.1268549011="+str(self.cobra)
		url+="&entry.1201289190=No"
		url+="&entry.1758654357="+str(this.guid)+"&submit=Submit"
		return url
		#&entry.671628463=self.hostile
		#&entry.1276226296=self.description
		#&entry.1201289190=self.scanned
		#&entry.2069330363=self.core
		#&entry.2082917464=self.inner
		#&entry.1904732354=self.outer
		#&entry.1121979243=self.image
		
	
	def setReport(self):
		self.report="Threat "+str(self.threat)+":"
		self.report=self.getThings(self.report,"probe",self.probe)
		self.report=self.getThings(self.report,"sensor",self.sensor)
		self.report=self.getThings(self.report,"scout",self.scout)
		self.report=self.getThings(self.report,"cyclops",self.cyclops)
		self.report=self.getThings(self.report,"basilisk",self.basilisk)
		self.report=self.getThings(self.report,"medusa",self.medusa)
		self.report=self.getThings(self.report,"human ship",self.cobra)
		if self.probe+self.sensor+self.scout+self.cyclops+self.basilisk+self.medusa+self.cobra == 0:
			self.report=self.report+" click icons to report thargoids"
		self.label["text"]=self.report
		self.label["url"]=self.getUrl("viewform")
		
		
		
class PlanetaryScan:
	
	# we want to split the planet surface into searchable sections
	# flight time should be around 10 minutes to cover a section. 
	# Assume 300m/s speed
	# 200km will take around 8-12 minutes to survey depending on speed. A nice round number
	# Merope 5C Radius = 1,478 km 
	# Merope 5C Circumference = 9,286.54 km 
	# sections around circumference  = 46
	# Total sections.. 46x23?
	# pole = 1 section
	# 
	
	def __init__(self,frame):
		debug("Initiating USS Detector")
		
	def SupercruiseExit(self,cmdr, system, station, entry):
		debug("We have exit near a body")
		#{ "timestamp":"2016-06-10T14:32:03Z", "event":"SupercruiseExit", "StarSystem":"Yuetu", "Body":"Yuetu B", "BodyType: "Planet"}
		#if we are at a planet let us find out if it is landable

class USSDetector:
	'Class for Detecting USS Drops'

	def __init__(self,frame):
		debug("Initiating USS Detector")
		self.frame=frame
		self.uss = False
		today=datetime.datetime.now()
		self.arrival=today.strftime("%Y/%m/%d %H:%M:%S")
		## we might start in system and so never have jumped
		self.jumped=False

	def Location(self,cmdr, system, station, entry):		
		self.arrival=entry["timestamp"].replace("T"," ").replace("-","/").replace("Z","")
		self.sysx=entry["StarPos"][0]
		self.sysy=entry["StarPos"][1]
		self.sysz=entry["StarPos"][2]
		# need to set this so we know we have coordinates available
		self.jumped=True
		
	def FSDJump(self,cmdr, system, station, entry):
		self.arrival=entry["timestamp"].replace("T"," ").replace("-","/").replace("Z","")
		self.sysx=entry["StarPos"][0]
		self.sysy=entry["StarPos"][1]
		self.sysz=entry["StarPos"][2]
		# need to set this so we know we have coordinates available
		self.jumped=True
	  
	def ussDrop(self,cmdr, system, station, entry):
		debug("USS Drop",2)
		self.uss=True
		self.usstype=entry['USSType']
		self.usslocal=entry['USSType_Localised']
		self.threat=str(entry['USSThreat'])

			
	def SupercruiseExit(self,cmdr, system, station, entry):
		if self.uss:
			#This is a USS drop set back to false
			self.uss=False
						
			if self.jumped == False:
				self.sysx,self.sysy,self.sysz=edsmGetSystem(system)
				
				
			dmerope=getDistanceMerope(self.sysx,self.sysy,self.sysz)
			dsol=getDistanceSol(self.sysx,self.sysy,self.sysz)
			self.timestamp=entry["timestamp"].replace("T"," ").replace("-","/").replace("Z","")
			
			# lets calculate how long it too before you saw that USS
			minutes=dateDiffMinutes(self.arrival,self.timestamp)
			debug("Minutes before USS = "+str(minutes),2)
								
			url = "https://docs.google.com/forms/d/e/1FAIpQLScVk2LW6EkIW3hL8EhuLVI5j7jQ1ZmsYCLRxgCZlpHiN8JdcA/formResponse?usp=pp_url&entry.1236915632="+str(this.guid)+"&entry.106150081="+cmdr+"&entry.582675236="+quote_plus(entry['StarSystem'])+"&entry.158339236="+str(self.sysx)+"&entry.608639155="+str(self.sysy)+"&entry.1737639503="+str(self.sysz)+"&entry.413701316="+quote_plus(entry['Body'])+"&entry.1398738264="+str(dsol)+"&entry.922392846="+str(dmerope)+"&entry.218543806="+quote_plus(self.usstype)+"&entry.455413428="+quote_plus(self.usslocal)+"&entry.790504343="+quote_plus(self.threat)+"&submit=Submit"
			#print url
			Reporter(url).start()
			
			
				
class HyperdictionDetector:		
	'Class for Detecting Hyperdictions'

	def __init__(self,frame):
		debug("Initiating Hyperdiction Detector")
		self.frame=frame
		today=datetime.datetime.now()
		self.arrival=today.strftime("%Y/%m/%d %H:%M:%S")
      
	def StartJump(self,cmdr, system, station, entry):
		debug("Starting Jump",2)
		self.start_jump = system
		self.target_jump = entry["StarSystem"]
		self.station = station
		self.timestamp = entry["timestamp"].replace("T"," ").replace("-","/").replace("Z","")
		self.cmdr=cmdr
		

	def FSDJump(self,cmdr, system, station, entry):
		self.end_jump = entry["StarSystem"]
		self.cmdr=cmdr
		if self.target_jump != self.end_jump:
			debug("Hyperdiction Detected",2)	
			startx,starty,startz=edsmGetSystem(self.start_jump) 
			endx,endy,endz=edsmGetSystem(self.target_jump) 
			startmerope=getDistanceMerope(startx,starty,startz)
			endmerope=getDistanceMerope(endx,endy,endz)
			debug("Hyperdiction detected("+self.end_jump+","+self.start_jump+","+self.target_jump+")",2)
			url = "https://docs.google.com/forms/d/e/1FAIpQLSfDFsZiD1btBXSHOlw2rNK5wPbdX8fF7JBCtiflX8jPgJ-OqA/formResponse?usp=pp_url&entry.1282398650="+str(guid)+"&entry.2105897249="+quote_plus(cmdr)+"&entry.448120794="+quote_plus(self.start_jump)+"&entry.1108314590="+str(startx)+"&entry.1352373541="+str(starty)+"&entry.440246589="+str(startz)+"&entry.163179951="+quote_plus(self.target_jump)+"&entry.549665465="+str(endx)+"&entry.1631305292="+str(endy)+"&entry.674481857="+str(endz)+"&entry.1752982672="+str(startmerope)+"&entry.659677957="+str(endmerope)+"&submit=Submit"
			#print url
			Reporter(url).start()
			setHyperReport(self.start_jump,self.target_jump)

class news:
	def __init__(self,frame):
		debug("Initiating News")
		self.feed_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vSy9ij93j2qbwD-1_bXlI5IfO4EUD4ozNX2GJ2Do5tZNl-udWIqBHxYbtmcMRwvF6favzay3zY2LpH5/pub?gid=1876886084&single=true&output=tsv"
		self.version_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vSy9ij93j2qbwD-1_bXlI5IfO4EUD4ozNX2GJ2Do5tZNl-udWIqBHxYbtmcMRwvF6favzay3zY2LpH5/pub?gid=0&single=true&output=tsv"
		this.description = tk.Message(frame,width=200)
		this.news_label = tk.Label(frame, text=  "Report:")
		this.newsitem= HyperlinkLabel(frame, compound=tk.LEFT, popup_copy = True)
		this.news_label.grid(row = 3, column = 0, sticky=tk.W)
		this.newsitem.grid(row = 3, column = 1, columnspan=3, sticky=tk.W)	
		this.newsitem["text"]= "News"
		this.news_label["text"]= "News"
		this.newsitem.grid_remove()
		this.news_label.grid_remove()
		self.getPost()
		
	
			
		
	def getPost(self):
		
		versions = requests.get(self.version_url)	
		
		getnews=True
		for line in versions.content.split("\r\n"):
			rec=line.split("\t")
			if rec[0] == 'EDMC-USS-Survey' and rec[1] != this.version:
				this.newsitem["text"] = "Please upgrade USS Survey to release; "+rec[1]
				this.newsitem["url"] = rec[2]
				this.newsitem.grid()	
				this.news_label.grid()
				getnews=False
				
		
		if getnews:
			feed = requests.get(self.feed_url)		
			debug(feed.content,2)
			lines=feed.content.split("\r\n")
			## only want most recent news item
			line=lines[1]
			rec=line.split("\t")
			this.newsitem["text"] = rec[2]
			this.newsitem["url"] = rec[1]
			this.newsitem.grid()	
			this.news_label.grid()
		
			
class Patrol:
	def __init__(self,frame):
		debug("Initiating Patrol")
		self.frame=frame
		today=datetime.datetime.now()
		
		self.arrival=today.strftime("%Y/%m/%d %H:%M:%S")
		debug(self.arrival,2)
		
	def Location(self,cmdr, system, station, entry):		
		self.cmdr=cmdr
		debug("Setting Location",2)
		self.system = { "x": entry["StarPos"][0], "y": entry["StarPos"][1], "z": entry["StarPos"][2], "name": entry["StarSystem"] }			
		self.body = entry["Body"]
		self.body_type = entry["BodyType"]
		self.showPatrol(cmdr)
	
	def FSDJump(self,cmdr, system, station, entry):
		self.cmdr=cmdr
		debug("Patrol Setting Location",2)
		self.body = ""
		self.body_type = ""
		self.system = { "x": entry["StarPos"][0], "y": entry["StarPos"][1], "z": entry["StarPos"][2], "name": entry["StarSystem"] }		
		self.arrival = entry["timestamp"].replace("T"," ").replace("-","/").replace("Z","")
		self.showPatrol(cmdr)
		
		
				
	def SupercruiseExit(self,cmdr, system, station, entry):
		self.cmdr=cmdr
		self.body = entry["Body"]
		self.body_type = entry["BodyType"]
		## system should already be set so no need to set it again
		
	def cmdrData(self,data):
		debug(data,2)
		x,y,z = edsmGetSystem(data["lastSystem"]["name"])
		self.system = { "x": x, "y": y, "z": z, "name": data["lastSystem"]["name"] }	
		debug(self.system,2)
		self.showPatrol(data["commander"]["name"])
		
	
		
	def showPatrol(self,cmdr):
		merge_visited()
		self.cmdr=cmdr
		nearest,distance,instructions,visits,x,y,z = findNearest(self.system,this.patrol)
		setPatrol(nearest,distance,instructions)
		self.nearest=nearest
		this.clip=nearest
		debug("setting clip",2)
		debug(this.clip,2)
		if distance == 0:
			setPatrolReport(cmdr,self.system["name"])
			
	def exitPoll(self,event):
		debug("exitPoll",2)
		instance=this.patrol[self.nearest]["instance"]
		#https://docs.google.com/forms/d/e/1FAIpQLSeK8nTeHfR7V1pYsr1dlFObwQ-BVXE1DvyCHqNNaTglLDW6bw/viewform?usp=pp_url&entry.1270833859=CMDR&entry.841171500=INSTANCE&entry.813177329=SYSTEM&entry.1723656810=ARRIVAL&entry.1218635359=Yes&entry.430344938=Maybe&entry.514733933=No
		url="https://docs.google.com/forms/d/e/1FAIpQLSeK8nTeHfR7V1pYsr1dlFObwQ-BVXE1DvyCHqNNaTglLDW6bw/viewform?usp=pp_url&entry.813177329="+quote_plus(self.nearest)+"&entry.1723656810="+self.arrival+"&entry.1218635359=Maybe&entry.514733933=Yes&entry.430344938=No&entry.1270833859="+quote_plus(self.cmdr)+"&entry.841171500="+quote_plus(instance)
		webbrowser.open(url)
		this.patrol[self.nearest]["visits"]+=1
		self.showPatrol(self.cmdr)
		
	def startUp(self,cmdr, system, station, entry):
		self.arrival = entry["timestamp"].replace("T"," ").replace("-","/").replace("Z","")
		x,y,z = edsmGetSystem(system)
		self.system = { "x": x, "y": y, "z": z, "name": system }	
		self.showPatrol(cmdr)		
			
		
class meropeLog:
	def __init__(self,frame):
		debug("Initiating Merope Log")
		
	def FSDJump(self,cmdr, system, station, entry):
		x = entry["StarPos"][0]
		y = entry["StarPos"][1]
		z = entry["StarPos"][2]
		 
		if getDistanceMerope(x,y,z) <= 200:
			url="https://docs.google.com/forms/d/e/1FAIpQLSeqLdzXzubMFicyDzDvSN6YIwFW9Txx71d1asGiAIt23j6vKQ/formResponse?usp=pp_url&entry.1604333823="+quote_plus(system)+"&entry.939851024="+str(x)+"&entry.1593775066="+str(y)+"+&entry.1149646403="+str(z)
			Reporter(url).start()

			
def dateDiffMinutes(s1,s2):
	format="%Y/%m/%d %H:%M:%S"
	d1=datetime.datetime.strptime(s1,format) 
	d2=datetime.datetime.strptime(s2,format)
	
	return (d2-d1).days	*24 *60
		
def debug(value,level=None):
	if level is None:
		level = 1
	if this.debuglevel >= level:
		print "["+myPlugin+"] "+str(value)


def getDistance(x1,y1,z1,x2,y2,z2):
	debug(x1,2)
	debug(y1,2)
	debug(z1,2)
	debug(x2,2)
	debug(y2,2)
	debug(z2,2)
	return round(sqrt(pow(float(x2)-float(x1),2)+pow(float(y2)-float(y1),2)+pow(float(z2)-float(z1),2)),2)
	
def get_patrol():
	url="https://docs.google.com/spreadsheets/d/e/2PACX-1vQLtReZQbaSyNf8kFZlexFFQqpBzSGNiCr2DeidufZAFrYRertXI_q0AfJscZrTe1x8TkfRu0BhlUck/pub?gid=222743727&single=true&output=tsv"
	r = requests.get(url)
	#print r.content
	list={}
	
	for line in r.content.split("\n"):
		a = []
		a = line.split("\t")

		try:
			instance=a[0]
			system = a[1]
			x = a[2]
			y = a[3]
			z = a[4]
			instructions = a[5]
			if system != "System":
				list[system]={ "x": x, "y": y, "z": z, "instructions": instructions, "priority": 0, "visits": 0, "instance": instance }
		except:
			debug(a,2)

	return list

	

def merge_visited():
	url="https://docs.google.com/spreadsheets/d/e/2PACX-1vQS_KlvwvoGlEEUOvGpc8dwVo4ViOs1x8NJsVeMOvjfAe-xsJyT0ErBFLipMYPWIaTk8By2Zy26T8_l/pub?gid=159395757&single=true&output=tsv"
	r = requests.get(url)
	#print r.content
	failed=0
	
	for line in r.content.split("\r\n"):
		sline = []
		sline= line.split("\t")
		
		system=sline[1]
		objective=sline[2]
		remove=sline[5]
		commander=sline[6]
		
		#debug(sline)
		#debug(system)
		#debug(objective)
		
		
		try:
			if system != "System":
				if objective=="Yes":
					this.patrol[system]["visits"]+=2
					#debug(system+" obj: yes")
				if objective=="Maybe":
					this.patrol[system]["visits"]+=1					
					#debug(system+" obj Maybe")
			if system != "System" and commander == this.cmdr and remove == "Yes":			
				#need to work on removal. In the meantime lets make it low priority
				this.patrol[system]["visits"]+=10					
				#debug(system+" obj Forget")
				
		except:
			failed += 1
			#print "failed "+ system

	debug(str(failed) + " visited systems not in patrol list",2)
	#debug(this.patrol)
	return list	
	
		
def plugin_start():
	"""
	Load Template plugin into EDMC
	"""
	
	#Load Images we intend to use
	this._IMG_VISITED = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'/tick3.gif')
	this._IMG_IGNORE = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'/cross.gif')
	this._IMG_CLIPBOARD = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'/clipboard.gif')
	this._IMG_BASILISK = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Basilisk_25px.gif')
	this._IMG_CYCLOPS = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Cyclops_25px.gif')
	this._IMG_MEDUSA = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Medusa_25px.gif')
	this._IMG_PROBE = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Probe_25px.gif')
	this._IMG_SCOUT = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Scout_25px_1.gif')
	this._IMG_SENSOR = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Sensor_25px.gif')
	this._IMG_SPACE = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\LCU_Space_25px.gif')
	this._IMG_TRANSMIT = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\\transmit.gif')
	this._IMG_COBRA = tk.PhotoImage(file = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))+'\Icons\\cobra.gif')	
	
	this.patrol=get_patrol()
	merge_visited()
	
	#print this.patrol
	return myPlugin
	
def copy_patrol_to_clipboard(event):
	window.clipboard_clear()  # clear clipboard contents
	window.clipboard_append(this.clip)  	
		

	
def plugin_app(parent):

	this.parent = parent
	#create a new frame as a containier for the status
	
	
	
	this.frame = tk.Frame(parent)
	
	this.ussSelector = ussSelect(this.frame)
	this.buttonbar = tk.Frame(this.frame)
	#We want three columns, label, text, button
	this.frame.columnconfigure(5, weight=1)
	this.buttonbar.columnconfigure(7, weight=1)
	this.buttonbar.grid(row = 4, column = 0, columnspan=5, sticky=tk.W)

	#this.canonnReportDesc = tk.Message(this.frame,width=200)
	#this.canonnReportDesc = tk.Label(this.frame,wraplength=200)
	this.canonnReportDesc = HyperlinkLabel(this.frame,wraplength=200,popup_copy = False)
	this.canonnReportDesc.grid(row = 5, column = 0, columnspan=4, sticky=tk.W)
	this.canonnReport=CanonnReport(canonnReportDesc);	
	this.canonnReportDesc.bind("<Button-1>", this.canonnReport.hyperLink)  
	
	this.ussInator = USSDetector(frame)
	this.hyperdictionInator = HyperdictionDetector(frame)
	this.patrolZone = Patrol(frame)
	this.newsFeed = news(frame)
	this.meropeLog = meropeLog(frame)
	
	# maybe we want to be able to change the labels?
	this.label = tk.Label(this.frame, text=  "Patrol:")
	#this.status = tk.Label(this.frame, anchor=tk.W, text="Getting current location")
	this.status = HyperlinkLabel(this.frame, compound=tk.RIGHT, popup_copy = True)
	this.status["url"] = None
	
	this.system = HyperlinkLabel(this.frame, compound=tk.RIGHT, popup_copy = True)
	this.clipboard = tk.Label(this.frame, anchor=tk.W, image=this._IMG_CLIPBOARD)
	this.cross = tk.Label(this.frame, anchor=tk.W, image=this._IMG_IGNORE)
	
	#tk.text_widget.window_create("insert", window=image_link)
	
	
	this.BASILISK = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_BASILISK, command=canonnReport.incBasilisk)
	this.CYCLOPS = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_CYCLOPS, command=canonnReport.incCyclops)
	this.MEDUSA = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_MEDUSA, command=canonnReport.incMedusa)
	this.PROBE = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_PROBE, command=canonnReport.incProbe)
	this.SCOUT = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_SCOUT, command=canonnReport.incScout)
	this.SENSOR = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_SENSOR, command=canonnReport.incSensor)
	this.SPACE = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_SPACE, command=canonnReport.setSpace)
	this.COBRA = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_COBRA, command=canonnReport.incCobra)
	this.TRANSMIT = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_VISITED, command=canonnReport.transmit)
	
	

	
	this.SPACE.grid(row = 0, column = 0, sticky=tk.W)
	this.PROBE.grid(row = 0, column = 1, sticky=tk.W)
	this.SENSOR.grid(row = 0, column = 2, sticky=tk.W)	
	this.SCOUT.grid(row = 0, column = 3, sticky=tk.W)
	this.CYCLOPS.grid(row = 0, column = 4, sticky=tk.W)
	this.BASILISK.grid(row = 0, column = 5, sticky=tk.W)
	this.MEDUSA.grid(row = 0, column = 6, sticky=tk.W)
	this.COBRA.grid(row = 0, column = 7, sticky=tk.W)
	this.TRANSMIT.grid(row = 0, column = 8, sticky=tk.W)
	
	this.BASILISK.grid_remove()
	this.CYCLOPS.grid_remove()
	this.MEDUSA.grid_remove()
	this.PROBE.grid_remove()
	this.SCOUT.grid_remove()
	this.SENSOR.grid_remove()
	this.SPACE.grid_remove()
	this.TRANSMIT.grid_remove()
	this.COBRA.grid_remove()
	this.canonnReportDesc.grid_remove()
	
	this.clipboard.bind("<Button-1>", copy_patrol_to_clipboard)  
	
	this.description = tk.Message(this.frame,width=200)
	this.report_label = tk.Label(this.frame, text=  "Report:")
	this.report= HyperlinkLabel(this.frame, compound=tk.RIGHT, popup_copy = True)
	this.report["text"]= None
	this.status["url"] = None
	
	this.label.grid(row = 0, column = 0, sticky=tk.W)
	this.status.grid(row = 0, column = 1, sticky=tk.W)
	this.clipboard.grid(row = 0, column = 2, sticky=tk.W)
#	this.tick.grid(row = 0, column = 3, sticky=tk.W)
	this.cross.grid(row = 0, column = 3, sticky=tk.W)
	this.report_label.grid(row = 2, column = 0, sticky=tk.W)
	this.report.grid(row = 2, column = 1, columnspan=3, sticky=tk.W)
	this.description.grid(row = 1, column = 0, columnspan=4, sticky=tk.W)
	
	this.label.grid_remove()
	this.status.grid_remove()
	this.clipboard.grid_remove()
#	this.tick.grid_remove()
	this.cross.grid_remove()
	this.description.grid_remove()
	this.report.grid_remove()
	this.report_label.grid_remove()
	this.cross.bind("<Button-1>", this.patrolZone.exitPoll)  
	#label.grid(row = 1, column = 0, sticky=tk.W)
	#this.status.grid(row = 1, column = 1, sticky=tk.W)
	#this.icon.pack(side=RIGHT)
	return this.frame

def findNearest(jumpsystem,list):
	#print list
	nearest	= { 'distance': 999999, 'name': "No Systems to Patrol" } 
	n=999999
	p=999999
	for key,value in list.iteritems():
		#print str(n) +  ">"  + str(sysrec['distance'])
		d = getDistance(jumpsystem["x"],jumpsystem["y"],jumpsystem["z"],value["x"],value["y"],value["z"])
		#print key+" "+str(d)+" "+str(value["priority"])
		lower_priority=int(value["visits"]) < int(p)
		closer=float(d) < float(n) and int(value["visits"]) == int(p)
		if  lower_priority or closer:			
			try:
				n = d
				p = int(value["visits"])
				nearest=key
					#print "try: "+key+" "+str(n)+" "+str(p)
			except:
				debug(exception)
					
	if n == 999999:
		return None,None,None,None,None,None,None,None,None,None,None
	
	return nearest,n,list[nearest]["instructions"],list[nearest]["visits"],list[nearest]["x"],list[nearest]["y"],list[nearest]["z"]

def edsmGetSystem(system):
	url = 'https://www.edsm.net/api-v1/system?systemName='+quote_plus(system)+'&showCoordinates=1'		
	#print url
	r = requests.get(url)
	s =  r.json()
	#print s
	return s["coords"]["x"],s["coords"]["y"],s["coords"]["z"]

def getDistanceMerope(x1,y1,z1):
	return round(sqrt(pow(float(-78.59375)-float(x1),2)+pow(float( -149.625)-float(y1),2)+pow(float(-340.53125)-float(z1),2)),2)		
	
def getDistanceSol(x1,y1,z1):
	return round(sqrt(pow(float(0)-float(x1),2)+pow(float(0)-float(y1),2)+pow(float(0)-float(z1),2)),2)			
		

		
	
# Detect journal events
def journal_entry(cmdr, system, station, entry):

	this.guid = uuid.uuid1()
	this.cmdr=cmdr
	  
	this.ussSelector.journal_entry(cmdr, system, station, entry)
	  
	if entry['event'] == 'USSDrop':
		this.ussInator.ussDrop(cmdr, system, station, entry)
		this.canonnReport.ussDrop(cmdr, system, station, entry)
		
	if entry['event'] == 'SupercruiseExit':
		# we need to check if we dropped from a uss
		this.ussInator.SupercruiseExit(cmdr, system, station, entry)		
	
	if entry['event'] == 'StartJump':	
		this.newsFeed.getPost()  
		
	if entry['event'] == 'StartJump' and entry['JumpType'] == 'Hyperspace':
			
		debug("StartJump Hyperspace")
		debug(entry,2)
		
		this.hyperdictionInator.StartJump(cmdr, system, station, entry)
						
		#patrol_start_jump(cmdr,this.arrived,entry["timestamp"],system,entry["StarSystem"])
				
	
	if entry['event'] == 'FSDJump':
		
		debug("FSDJump")
		debug(entry,2)
			
		this.ussInator.FSDJump(cmdr, system, station, entry)
		this.hyperdictionInator.FSDJump(cmdr, system, station, entry)	
		this.patrolZone.FSDJump(cmdr, system, station, entry)
		this.meropeLog.FSDJump(cmdr, system, station, entry)
	
	if entry['event'] == 'Location':
		this.patrolZone.Location(cmdr, system, station, entry)
		
	if entry['event'] == 'StartUp':
		this.patrolZone.startUp(cmdr, system, station, entry)		

def setPatrolReport(cmdr,system):
	debug("Patrol Report Disabled")
	#this.report_label["text"] = "Patrol Report"
	#this.report["text"] = "Unknown report "+system
	#https://docs.google.com/forms/d/e/1FAIpQLSeWVPRUXbofwFho5kTqd9_YUzLu2Tv3iz58jccobYohLV2nlA/viewform?entry.391050800=LCU%20No%20Fool&entry.1859995282=SYSTEM&entry.2075217736=BODY&entry.578283301=LATLON
	#this.report["url"] = "https://docs.google.com/forms/d/e/1FAIpQLSeWVPRUXbofwFho5kTqd9_YUzLu2Tv3iz58jccobYohLV2nlA/viewform?entry.391050800="+quote_plus(cmdr)+"&entry.1859995282="+quote_plus(system)
	#this.report_label.grid()
	#this.report.grid()
			
def setHyperReport(sysfrom,systo):
	this.report_label["text"] = "Hyperdiction"
	this.report["text"] = "Report to Canonn"
	this.report["url"] = "https://docs.google.com/forms/d/e/1FAIpQLSeQyYdpD79L7v0qL6JH09cfPZw_7QJ_3d526jweaS92VmK-ZQ/viewform?usp=pp_url&entry.1593923043="+quote_plus(sysfrom)+"&entry.1532195316="+quote_plus(systo)+"&entry.1157975236="+str(this.guid)
	this.report_label.grid()
	this.report.grid()			
	
		
			
def setPatrol(nearest,distance,instructions):

	
	if nearest == None:
		this.status['text'] = "No patrol at this time" 
		this.status['url'] = None
		this.clipboard.grid_remove()
		this.description.grid_remove()
	else:
		this.status['text'] = nearest + " (" + str(distance) +"ly)"
		this.status['url'] = 'https://www.edsm.net/show-system?systemName=%s' % quote_plus(nearest)
		
		this.description["text"] = instructions
		this.label.grid()
		this.status.grid()
		this.clipboard.grid()
		this.cross.grid()
		this.description["width"]=100
		this.description["width"]=this.parent.winfo_width()-10
		this.description.grid()
			
def cmdr_data(data):
	this.patrolZone.cmdrData(data)
	
def plugin_stop():
	debug("Destroying Clipboard",3)
	window.destroy()
	
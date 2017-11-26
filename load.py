# -*- coding: utf-8 -*-
import sys
import re
import ttk
import Tkinter as tk
import requests
import os
import uuid
from urllib import quote_plus
from  math import sqrt,pow,trunc
from ttkHyperlinkLabel import HyperlinkLabel
import datetime
import webbrowser


from config import applongname, appversion
import myNotebook as nb
from config import config
import csv

this = sys.modules[__name__]
this.s = None
this.prep = {}
this.debuglevel=1

window=tk.Tk()
window.withdraw()

# Lets capture the plugin name we want the name - "EDMC -"
myPlugin = "USS Survey"

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
			r = requests.get(url)	
			debug(r,2)
			if self.usstype == "$USS_Type_NonHuman;":
				setUssReport(system,self.threat,entry["timestamp"])
				
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
		self.end_jump = system
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
			r = requests.get(url)	
			setHyperReport(self.start_jump,self.target_jump)

class news:
	def __init__(self,frame):
		debug("Initiating News")
		self.feed_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vTT7azBCL7FxjSEy1RBw52u1o3FXdQGIIpTlq1K1hMt5OHmDzJ_9Kjx3R952I9RrDWFC0NwHUPDlC9s/pub?gid=0&single=true&output=tsv"
		this.description = tk.Message(frame,width=200)
		this.news_label = tk.Label(frame, text=  "Report:")
		this.newsitem= HyperlinkLabel(frame, compound=tk.RIGHT, popup_copy = True)
		this.news_label.grid(row = 3, column = 0, sticky=tk.W)
		this.newsitem.grid(row = 3, column = 1, columnspan=3, sticky=tk.W)	
		this.newsitem["text"]= None
		this.newsitem.grid_remove()
		this.news_label.grid_remove()
		self.getPost()
		
			
		
	def getPost(self):
		feed = requests.get(self.feed_url)	
		debug(feed.content,2)
		
		lines=[]
		lines = feed.content.split("\r\n")
		line = []
		try:
			line = lines[4].split("\t")
			this.newsitem.grid()	
			this.news_label.grid()	
			
			this.news_label["text"] = "News"
			this.newsitem["text"] = line[0]
			this.newsitem["url"] = line[1]

		except:
			this.newsitem.grid_remove()
			this.news_label.grid_remove()	
			
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
			r = requests.get(url)

			
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
	#We want three columns, label, text, button
	this.frame.columnconfigure(5, weight=1)
	
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
	  
	this.newsFeed.getPost()  
	  
	if entry['event'] == 'USSDrop':
		this.ussInator.ussDrop(cmdr, system, station, entry)
		
	if entry['event'] == 'SupercruiseExit':
		# we need to check if we dropped from a uss
		this.ussInator.SupercruiseExit(cmdr, system, station, entry)		
		
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
	
def setUssReport(system,threat,timestamp):
	this.report_label["text"] = "NHSS USS"
	this.report["text"] = "Report Thargoid activity to Canonn"
	
	# Timesytamp 2017-10-14T15:08:24Z
	date,part=timestamp.split("T")
	time=part[:5]
	
	this.report["url"] = "https://docs.google.com/forms/d/e/1FAIpQLScsU0RZLWl2JPEW-Oy3D1FBGi2G7wGZTrFHe9mOIdLfX0wTEQ/viewform?usp=pp_url&entry.745898940="+quote_plus(system)+"&entry.1910321643="+str(threat)+"&entry.829248547="+date+"&entry.1395484353="+time+"&entry.689381068="+str(this.guid)
	#this.report["url"] = "https://docs.google.com/forms/d/e/1FAIpQLScsU0RZLWl2JPEW-Oy3D1FBGi2G7wGZTrFHe9mOIdLfX0wTEQ/viewform?entry.745898940="+quote_plus(system)+"&entry.829248547&entry.1395484353&entry.191907177"
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
	
# -*- coding: utf-8 -*-
import sys
import re
import ttk
import Tkinter as tk
import requests
import os
from urllib import quote_plus
from  math import sqrt,pow,trunc


from config import applongname, appversion
import myNotebook as nb
from config import config
import csv

this = sys.modules[__name__]
this.s = None
this.prep = {}

# Lets capture the plugin name we want the name - "EDMC -"
myPlugin = "USS Survey"

def getDistance(x1,y1,z1,x2,y2,z2):
	return round(sqrt(pow(float(x2)-float(x1),2)+pow(float(y2)-float(y1),2)+pow(float(z2)-float(z1),2)),2)

def get_patrol():
	url="https://docs.google.com/spreadsheets/d/e/2PACX-1vS6PK6ZhVuNEPqmYXdBDd9hAwD7DYjg7SQmsRqcfLFBqNVexTD1Q43d6RKa1RBakZVvkcgF625FLCTP/pub?output=tsv"
	r = requests.get(url)
	#print r.content
	list={}
	
	for line in r.content.split("\n"):
		system,earth,merope,x,y,z,instructions= line.split("\t")
		if system != "System":
			list[system]={ "x": x, "y": y, "z": z, "instructions": instructions, "priority": 0, "visits": 0 }

	return list
	
	
def merge_visited():
	url="https://docs.google.com/spreadsheets/d/e/2PACX-1vQo6ZKo_30HVPledftSo5_bjxdGYymTS2lycTjpmxUz4Q5WsrN0jV05VKo9y-IbY0I3J35kZSftYoS1/pub?output=tsv"
	r = requests.get(url)
	#print r.content
	
	
	for line in r.content.split("\r\n"):
		ts,arrived,departed,commander,system= line.split("\t")
		
		try:
			if system != "System Name":
				this.patrol[system]["visits"]+=1
		except:
			print "Failed: "+ system

	return list	
		
def plugin_start():
	"""
	Load Template plugin into EDMC
	"""
	
	this.patrol=get_patrol()
	merge_visited()
	
	print this.patrol
	return myPlugin
	

def plugin_app(parent):
	label = tk.Label(parent, text= myPlugin + ":")
	this.status = tk.Label(parent, anchor=tk.W, text="Ready")
		
	return (label, this.status)

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
				print exception
					
	if n == 999999:
		return None,None,None,None,None,None,None,None,None,None,None
	
	return nearest,n,list[nearest]["instructions"],list[nearest]["visits"],list[nearest]["x"],list[nearest]["y"],list[nearest]["z"]
	
def detect_hyperdiction(cmdr,timestamp,endjump,startjump=None):
	if startjump == None:
		print "No startjump event: Is that even possible"
	if startjump == endjump:
		print "Hyperdiction detected."
		# log it to a spreadheet
		# show it in the status with a pre-filled link to the Canonn form.
	
	
		
	
# Detect journal events
def journal_entry(cmdr, system, station, entry):
  
	try:
		this.uss
	except:
		this.uss=False
		
	  
	if entry['event'] == 'USSDrop':
		#set some variables for logging when we exit supercruise
		this.uss=True
		this.usstype=entry['USSType']
		this.usslocal=entry['USSType_Localised']
		this.threat=str(entry['USSThreat'])
			
		
	if entry['event'] == 'SupercruiseExit':
		# we need to check if we dropped from a uss
		if this.uss:
			this.uss=False
			
			this.status['text']="Logging: "+this.usslocal
			#url  = "https://docs.google.com/forms/d/e/1FAIpQLScVk2LW6EkIW3hL8EhuLVI5j7jQ1ZmsYCLRxgCZlpHiN8JdcA/formResponse?usp=pp_url&entry.106150081="+cmdr+"&entry.582675236="+quote_plus(entry['StarSystem'])+"&entry.413701316="+quote_plus(entry['Body'])+"&entry.218543806="+quote_plus(this.usstype)+"&entry.455413428=+"quote_plus(this.usslocal)+"&entry.790504343="+quote_plus(this.threat)+"&submit=Submit"
			url = "https://docs.google.com/forms/d/e/1FAIpQLScVk2LW6EkIW3hL8EhuLVI5j7jQ1ZmsYCLRxgCZlpHiN8JdcA/formResponse?usp=pp_url&entry.106150081="+cmdr+"&entry.582675236="+quote_plus(entry['StarSystem'])+"&entry.413701316="+quote_plus(entry['Body'])+"&entry.218543806="+quote_plus(this.usstype)+"&entry.455413428="+quote_plus(this.usslocal)+"&entry.790504343="+quote_plus(this.threat)+"&submit=Submit"
			#print url
			r = requests.get(url)	
			print r
		
	if entry['event'] == 'StartJump' and entry['JumpType'] == 'Hyperspace':
			
		#When we start a jump we are leaving the system so we can log our jump
		try:	
			#we might have not captured the arrival because we were offline
			this.arrived
		except:
			this.arrived=entry["timestamp"]
			
		this.startjump=system
		
		try:	
			#If the system we are jumping out of is one of the nearest then 
			# we need to log it otherwise dont both
			if this.nearest == system:
				try:
					url = "https://docs.google.com/forms/d/e/1FAIpQLScmM7IuJAla_9LflBf-Bi7aNsIhbNkuh_3g6_Z2PL87zMzXGg/formResponse?usp=pp_url&entry.1836345870="+this.arrived+"&entry.25192571="+entry["timestamp"]+"&entry.424221764="+cmdr+"&entry.799655481="+system			
					r = requests.get(url)	
					print r
					print "Jump started: " +cmdr+"  "+system
				except:
					print "error sending "+url 
		except:	
			print entry
			
			
	
	if entry['event'] == 'FSDJump':
			detect_hyperdiction(cmdr,entry["timestamp"],entry["StarSystem"],this.startjump)
					
			#set the arrival time for locgging
			this.arrived=entry["timestamp"]
			#we have coordinates so we can find the nearest system
			this.jumpsystem = { "x": entry["StarPos"][0], "y": entry["StarPos"][1], "z": entry["StarPos"][2], "name": entry["StarSystem"] }	
			print this.jumpsystem
			merge_visited()
			this.nearest,distance,instructions,visits,x,y,z = findNearest(this.jumpsystem,this.patrol)
			this.status['text']=this.nearest+" ("+str(distance)+")"


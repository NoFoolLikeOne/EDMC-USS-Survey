# -*- coding: utf-8 -*-
import sys
import re
import ttk
import Tkinter as tk
import requests
import os

from PIL import Image


from config import applongname, appversion
import myNotebook as nb
from config import config


this = sys.modules[__name__]
this.s = None
this.prep = {}

# Lets capture the plugin name we want the name - "EDMC -"
myPlugin = "USS Survey"


def plugin_start():
	"""
	Load Template plugin into EDMC
	"""
	
	
	return myPlugin

	

def plugin_app(parent):
	label = tk.Label(parent, text= myPlugin + ":")
	this.status = tk.Label(parent, anchor=tk.W, text="Ready")
		
	return (label, this.status)


# Detect journal events
def journal_entry(cmdr, system, station, entry):
  
	try:
		this.uss
	except:
		this.uss=False
  
	if entry['event'] == 'USSDrop':
		this.uss=True
		this.usstype=entry['USSType']
		this.usslocal=entry['USSType_Localised']
		this.threat=entry['USSThreat']
		
				
		
		
	if entry['event'] == 'SupercruiseExit':
		# we need to check if we dropped from a uss
		if this.uss:
			this.uss=False
			
			this.status['text']="Logging: "+this.usslocal+" "+entry['StarSystem']+" ("+entry['Body']+")"
			url = "https://docs.google.com/forms/d/e/1FAIpQLScVk2LW6EkIW3hL8EhuLVI5j7jQ1ZmsYCLRxgCZlpHiN8JdcA/viewform?usp=pp_url&entry.582675236="+entry['StarSystem']+"&entry.413701316="+entry['Body']+"&entry.218543806="+this.usstype+"&entry.455413428="+this.usslocal+"&entry.790504343="+str(this.threat)
			print url
			r = requests.get(url)	
		
		
		



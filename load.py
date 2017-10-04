# -*- coding: utf-8 -*-
import sys
import re
import ttk
import Tkinter as tk
import requests
import os
from urllib import quote_plus



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
		this.threat=str(entry['USSThreat'])
		
				
		
		
	if entry['event'] == 'SupercruiseExit':
		# we need to check if we dropped from a uss
		if this.uss:
			this.uss=False
			
			this.status['text']="Logging: "+this.usslocal
			url = "https://docs.google.com/forms/d/e/1FAIpQLScVk2LW6EkIW3hL8EhuLVI5j7jQ1ZmsYCLRxgCZlpHiN8JdcA/formResponse?usp=pp_url&entry.582675236="+quote_plus(entry['StarSystem'])+"&entry.413701316="+quote_plus(entry['Body'])+"&entry.218543806="+quote_plus(this.usstype)+"&entry.455413428="+quote_plus(this.usslocal)+"&entry.790504343="+quote_plus(this.threat)+"&submit=Submit"
			#print url
			r = requests.get(url)	
		
		
		



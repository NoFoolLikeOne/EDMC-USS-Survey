# -*- coding: utf-8 -*-
import sys
import re
import ttk
import Tkinter as tk
import requests
import os
import csv
import json
import uuid
from urllib import quote_plus
from  math import sqrt,pow,trunc
from ttkHyperlinkLabel import HyperlinkLabel
import datetime
import webbrowser
import threading
from winsound import *
import ctypes


from config import applongname, appversion
import myNotebook as nb
from config import config
import csv
import re

from canonn import journaldata
from canonn import factionkill
from canonn import nhss
from canonn import codex
from canonn import hdreport



this = sys.modules[__name__]
this.s = None
this.prep = {}
# Lets capture the plugin name we want the name - "EDMC -"
myPlugin = "USS Survey"

#this.debuglevel=2
this.version="4.8.1"
this.client_version="{}.{}".format(myPlugin,this.version)

this.body_name=None
this.fss= {}

this.systemCache={ "Sol": (0,0,0) }

this.nearloc = {
   'Latitude' : None,
   'Longitude' : None,
   'Altitude' : None,
   'Heading' : None,
   'Time' : None
}

#for 
def _callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode_unicode_references(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data)
    
    
class SelfWrappingHyperlinkLabel(HyperlinkLabel):
    "Tries to adjust its width."

    def __init__(self, *a, **kw):
        "Init."

        HyperlinkLabel.__init__(self, *a, **kw)
        self.frame=a[0]
        self.frame.bind('<Configure>', self.__configure_event)      

    def __configure_event(self, event):
        "Handle resizing."
        self.configure(wraplength=event.width-2)    

#data = "U.S. Adviser&#8217;s Blunt Memo on Iraq: Time &#8216;to Go Home&#8217;"
#print decode_unicode_references(data)


def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    this.anon = tk.IntVar(value=config.getint("Anonymous")) # Retrieve saved value from config
    this.hide_patrol = tk.IntVar(value=config.getint("hide_patrol"))    # Retrieve saved value from config
    
    this.hide_nhss = tk.IntVar(value=config.getint("hide_nhss"))    # Retrieve saved value from config
    this.uss_debug = tk.IntVar(value=config.getint("uss_debug"))
    this.gnosis_egg = tk.IntVar(value=config.getint("gnosis_egg"))
    
    frame = nb.Frame(parent)
    frame.columnconfigure(3, weight=1)
    
    #nb.Label(frame, text="Hello").grid()
    #nb.Label(frame, text="Make me anonymous").grid()
    #this.canonnReportDesc = tk.Message(this.frame,width=200)
    
    nb.Checkbutton(frame, text="I want to be anonymous", variable=this.anon).grid(row = 1, column = 0,sticky=tk.W)
    nb.Checkbutton(frame, text="Hide Canonn Patrol", variable=this.hide_patrol).grid(row = 2, column = 0,columnspan=1,sticky=tk.W)
    
    nb.Checkbutton(frame, text="Hide Non Human Survey", variable=this.hide_nhss).grid(row = 2, column = 3,columnspan=1,sticky=tk.W)
    nb.Checkbutton(frame, text="Turn on debugging", variable=this.uss_debug).grid(row = 10, column = 0,columnspan=3,sticky=tk.SW)
    nb.Checkbutton(frame, text="Disable Gnosis Easter Egg", variable=this.gnosis_egg).grid(row = 11, column = 0,columnspan=3,sticky=tk.SW)
        
    
    return frame
   
def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('Anonymous', this.anon.get())       
    config.set('hide_patrol', this.hide_patrol.get())      
    
    config.set('hide_nhss', this.hide_nhss.get())      
    config.set('uss_debug', this.uss_debug.get())      
    config.set('gnosis_egg', this.gnosis_egg.get())    
    
    this.patrolZone.showPatrol(cmdr)
    
    if config.getint("Anonymous") >0:
        debug("I want to be anonymous")     
    else:
        debug("I want to be famous")        
        
    this.patrolZone.showPatrol(cmdr)

class Reporter(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload = payload

    def run(self):
        try:
            requests.get(self.payload)
            debug(self.payload,2)
        except:
            print("["+myPlugin+"] Issue posting message " + str(sys.exc_info()[0]))
            
class Player(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload = payload

    def run(self):
        try:
            soundfile = plugin_dir()+'\\'+self.payload
            PlaySound(soundfile,SND_FILENAME)
        except:
            print("["+myPlugin+"] Issue playing sound " + str(sys.exc_info()[0]))           
        
        
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
        self.hydra=0
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

    def incHydra(self):
        self.hydra+=1   
        self.setReport()        
        
    def setSpace(self):
        self.probe=0
        self.sensor=0
        self.scout=0
        self.cyclops=0
        self.basilisk=0
        self.medusa=0
        self.hydra=0
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
        
    def uivisible(self):
        if config.getint("hide_nhss") >0:
            debug("Hide NHSS")      
            return False
        else:
            debug("Show NHSS,2")        
            return True     
        
    def hide(self):
        this.BASILISK.grid_remove()
        this.CYCLOPS.grid_remove()
        this.MEDUSA.grid_remove()
        this.HYDRA.grid_remove()
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
        if entry['USSType'] == "$USS_Type_NonHuman;" and self.uivisible(): 
            self.uss_type=entry['USSType']
            self.threat=str(entry['USSThreat'])     
            self.system=system
            self.commander=cmdr
            self.setSpace()
            this.BASILISK.grid()
            this.CYCLOPS.grid()
            this.MEDUSA.grid()
            this.HYDRA.grid()
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
        url+="&entry.257267572="+str(self.hydra)    
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
        self.report=self.getThings(self.report,"hydra",self.hydra)      
        self.report=self.getThings(self.report,"human ship",self.cobra)
        if self.probe+self.sensor+self.scout+self.cyclops+self.basilisk+self.medusa+self.cobra+self.hydra == 0:
            self.report=self.report+" click icons to report thargoids"
        self.label["text"]=self.report
        self.label["url"]=self.getUrl("viewform")
        
        
        


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

    def FSSDetect(self,cmdr, system, station, entry):
        debug("FSSDetect",2)
        
        try:
            globalfss=fss.get(system)
            oldthreat=globalfss.get(entry.get("ThreatLevel"))
        except:
            oldthreat=False
        
        if oldthreat==True:
            debug("Threat level already recorded here "+str(entry.get("ThreatLevel")))
        else:
            try:
                fss[system][entry.get("ThreatLevel")] =  True
            except:
                fss[system]={ entry.get("ThreatLevel"): True}
          
                
            debug("Recording threat level "+str(entry.get("ThreatLevel")))
            debug(fss)
            usstype=entry['USSType']
            usslocal=entry['USSType_Localised']
            threat=str(entry['ThreatLevel'])
            self.sysx,self.sysy,self.sysz=edsmGetSystem(system)
                    
                    
            dmerope=getDistanceMerope(self.sysx,self.sysy,self.sysz)
            dsol=getDistanceSol(self.sysx,self.sysy,self.sysz)
            
                                        
            url = "https://docs.google.com/forms/d/e/1FAIpQLScVk2LW6EkIW3hL8EhuLVI5j7jQ1ZmsYCLRxgCZlpHiN8JdcA/formResponse?usp=pp_url&entry.1236915632="+str(this.guid)+"&entry.106150081="+cmdr+"&entry.582675236="+quote_plus(system)+"&entry.158339236="+str(self.sysx)+"&entry.608639155="+str(self.sysy)+"&entry.1737639503="+str(self.sysz)+"&entry.1398738264="+str(dsol)+"&entry.922392846="+str(dmerope)+"&entry.218543806="+quote_plus(usstype)+"&entry.455413428="+quote_plus(usslocal)+"&entry.790504343="+quote_plus(threat)+"&submit=Submit"
                #print url
            Reporter(url).start()        
            url="https://docs.google.com/forms/d/e/1FAIpQLSeOBbUTiD64FyyzkIeZfO5UMfqeuU2lsRf3_Ulh7APddd91JA/formResponse?usp=pp_url"
            url+="&entry.306505776="+quote_plus(system)
            url+="&entry.1559250350=Non Human Signal"
            url+="&entry.1031843658="+str(threat)
            url+="&entry.1519036101="+quote_plus(cmdr)
            Reporter(url).start()        
        
            
    def SupercruiseExit(self,cmdr, system, station, entry):
        if self.uss:
            #This is a USS drop set back to false
            self.uss=False
                    
            
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
        self.uss=False
            
def v2n(v):
    major,minor,point=v.split('.')
    r = int("%(major)03d%(minor)03d%(point)03d" % {"major": int(major), "minor": int(minor), "point": int(point)})
    return r            
                
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
        self.startevent=entry
        
    def DebugInfo(self,cmdr, system, entry):
        url="https://docs.google.com/forms/d/e/1FAIpQLSeLsjL0M7mJy89y6AOH7eo5kSoVZhR_hb3zAmF_C4tsvKpvKQ/formResponse?usp=pp_url"
        url+="&entry.1892927060="+quote_plus(cmdr);
        url+="&entry.1740782271="+quote_plus(system);
        url+="&entry.531806815="+quote_plus(json.dumps(self.startevent));
        url+="&entry.495111246="+quote_plus(json.dumps(entry));
        Reporter(url).start()
        

    def FSDJump(self,cmdr, system, station, entry):
        self.end_jump = entry["StarSystem"]
        self.cmdr=cmdr
        if self.target_jump != self.end_jump and system == self.start_jump:
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
            self.DebugInfo(cmdr, system,entry)

class news:
    def __init__(self,frame):
        debug("Initiating News")
        self.feed_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vSy9ij93j2qbwD-1_bXlI5IfO4EUD4ozNX2GJ2Do5tZNl-udWIqBHxYbtmcMRwvF6favzay3zY2LpH5/pub?gid=1876886084&single=true&output=tsv"
        self.version_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vSy9ij93j2qbwD-1_bXlI5IfO4EUD4ozNX2GJ2Do5tZNl-udWIqBHxYbtmcMRwvF6favzay3zY2LpH5/pub?gid=0&single=true&output=tsv"
        self.nag_count=0
        this.description = tk.Message(frame,width=200)
        this.news_label = tk.Label(frame, text=  "Report:")
        this.newsitem= SelfWrappingHyperlinkLabel(frame, compound=tk.LEFT, popup_copy = True,wraplength=50)
        
        #this.newsitem["width"]=100
        #this.newsitem["width"]=this.parent.winfo_width()-10-this.news_label.winfo_width()
        #this.newsitem["wraplength"]=this.parent.winfo_width()-10-this.news_label.winfo_width()
        
        this.news_label.grid(row = 3, column = 0, sticky=tk.W)
        this.newsitem.grid(row = 3, column = 1, columnspan=3, sticky=tk.W)  
        this.newsitem["text"]= "News"
        this.news_label["text"]= "News"
        this.newsitem.grid_remove()
        this.news_label.grid_remove()
        self.getPost()
        
    
    def nag(self):
        debug("Nagging")
        self.nag_count=self.nag_count+1
        if self.nag_count == 3:
            Player("nag1.wav").start()
        if self.nag_count == 10:
            Player("nag2.wav").start()


        
    def getPost(self):
        
        versions = requests.get(self.version_url)   
        
        getnews=True
        for line in versions.content.split("\r\n"):
            rec=line.split("\t")
            if rec[0] == 'EDMC-USS-Survey' and v2n(rec[1]) > v2n(this.version):
                
                this.newsitem["text"] = "Please upgrade USS Survey to release; "+rec[1]
                this.newsitem["url"] = rec[2]
                this.newsitem.grid()    
                this.news_label.grid()
                debug("Nagging in getPost")
                self.nag()
                getnews=False
                
        
        if getnews:
            feed = requests.get(self.feed_url)      
            debug(feed.content,2)
            lines=feed.content.split("\r\n")
            ## only want most recent news item
            line=lines[1]
            rec=line.split("\t")
            this.newsitem["text"] = decode_unicode_references(rec[2])
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
        if config.getint("Anonymous") >0:
            cmdr="Anonymous"
        else:
            cmdr=data["commander"]["name"]
            
        self.showPatrol(cmdr)
        
    
        
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
    
    return (d2-d1).days *24 *60
        
def debug(value,level=None):
    if config.getint("uss_debug") >0:
        print "["+myPlugin+"] "+str(value)
        


def getDistance(x1,y1,z1,x2,y2,z2):
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
    
def plugin_dir():
    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.GetEnvironmentVariableW(u"USERPROFILE", buf, 1024)
    home_dir = buf.value
    plugin_base = os.path.basename(os.path.dirname(__file__))
    return home_dir+'\\AppData\\Local\\EDMarketConnector\\plugins\\'+plugin_base
        
def plugin_start():
    """
    Load Template plugin into EDMC
    """

    
    this._IMG_VISITED = tk.PhotoImage(file = plugin_dir()+'\\tick3.gif')
    this._IMG_IGNORE = tk.PhotoImage(file = plugin_dir()+'\\cross.gif')
    this._IMG_CLIPBOARD = tk.PhotoImage(file = plugin_dir()+'\\clipboard.gif')
    this._IMG_BASILISK = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Basilisk_25px.gif')
    this._IMG_CYCLOPS = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Cyclops_25px.gif')
    this._IMG_MEDUSA = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Medusa_25px.gif')
    this._IMG_HYDRA = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Hydra_25px.gif')
    this._IMG_PROBE = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Probe_25px.gif')
    this._IMG_SCOUT = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Scout_25px_1.gif')
    this._IMG_SENSOR = tk.PhotoImage(file = plugin_dir()+'\Icons\\LCU_Sensor_25px.gif')
    this._IMG_SPACE = tk.PhotoImage(file = plugin_dir()+'\\Icons\\LCU_Space_25px.gif')
    this._IMG_TRANSMIT = tk.PhotoImage(file = plugin_dir()+'\\Icons\\transmit.gif')
    this._IMG_COBRA = tk.PhotoImage(file = plugin_dir()+'\\Icons\\cobra.gif')   
    
    this.patrol=get_patrol()
    merge_visited()
    
    #print this.patrol
    return myPlugin
    
def copy_patrol_to_clipboard(event):
    window=tk.Tk()
    window.withdraw()
    window.clipboard_clear()  # clear clipboard contents
    window.clipboard_append(this.clip)      
    window.destroy()
    
        

    
def plugin_app(parent):

    this.parent = parent
    #create a new frame as a containier for the status
    
        
    this.frame = tk.Frame(parent)
    
    
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
    this.HYDRA = tk.Button(this.buttonbar, anchor=tk.W, image=this._IMG_HYDRA, command=canonnReport.incHydra)
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
    this.HYDRA.grid(row = 0, column = 7, sticky=tk.W)   
    this.COBRA.grid(row = 0, column = 8, sticky=tk.W)
    this.TRANSMIT.grid(row = 0, column = 9, sticky=tk.W)
    
    this.BASILISK.grid_remove()
    this.CYCLOPS.grid_remove()
    this.MEDUSA.grid_remove()
    this.HYDRA.grid_remove()
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
#   this.tick.grid(row = 0, column = 3, sticky=tk.W)
    this.cross.grid(row = 0, column = 3, sticky=tk.W)
    this.report_label.grid(row = 2, column = 0, sticky=tk.W)
    this.report.grid(row = 2, column = 1, columnspan=3, sticky=tk.W)
    this.description.grid(row = 1, column = 0, columnspan=4, sticky=tk.W)
    
    this.label.grid_remove()
    this.status.grid_remove()
    this.clipboard.grid_remove()
#   this.tick.grid_remove()
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
    nearest = { 'distance': 999999, 'name': "No Systems to Patrol" } 
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

def setSystem(system,x,y,z):
    this.systemCache[system]=(x,y,z)
    
def edsmGetSystem(system):
    debug(this.systemCache)
    if this.systemCache.has_key(system):
        debug("using system cache")
        return this.systemCache[system]
        
    else:
        url = 'https://www.edsm.net/api-v1/system?systemName='+quote_plus(system)+'&showCoordinates=1'      
        #print url
        r = requests.get(url)
        s =  r.json()
        #print s
        debug("populating cache")
        this.systemCache[system]=(s["coords"]["x"],s["coords"]["y"],s["coords"]["z"])
        return s["coords"]["x"],s["coords"]["y"],s["coords"]["z"]

def getDistanceMerope(x1,y1,z1):
    return round(sqrt(pow(float(-78.59375)-float(x1),2)+pow(float( -149.625)-float(y1),2)+pow(float(-340.53125)-float(z1),2)),2)        
    
def getDistanceSol(x1,y1,z1):
    return round(sqrt(pow(float(0)-float(x1),2)+pow(float(0)-float(y1),2)+pow(float(0)-float(z1),2)),2)         
        
def journal_entry(cmdr, is_beta, system, station, entry, state):

    startup_stats(cmdr)
    
    if ('Body' in entry):
            this.body_name = entry['Body']    
    
    if config.getint("Anonymous") >0:
        commander="Anonymous"
    else:
        commander=cmdr
        
        
    
    
    if system:
        x,y,z=edsmGetSystem(system)
    else:
        x=None
        y=None
        z=None    
    
    journal_entry_wrapper(commander, is_beta, system, station, entry, state,x,y,z,this.body_name,this.nearloc['Latitude'],this.nearloc['Longitude'],this.client_version)    
    
def play_gnosis_egg():
    if config.getint("gnosis_egg") != 1 :
        Player("gnosis_egg.wav").start()
        config.set('gnosis_egg', 1)    
        
    
# Detect journal events
def journal_entry_wrapper(cmdr, is_beta, system, station, entry, state,x,y,z,body,lat,lon,client):

    this.guid = uuid.uuid1()
    this.cmdr=cmdr
      
    statistics(cmdr, is_beta, system, station, entry, state)      
      
    
    faction_kill(cmdr, is_beta, system, station, entry, state)
    refugee_mission(cmdr, is_beta, system, station, entry, state)
    CodexEntry(cmdr, is_beta, system, station, entry, state)
    AXZone(cmdr, is_beta, system, station, entry, state)

    
    
    if entry['event'] == "SupercruiseExit" and entry["Body"] == "The Gnosis" and entry["BodyType"] == "Station":
        this.frame.after(20000,lambda: play_gnosis_egg())
    
    if entry['event'] == 'USSDrop':
        this.ussInator.ussDrop(cmdr, system, station, entry)
        this.canonnReport.ussDrop(cmdr, system, station, entry)
        
    if entry['event'] == 'FSSSignalDiscovered' and entry.get('USSType') == "$USS_Type_NonHuman;":       
        this.ussInator.FSSDetect(cmdr, system, station, entry)
        
        

        
        
    if entry['event'] == 'SupercruiseExit':
        # we need to check if we dropped from a uss
        this.ussInator.SupercruiseExit(cmdr, system, station, entry)        
        this.newsFeed.getPost()  
    
    if entry['event'] == 'StartJump':   
        this.newsFeed.getPost()  
        
    if entry['event'] == 'StartJump' and entry['JumpType'] == 'Hyperspace':
            
        debug("StartJump Hyperspace",2)
        debug(entry,2)
        
        this.hyperdictionInator.StartJump(cmdr, system, station, entry)
                        
                
    
    if entry['event'] == 'FSDJump':
        
        setSystem(entry["StarSystem"],entry["StarPos"][0],entry["StarPos"][1],entry["StarPos"][2])
        debug("FSDJump",2)
        debug(entry,2)
            
        this.ussInator.FSDJump(cmdr, system, station, entry)
        this.hyperdictionInator.FSDJump(cmdr, system, station, entry)   
        this.patrolZone.FSDJump(cmdr, system, station, entry)
        this.meropeLog.FSDJump(cmdr, system, station, entry)
    
    if entry['event'] == 'Location':
        this.patrolZone.Location(cmdr, system, station, entry)
        setSystem(system,entry["StarPos"][0],entry["StarPos"][1],entry["StarPos"][2])
        
    if entry['event'] == '1G':
        this.patrolZone.startUp(cmdr, system, station, entry)       

    #Canonn API calls
    #dont load journal data
    #journaldata.submit(cmdr, is_beta, system, station, entry,client)
    factionkill.submit(cmdr, is_beta, system, station, entry,client)
    nhss.submit(cmdr, is_beta, system, station, entry,client)
    hdreport.submit(cmdr, is_beta, system, station, entry,client)
    codex.submit(cmdr, is_beta, system, x,y,z, entry, body,lat,lon,client)
        

        
def matches(d, field, value):
    return field in d and value == d[field]     
        
def faction_kill(cmdr, is_beta, system, station, entry, state):
    if entry['event'] == "FactionKillBond":
        debug("FactionKillBond",2)
        factionMatch=(matches(entry, 'VictimFaction', '$faction_Thargoid;') or matches(entry, 'VictimFaction', '$faction_Guardian;'))
        if factionMatch and 'Reward' in entry:
            url="https://docs.google.com/forms/d/e/1FAIpQLSevc8RrhOzOq9U0a2VC29N_lgjRfVU9vlF-oKdjhvZu6YnLvw/formResponse?usp=pp_url"
            url+="&entry.567957318="+quote_plus(cmdr);
            if is_beta:
                beta='Y'
            else: 
                beta='N'
            url+="&entry.1848556807="+quote_plus(beta)
            url+="&entry.1086702490="+quote_plus(system)
            if station is not None:
                url+="&entry.1446740035="+quote_plus(station)
            
            url+="&entry.396335290="+str(entry["Reward"])
            url+="&entry.576102634="+quote_plus(entry["AwardingFaction"])
            url+="&entry.691973931="+quote_plus(entry["VictimFaction"])
            Reporter(url).start()

def CodexEntry(cmdr, is_beta, system, station, entry, state):
    #{ "timestamp":"2018-12-30T00:48:12Z", "event":"CodexEntry", "EntryID":2100301, "Name":"$Codex_Ent_Cone_Name;", "Name_Localised":"Bark Mounds", "SubCategory":"$Codex_SubCategory_Organic_Structures;", "SubCategory_Localised":"Organic structures", "Category":"$Codex_Category_Biology;", "Category_Localised":"Biological and Geological", "Region":"$Codex_RegionName_18;", "Region_Localised":"Inner Orion Spur", "System":"HIP 16378", "SystemAddress":1, "VoucherAmount":2500 }
    if entry['event'] == "CodexEntry":
        debug("CodexEntry",2)
        debug(entry)
        x,y,z=edsmGetSystem(system)
        url="https://docs.google.com/forms/d/e/1FAIpQLSfdr7GFj6JJ1ubeRXP_uZu3Xx9HPYT6507lRLqqC0oUZyj-Jg/formResponse?usp=pp_url"
        
        url+="&entry.1415400073="+quote_plus(cmdr);
        url+="&entry.1860059185="+quote_plus(system)
        url+="&entry.810133478="+str(x)
        url+="&entry.226558470="+str(y)
        url+="&entry.1643947574="+str(z)
        if this.body_name:
            url+="&entry.1432569164="+quote_plus(this.body_name)
        if this.nearloc['Latitude']:
            url+="&entry.1891952962="+str(this.nearloc['Latitude'])
            url+="&entry.405491858="+str(this.nearloc['Longitude'])
        url+="&entry.1531581549="+quote_plus(str(entry["EntryID"]))
        url+="&entry.1911890028="+quote_plus(entry["Name"])
        url+="&entry.1057995915="+quote_plus(entry["Name_Localised"])
        url+="&entry.598514572="+quote_plus(entry["SubCategory"])
        url+="&entry.222515268="+quote_plus(entry["SubCategory_Localised"])
        url+="&entry.198049318="+quote_plus(entry["Category"])
        url+="&entry.348683576="+quote_plus(entry["Category_Localised"])
        url+="&entry.761612585="+quote_plus(entry["Region"])
        url+="&entry.216399442="+quote_plus(entry["Region_Localised"])
        url+="&entry.1236018468="+quote_plus(str(entry["SystemAddress"]))
        if('VoucherAmount' in entry):
            url+="&entry.1250864566="+quote_plus(str(entry["VoucherAmount"]))
                
            
        
        Reporter(url).start()

        
def AXZone(cmdr, is_beta, system, station, entry, state):
    #{ "timestamp":"2019-01-19T23:22:26Z", "event":"FSSSignalDiscovered", "SystemAddress":250414621860, "SignalName":"$Warzone_TG;", "SignalName_Localised":"AX Conflict Zone" }
    if entry['event'] == "FSSSignalDiscovered" and entry["SignalName"] == "$Warzone_TG;":
        debug("AXZone",2)
        debug(entry)
        x,y,z=edsmGetSystem(system)
        url="https://docs.google.com/forms/d/e/1FAIpQLSdHFZ8Mp4EHsJH6gUqXyeWkeEUt3YOGEaOO3X8H4m-gHNYzdQ/formResponse?usp=pp_url"
       
        
        url+="&entry.1257612503="+quote_plus(cmdr);
        url+="&entry.1541680555="+quote_plus(system)
        url+="&entry.484596368="+str(x)
        url+="&entry.1443755704="+str(y)
        url+="&entry.1285491432="+str(z)
        url+="&entry.837147926="+str(entry.get("SystemAddress"))
        
        Reporter(url).start()        

            
def refugee_mission(cmdr, is_beta, system, station, entry, state):          
    if entry['event'] == "MissionAccepted": 
        if entry['Name'] == "Mission_RS_PassengerBulk_name" or entry['Name'] == "Mission_RS_PassengerBulk":
            if entry['PassengerType'] == "Refugee":
                url="https://docs.google.com/forms/d/e/1FAIpQLSckkj7F4EdwGtwBl0uGtHeDloXErdTIdhFDajtnkJTqomqeYA/formResponse?usp=pp_url"
                url+="&entry.136746653="+quote_plus(cmdr)
                url+="&entry.1227401710="+quote_plus(system)
                url+="&entry.245393486="+quote_plus(entry["Faction"])
                url+="&entry.529899739="+quote_plus(entry["Name"])  
                url+="&entry.7428048="+str(entry["PassengerCount"])
                url+="&entry.1730742117="+str(entry["Reward"])
                Reporter(url).start()
        

## I want to avoid sending this event if there has not been any change
## so we will have a global dict

this.tg_stats = {
    "tg_encounter_wakes": 0,
    "tg_encounter_imprint": 0,
    "tg_encounter_total": 0,
    "tg_timestamp": 'x',
    "tg_scout_count": 0,
    "tg_last_system": "x"
}

        
        
def statistics(cmdr, is_beta, system, station, entry, state):
    if entry['event'] == "Statistics":
        tge=entry.get('TG_ENCOUNTERS')
        new_tg_stats = {
            "tg_encounter_wakes": tge.get("TG_ENCOUNTER_WAKES"),
            "tg_encounter_imprint": tge.get("TG_ENCOUNTER_IMPRINT"),
            "tg_encounter_total": tge.get("TG_ENCOUNTER_TOTAL"),
            "tg_timestamp": tge.get("TG_ENCOUNTER_TOTAL_LAST_TIMESTAMP"),
            "tg_scout_count": tge.get("TG_SCOUT_COUNT"),
            "tg_last_system": tge.get("TG_ENCOUNTER_TOTAL_LAST_SYSTEM")
        }
        if new_tg_stats == this.tg_stats:
            debug("TG Stats unchanged",2)
        else:
            debug("TG Stats changed",2)
            this.tg_stats=new_tg_stats
            url="https://docs.google.com/forms/d/e/1FAIpQLScF_URtGFf1-CyMNr4iuTHkxyxOMWcrZ2ZycrKAiej0eC-hTA/formResponse?usp=pp_url"
            url+="&entry.613206362="+quote_plus(cmdr)
            if "TG_ENCOUNTER_WAKES" in entry['TG_ENCOUNTERS']:
                url+="&entry.1085684396="+str(entry['TG_ENCOUNTERS']["TG_ENCOUNTER_WAKES"])
            if "TG_ENCOUNTER_IMPRINT" in entry['TG_ENCOUNTERS']:
                url+="&entry.2026302508="+str(entry['TG_ENCOUNTERS']["TG_ENCOUNTER_IMPRINT"])
            if "TG_ENCOUNTER_TOTAL" in entry['TG_ENCOUNTERS']:
                url+="&entry.1600696255="+str(entry['TG_ENCOUNTERS']["TG_ENCOUNTER_TOTAL"])
            if "TG_ENCOUNTER_TOTAL_LAST_TIMESTAMP" in entry['TG_ENCOUNTERS']:
                url+="&entry.712826938="+str(entry['TG_ENCOUNTERS']["TG_ENCOUNTER_TOTAL_LAST_TIMESTAMP"])
            if "TG_SCOUT_COUNT" in entry['TG_ENCOUNTERS']:
                url+="&entry.1384358412="+str(entry['TG_ENCOUNTERS']["TG_SCOUT_COUNT"])
            if "TG_ENCOUNTER_TOTAL_LAST_SYSTEM" in entry['TG_ENCOUNTERS']:
                url+="&entry.1091946522="+str(entry['TG_ENCOUNTERS']["TG_ENCOUNTER_TOTAL_LAST_SYSTEM"])
            Reporter(url).start()
            
        
def startup_stats(cmdr):
    try:
        this.first_event
    except:
        this.first_event = True
        url="https://docs.google.com/forms/d/e/1FAIpQLSeuH9Rvt5mw9PGDZLtI6lAoanx5SOq_PKXjr7iPtRBP2QK_vg/formResponse?usp=pp_url"
        url+="&entry.1825274888="+quote_plus(cmdr)
        url+="&entry.294392943="+quote_plus(this.version)
        debug(url,2)
        Reporter(url).start()
        
        
        
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
    
def patrolVisible():
    if config.getint("hide_patrol") >0:
        debug("Hide Patrol,2")      
        return False
    else:
        debug("Show Patrol,2")      
        return True             
            
def setPatrol(nearest,distance,instructions):

    
    if nearest == None:
        this.status['text'] = "No patrol at this time" 
        this.status['url'] = None
        this.clipboard.grid_remove()
        this.description.grid_remove()
    else:
        if patrolVisible():
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
            
    if not patrolVisible():
        this.cross.grid_remove()
        this.label.grid_remove()
        this.status.grid_remove()
        this.clipboard.grid_remove()
        this.description.grid_remove()
            
def cmdr_data(data):
    this.patrolZone.cmdrData(data)
    
# def plugin_stop():
    # debug("Destroying Clipboard",3)
    # window.destroy()
    
def dashboard_entry(cmdr, is_beta, entry):
      
    
    this.landed = entry['Flags'] & 1<<1 and True or False
    this.SCmode = entry['Flags'] & 1<<4 and True or False
    this.SRVmode = entry['Flags'] & 1<<26 and True or False
    this.landed = this.landed or this.SRVmode
      #print "LatLon = {}".format(entry['Flags'] & 1<<21 and True or False)
      #print entry
    if(entry['Flags'] & 1<<21 and True or False):
        if('Latitude' in entry):
            this.nearloc['Latitude'] = entry['Latitude']
            this.nearloc['Longitude'] = entry['Longitude']
    else:
        this.body_name = None
        this.nearloc['Latitude'] = None
        this.nearloc['Longitude'] = None    
    
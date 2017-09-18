#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
from StringIO import StringIO
import xml.etree.ElementTree as ET
import time
import requests
from datetime import datetime
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context




# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString

# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'tvshows')

baseurl="http://www.7tv.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")



cookie=temp+"/cookie.jar"
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)


#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

favdatei   = xbmc.translatePath( os.path.join(temp,"favorit.txt") ).decode("utf-8")


def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def addDir(name, url, mode, iconimage, desc="",sendername="",offset="",limit="",type="",bild="",title="",series=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&sendername="+str(sendername)+"&offset="+str(offset)+"&limit="+str(limit)+"&type="+str(type)+"&iconimage="+bild+"&title="+title+"&series="+series
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  iconimage = ""
  liz.setProperty("fanart_image", iconimage)	
  liz.setProperty("fanart_image", "")
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok


        
def geturl(url,data="x",header=""):
        global cj
        print("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))           
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        return content

   
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',staffel=-1,episode=-1,serie="",aired=None):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"episode": episode, "season": staffel,"tvshowtitle":serie,"aired":aired})
  #liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", "")
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
 
       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
sendername = urllib.unquote_plus(params.get('sendername', ''))
offset = urllib.unquote_plus(params.get('offset', ''))
limit = urllib.unquote_plus(params.get('limit', ''))
type = urllib.unquote_plus(params.get('type', ''))
title = urllib.unquote_plus(params.get('title', ''))
bild = urllib.unquote_plus(params.get('iconimage', ''))
series = urllib.unquote_plus(params.get('series', ''))



def senderlist():

    inhalt = geturl(baseurl) 
    image_url=re.compile('<link rel="stylesheet" type="text/css" href="(.+?)">', re.DOTALL).findall(inhalt)
    
    kurz_inhalt = inhalt[inhalt.find('<ul class="site-nav-submenu">')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</nav>')]  
    match=re.compile('<a href="([^"]+)" [^>]+>([^<]+)</a>', re.DOTALL).findall(kurz_inhalt)
    for id,name in match:
      newurl=baseurl+id      
      debug("#### : "+newurl)
      addDir(name, newurl, "sender", "")      
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sender(url):
    addDir("Beliebte Sendungen", url, "belibtesendungen", "")      
    addDir("Aktuelle Ganze Folgen", url, "ganzefolgensender", "")           
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def belibtesendungen(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<h3 class="row-headline">Beliebte Sendungen</h3>')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="row ">')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      debug(" ##### ENTRY ####")
      debug(entry)
      urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('teaser-formatname">(.+?)<', re.DOTALL).findall(entry)[0]
      urlv=baseurl+urlt
      debug("belibtesendungen addurl :"+urlv)
      addDir(title, urlv, "serie", img,bild=img,title=title)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def ganzefolgensender(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('</h3>')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<h3 class="row-headline">Ihre Favoriten</h3>')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      if "class-clip" in entry:
        debug(" ##### ENTRY ####")
        debug(entry)
        urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
        img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
        serie=re.compile('<h4 class="teaser-formatname">(.+?)</h4>', re.DOTALL).findall(entry)[0]
        folge=re.compile('<h5 class="teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]#      
        try:
          teaser =re.compile(' <p class="teaser-info">(.+?)</p>', re.DOTALL).findall(entry)[0]        
          if not "Min." in teaser:
             aired=teaser
             duration=0
          else:
            aired=""
            laenge =re.compile('([0-9]+):([0-9]+) Min.', re.DOTALL).findall(teaser)           
            duration=laenge[0][0]*60+laenge[0][1]
        except:
             duration=0
             aired=""
        try: 
            staffel=re.compile('Staffel ([0-9]+)', re.DOTALL).findall(folge)[0]  
        except :
             staffel=-1
        try: 
            episode=re.compile('Episode ([0-9]+)', re.DOTALL).findall(folge)[0]  
        except :
             episode=-1                   
        title=serie + " - " + folge 
        urlv=baseurl+urlt
        debug("belibtesendungen addurl :"+urlv)
        addLink(title, urlv, "getvideoid", img,staffel=staffel,episode=episode,serie=serie,aired=aired,duration=duration)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def favadd(url,title,bild):
  debug(" favadd url :"+url)
  textfile=url+"###"+title+"###"+bild+"\n"
  try:
    f=open(favdatei,'r')
    for line in f:
      textfile=textfile+line
    f.close()
  except:
    pass
  f=open(favdatei,'w')
  f.write(textfile)
  f.close()
  xbmc.executebuiltin('Notification(7tv - Favoriten, [COLOR green]'+title+' hinzugefügt[/COLOR],5000,'+icon+')')
  xbmc.executebuiltin("Container.Refresh")
    

def favdel(url):
  debug(" FAVDEL url :"+url)
  textfile=""
  f=open(favdatei,'r')
  for line in f:
     if not url in line and not line=="\n":
      textfile=textfile+line
  f.close()
  f=open(favdatei,'w')
  f.write(textfile)
  f.close()
  xbmc.executebuiltin('Notification(7tv - Favoriten, [COLOR red]SERIE wurde gelöscht ![/COLOR],5000,'+icon+')')
  xbmc.executebuiltin("Container.Refresh")  

def listfav()  :
    if xbmcvfs.exists(favdatei):
        f=open(favdatei,'r')
        for line in f:
          spl=line.split('###')       
          addDir(name=spl[1], url=spl[0], mode="serie", iconimage=spl[2].strip(), desc="",title=spl[1],bild=spl[2].strip())
        f.close()
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
  
def  serie(url,bild="",title=""):
    debug("serie :"+url)
    debug("title :"+title)
    addDir("Alle Clips", url+"/alle-clips", "listvideos", "",series=title)      
    addDir("Ganze Folgen", url+"/ganze-folgen", "listvideos", "",series=title)
    found=0
    if xbmcvfs.exists(favdatei):
      f=open(favdatei,'r')     
      for line in f:
           if url in line:
              found=1
    if found==0:           
             addDir("Favoriten hinzufügen...", url, mode="favadd", iconimage="", desc="",title=title,bild=bild)
    else :
             addDir("Favoriten löschen...", url, mode="favdel", iconimage="", desc="")
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sendungsmenu():
    addDir("Sender", "sixx", "allsender", "")      
    addDir("Genres", "Anime", "allsender", "")   
    addDir("Alle Sendungen", baseurl+"/queue/format", "abisz", "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def abisz(url):
  url=url.replace(" ","+")
  debug("abisz URL :"+url)
  inhalt = geturl(url) 
  struktur = json.loads(inhalt) 
  debug("struktur --------")
  debug(struktur)
  for buchstabe in sorted(struktur["facet"], key=lambda str: (str=="#", str)):
     if   buchstabe=="#" :  
        ubuchstabe="0-9"
     else:
         ubuchstabe=buchstabe
     debug(ubuchstabe)
     addDir(buchstabe.title(), url+"/(letter)/"+ubuchstabe.encode("utf-8"), "jsonfile", "")  
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def jsonfile(url):
   debug("jsonfile url :"+url)
   inhalt = geturl(url) 
   struktur = json.loads(inhalt) 
   for element in struktur["entries"]:
     urlv=element["url"]
     image=element["images"][0]["url"]
     title=element["title"]
     addDir(title, baseurl+"/"+urlv, "serie", image,bild=image,title=title)       
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def allsender(begriff):
  debug("allsender url :"+begriff)
  url="http://www.7tv.de/sendungen-a-z"    
  inhalt = geturl(url) 
  inhalt = inhalt[:inhalt.find('<div class="tvshow-list" data-type="bentobox">')] 
  debug("####### "+inhalt)
  spl=inhalt.split('<ul class="tvshow-filter">')
  for i in range(1,len(spl),1):   
      entry=spl[i]
      debug("Entry :"+ entry)
      if not begriff in entry:
         debug("Nicht gefunden")
         continue
      filter=re.compile('<a href="#tvshow-all" data-href="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
      for url,name in filter:        
         url=baseurl+url
         addDir(name, url, "abisz", "")      
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def listvideos(url,series=""):
  datetitle=addon.getSetting("datetitle")
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<div class="main-zone">')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<!--googleoff: index-->')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      debug(" ##### ENTRY ####")
      debug(entry)
      urlv=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]
      try:
          teaser =re.compile(' <p class="teaser-info">(.+?)</p>', re.DOTALL).findall(entry)[0]        
          if not "Min." in teaser:
             aired=teaser
             duration=0
          else:
            aired=""
            laenge =re.compile('([0-9]+):([0-9]+) Min.', re.DOTALL).findall(teaser)           
            duration=int(laenge[0][0])*60+int(laenge[0][1])
      except:
             duration=0
             aired=""
      try: 
            staffel=re.compile('Staffel ([0-9]+)', re.DOTALL).findall(title)[0]  
      except :
             staffel=-1
      try: 
            episode=re.compile('Episode ([0-9]+)', re.DOTALL).findall(title)[0]  
      except :
             episode=-1   
      if not (("http://" in urlv) or ("https://" in urlv)):
        urlv=baseurl+urlv
      try:
          datum=re.compile('<p class="teaser-info">(.+?)</p>', re.DOTALL).findall(entry)[0]
      except:
          datum=""
      if datetitle=="true":
        title=datum+" - "+title
      addLink(title, urlv, "getvideoid", img,duration=duration,episode=episode,serie=series,aired=aired,staffel=staffel)      
    except:
      pass
  if "data-ajax-more=" in inhalt:
    nexturl=baseurl+re.compile('data-ajax-more="(.+?)"', re.DOTALL).findall(inhalt)[0]
    addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", nexturl, "listvideos", "",series="")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def getvideoid(client_location):
  debug("getvideoid client_location :"+client_location)
  inhalt = geturl(client_location)
  video_id=re.compile('"cid":(.+?),', re.DOTALL).findall(inhalt)[0]  

  source_id = None
  videos = playvideo(video_id, client_location,  source_id)

  
  

def playvideo(video_id,  client_location, source_id=None):
        from hashlib import sha1

        adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
        struktur = json.loads(adaptivaddon) 
        debug("adaptivaddon struktur :")
        debug(struktur)
        is_type=""
        if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.adaptive"
        if is_type=="":
          adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
          struktur = json.loads(adaptivaddon)           
          if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.mpd"                
        if is_type=="":
            access_token = 'h''b''b''t''v'  
            salt = '0''1''r''e''e''6''e''L''e''i''w''i''u''m''i''e''7''i''e''V''8''p''a''h''g''e''i''T''u''i''3''B'
            client_name='h''b''b''t''v'
        else:
          access_token = 'seventv-web'  
          salt = '01!8d8F_)r9]4s[qeuXfP%'
          client_name=''
#          dialog = xbmcgui.Dialog()
          #nr=dialog.ok("Inputstream", "Inputstream fehlt")
          #return ""
        print "is_type :"+is_type
        if source_id is None:
            source_id=0 
            json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?' \
                       'access_token=%s&client_location=%s&client_name=%s' \
                       % (video_id, access_token, client_location, client_name)
            json_data = geturl(json_url)
            json_data = json.loads(json_data) 
            print json_data
            print "........................"
            if not is_type=="":
              for stream in json_data['sources']:
                if  stream['mimetype']=='application/dash+xml': 
                  if int(source_id) <  int(stream['id']):               
                    source_id = stream['id']
              print source_id
            else:
              #debug("Protected : "+json_data["is_protected"])
              if json_data["is_protected"]==True:
                xbmc.executebuiltin('Notification("Inputstream", "DRM geschützte Folgen gehen nur mit Inputstream")')
                return
              else:
                for stream in json_data['sources']:
                  if  stream['mimetype']=='video/mp4':           
                    if int(source_id) <  int(stream['id']):                                   
                        source_id = stream['id']
                print source_id
        client_id_1 = salt[:2] + sha1(
            ''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode(
                'utf-8')).hexdigest()
           
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?' \
                   'access_token=%s&client_location=%s&client_name=%s&client_id=%s' \
                   % (video_id, access_token, client_location, client_name, client_id_1)            
        json_data = geturl(json_url)
        json_data = json.loads(json_data) 
        print json_data
        print "........................"
        server_id = json_data['server_id']
        
        #client_name = 'kolibri-1.2.5'    
        client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
        url_api_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (video_id, urllib.urlencode({
            'access_token': access_token,
            'client_id': client_id,
            'client_location': client_location,
            'client_name': client_name,
            'server_id': server_id,
            'source_ids': str(source_id),
        }))
        print "url_api_url :"+url_api_url
        json_data = geturl(url_api_url)
        json_data = json.loads(json_data) 
        debug ("---------------------------")
        debug( json_data)
        debug( "........................")
        max_id=0
        for stream in json_data["sources"]:
            ul=stream["url"]
            try:
                sid=re.compile('-tp([0-9]+).mp4', re.DOTALL).findall(ul)[0]
                id=int(sid)
                if max_id<id:
                    max_id=id
                    data=ul
            except:
              data=ul                                 
        #data=json_data["sources"][-1]["url"]               
        userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        addon_handle = int(sys.argv[1])
        listitem = xbmcgui.ListItem(path=data+"|"+userAgent)         
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        listitem.setProperty(is_type+".license_type", "com.widevine.alpha")
        listitem.setProperty(is_type+".manifest_type", "mpd")
        listitem.setProperty('inputstreamaddon', is_type)
        try:
          lic=json_data["drm"]["licenseAcquisitionUrl"]        
          token=json_data["drm"]["token"]                
          listitem.setProperty(is_type+'.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")            
        except:
           pass
        #listitem.setProperty('inputstreamaddon', 'inputstream.mpd')        
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
        #print "Daten lic :"+lic
        #print "Daten token :"+token
        #print "Daten data :"+data        
        return ""

def verpasstdatum():
  #http://www.7tv.de/missedshows/data/20161215
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30009), type=xbmcgui.INPUT_DATE)
   d=d.replace(' ','0')  
   d= d[6:] +  d[3:5] + d[:2]
   return verpasstdatummenu(d)

def verpasstdatummenu(d):
   url=baseurl+"/missedshows/data/"+d
   json_data = geturl(url)
   json_data = json.loads(json_data) 
   for sendername in json_data["entries"].keys():
     debug("sender "+sendername)
     addDir(sendername, url, "listdatum", "",sendername=sendername)  
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
     
def  listdatum(url,sendername):
   debug("listdatum ulr :"+url)
   debug("listdatum sender :"+ sendername)
   json_data = geturl(url)
   json_data = json.loads(json_data) 
   senderliste=json_data["entries"][sendername]
   for element in senderliste:
     title=element["title"]
     urlv=baseurl+element["url"]     
     dur=int(element["duration"]) /1000     
     serie=element["metadata"]["tvShowTitle"]
     time=element["airtime"]
     name=time + " " + serie + " - " + title
     
     addLink(name, urlv, "getvideoid", "") 
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   debug("senderliste")
   debug(senderliste)

def search():
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   d=d.replace(" ","+")
   debug("XYXXX :::")   
   #xbmc.executebuiltin('Notification("Inputstream", "DRM geschützte Folgen gehen nur mit Inputstream")')
   return searchmenu(d)
   debug("WWWW :::")
   
def searchmenu(d):
   #/type/episode/offset/1/limit/5
   d=d.replace(" ","+")
   addDir("Serien", url=baseurl +"/7tvsearch/search/query/"+ d , mode="searchtext", iconimage="" ,offset=0,limit=5,type="format")           
   addDir("Ganze Folgen", url=baseurl +"/7tvsearch/search/query/"+ d , mode="searchtext", iconimage="" ,offset=0,limit=5,type="episode")   
   addDir("Clips", url=baseurl +"/7tvsearch/search/query/"+ d , mode="searchtext", iconimage="" ,offset=0,limit=5,type="clip")   
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)         
  

def searchtext(url,offset,limit,type): 
   debug("Type :"+type) 
   urlx=url+"/type/"+ type + "/offset/"+offset +"/limit/"+limit
   debug("Searchtext ---------")
   debug(urlx)
   content = geturl(urlx)
   spl=content.split('<article class')
   for i in range(1,len(spl),1):
      entry=spl[i]  
      urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      urlt=baseurl+urlt
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('title="(.+?)"', re.DOTALL).findall(entry)[0]      
      if  type=="format":
        addDir(title, urlt, "serie", img,bild=img,title=title) 
      else:
        addLink(title, urlt, "getvideoid", img) 
   if i>5:
     addDir("[COLOR chartreuse]Nächste Seite  >>>[/COLOR]", url, mode="searchtext", iconimage="" ,offset=str(int(offset)+7),limit=limit,type=type)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def livetv(url):
   from hashlib import sha1
   cookie=temp+"/cookie.jar"
   cj = requests.cookies.RequestsCookieJar()   
   start="https://sso.7pass.de/connect/v1.0/authorize?response_type=code&client_id=53d94e076563326dd3000000&redirect_uri=mega-app://openidcallback&scope=openid%20email%20profile&prompt=register"
   content = requests.get(start, allow_redirects=False,verify=False,cookies=cj)
   content2=content.text.encode('utf-8')
   cj=content.cookies
   flow=re.compile('flow=(.+?)"', re.DOTALL).findall(content2)[0]   
    
   content = requests.get("https://7tvapp.7pass.de/api/session/init?version=1", allow_redirects=False,verify=False,cookies=cj)
   cj=content.cookies
   srf=cj["XSRF-TOKEN"]
   
   headers = {'User-Agent':         'Mozilla/5.0 (Linux; Android 6.0.1; SM-G900F Build/M4B30X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/51.0.2704.106 Mobile Safari/537.36',
   'X-Requested-With':              'de.prosiebensat1digital.seventv',
   'Referer':                      'https://7tvapp.7pass.de/?source=app&flow='+flow,
   'Content-Type':                  'application/json;charset=UTF-8',
   'Origin':                        'https://7tvapp.7pass.de',
   'X-XSRF-TOKEN':srf
   }
   values = {
      'email' : "andreas@vogler.name",
   }       
   content = requests.post("https://7tvapp.7pass.de/api/session/checkMail?version=1",data=json.dumps(values), allow_redirects=False,verify=False,cookies=cj,headers=headers)
   #cj=content.cookies   
   
   content = requests.get("https://www.7pass.de/connect/v1.0/login?flow="+flow, allow_redirects=False,verify=False,cookies=cj,headers=headers)
   content2=content.text.encode('utf-8')
   #cj=content.cookies
   #debug("content2 :")
   #debug(content2)
   #exit
   values = {'flow' : flow,
      '_csrf' : srf,
      'login' : "andreas@vogler.name",        
      'password' : "Test1t",
   }      
   headers = {'User-Agent':         'Mozilla/5.0 (Linux; Android 6.0.1; SM-G900F Build/M4B30X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/51.0.2704.106 Mobile Safari/537.36',
   'X-Requested-With':              'de.prosiebensat1digital.seventv',
   'Referer':                      'https://www.7pass.de/connect/v1.0/login?flow='+flow,
   'Content-Type':                  'application/x-www-form-urlencoded',  
   'Origin':                        'https://7tvapp.7pass.de',
   }   
   content = requests.post("https://www.7pass.de/connect/v1.0/login", data=values, allow_redirects=False,verify=False,cookies=cj,headers=headers)
   content2=content.text.encode('utf-8')
   newurl=re.compile('href="(.+?)"', re.DOTALL).findall(content2)[0]
   newurl="https://www.7pass.de/connect/v1.0/"+newurl.replace("&amp;","&")
   debug("newurl :"+newurl)
   content = requests.get(newurl, allow_redirects=False,verify=False,cookies=cj,headers=headers)
   content2=content.text.encode('utf-8')
   code=re.compile('code=(.+?)"', re.DOTALL).findall(content2)[0]
   newurl="https://sso.7pass.de/connect/v1.0/token?code="+code+"&client_id=53d94e076563326dd3000000&client_secret=34af9cf73ee141d04ce32c81b6e988ecb2d9a7751401441ad9018e687d0773c4&redirect_uri=mega-app://openidcallback&grant_type=authorization_code"
   content = requests.post(newurl, allow_redirects=False,verify=False,cookies=cj,headers=headers)
   content2=content.text.encode('utf-8')
   _TOKEN=re.compile('"access_token":"(.+?)"', re.DOTALL).findall(content2)[0]   
   
   #_TOKEN = 'prosieben'
   _SALT = '01!8d8F_)r9]4s[qeuXfP%'
   _CLIENT_NAME = 'kolibri-2.0.19-splec4'
   clip_id="343487726"
   client_location="http://www.prosieben.de/livestream?v=343487726"
   access_token = _SALT[:2] + sha1(''.join([clip_id, _SALT, _TOKEN, client_location, _SALT, _CLIENT_NAME]).encode('utf-8')).hexdigest()
   newurl="http://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=seventv-app&client_location=http%3A%2F%2Fwww.prosieben.de&client_token="+access_token+"&property_name=prosieben-de-24x7"
   content = requests.get(newurl, allow_redirects=False,verify=False,cookies=cj,headers=headers)
   content2=content.text.encode('utf-8')
   

   debug("++++")
   debug(content2)

   #client_location="http://www.prosieben.de/livestream?v=39790251"
   #clientname="kolibri-2.0.19-splec4"
   #salt = '01!8d8F_)r9]4s[qeuXfP%'
   #clipid="39790251" 
   #json_url="http://vas.sim-technik.de/vas/live/v2/videos/"+clipid+"/sources?access_token="+access_token+"&client_location="+client_location+"&client_name=kolibri-2.0.19-splec4&ids=605741"
   #json_data = geturl(json_url)
   #debug("-------------")
   #debug(json_data)
  # client_id = salt[:2] + sha1(''.join([clipid, salt, access_token, client_location, salt, clientname]).encode('utf-8')).hexdigest()
  # cj.save(cookie,ignore_discard=True, ignore_expires=True) 
   
# Haupt Menu Anzeigen      
if mode is '':
    addDir("Sender", "Sender", 'senderlist', "") 
    addDir("Sendungen A-Z", url+"/ganze-folgen", "sendungsmenu", "")  
    addDir("Sendungen nach Datum", "", "verpasstdatum", "")  
    addDir("Suche","","search","")
    addDir("Favoriten", "Favoriten", 'listfav', "") 
    addDir("Einstellungen", "", 'Settings', "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'senderlist':
          senderlist()
  if mode == 'sender':
          sender(url)
  if mode == 'belibtesendungen':
          belibtesendungen(url)
  if mode == 'serie':
          serie(url,bild,title)       
  if mode == 'listvideos':
          listvideos(url,series)       
  if mode == 'getvideoid':
          getvideoid(url)     
  if mode == 'ganzefolgensender':
          ganzefolgensender(url)                      
  if mode == 'sendungsmenu':
          sendungsmenu()                  
  if mode == 'allsender':
          allsender(url)                          
  if mode == 'abisz':
          abisz(url)                                             
  if mode == 'jsonfile':
          jsonfile(url)                                                               
  if mode == 'verpasstdatum':
          verpasstdatum()   
  if mode == 'listdatum':
          listdatum(url,sendername) 
  if mode == 'search':
          search()
  if mode ==  'searchtext':
          searchtext(url,offset,limit,type)
  if mode ==  'searchmenu':
          searchmenu(url)
  if mode ==  'verpasstdatummenu':
          verpasstdatummenu(url)          
  if mode == 'favadd':          
          favadd(url,title,bild)       
  if mode == 'livetv':          
          livetv(url)              
  if mode == 'favdel':          
          favdel(url)                             
  if mode == 'listfav':          
          listfav()     

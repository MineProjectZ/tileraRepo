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
import base64
import ssl
import hashlib
from collections import OrderedDict


# Setting Variablen Des Plugins

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
cj = cookielib.LWPCookieJar();
xbmcplugin.setContent(addon_handle, 'tvshows')  

def AddonEnabled(addon_id):
    result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,\
                                   "params":{"addonid":"%s", "properties": ["enabled"]}}' % addon_id)
    return False if '"error":' in result or '"enabled":false' in result else True

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

is_addon=""
inputstreamcomp=addon.getSetting("inputstreamcomp") 
if AddonEnabled('inputstream.adaptive'):
    is_addon = 'inputstream.adaptive'    

if not is_addon and not inputstreamcomp=="true":
        debug('No Inputstream Addon found or activated')
        debug('inputstreamcomp')
        debug(inputstreamcomp)
        dialog = xbmcgui.Dialog()
        dialog.notification("Inpuitstream Fehler", 'Inputstream nicht eingeschaltet', xbmcgui.NOTIFICATION_ERROR)
        exit    

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
if not xbmcvfs.exists(temp):  
  xbmcvfs.mkdirs(temp)


cert=addon.getSetting("cert")
debug("##")
debug(cert)
if cert=="false":
  try:
      debug("#######")      
      _create_unverified_https_context = ssl._create_unverified_context
  except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
      pass
  else:
    # Handle target environment that doesn't support HTTPS verification
      ssl._create_default_https_context = _create_unverified_https_context


try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

cachezeit=addon.getSetting("cachetime")   
cache = StorageServer.StorageServer("plugin.video.rtlnow", cachezeit) # (Your plugin name, Cache time in hours

     
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", defaultBackground)
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  return u,liz,True
	#ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	#return ok
  
def getUrl(url,data="x",header=""):
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
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
             #debug( e.code   )
             cc=e.read()
             debug("Error : " +cc)

        opener.close()
        return content    

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
def addDir(name, url, mode, iconimage, desc="", duration="",nummer=0):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&nummer="+str(nummer)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({ 'fanart': iconimage })
    liz.setArt({ 'thumb': iconimage })
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    #ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return u,liz,True



       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
nummer = urllib.unquote_plus(params.get('nummer', ''))
name = urllib.unquote_plus(params.get('name', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'    
def serien(url):
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
  menu=[]
  debug("Serien New Menu")  
  debug(url)  
  
  if "maxPerPage" in url:  
   seitennr=1
  else:
   seitennr=0  
  counter=1
  anzahl=1
  while (anzahl>0):  
    if seitennr>0:
        newurl=url+"&page="+str(seitennr)
    else:
        newurl=url        
    content = cache.cacheFunction(getUrl,newurl) 
    serienliste = json.loads(content, object_pairs_hook=OrderedDict)  
    freeonly=addon.getSetting("freeonly") 
    items=[]
    try:
        liste=serienliste["movies"]["items"]
    except:
        liste=serienliste["items"]
    for serieelement in liste:
        title=serieelement["title"].encode('utf-8')
        debug(title)
        seoUrl=serieelement["seoUrl"]
        try:
        #Genre
            serieelement=serieelement["format"]
        except:
            pass
        try:
            logo=serieelement["defaultLogo"]
            desc=serieelement["infoTextLong"]
            freeep=serieelement["hasFreeEpisodes"]
        except:
            logo=""
            desc=""
            freeep="true"
        if (freeep==True or freeonly=="false") :
            menu.append(addDir(title , url=str(seoUrl), mode="rubrik", iconimage=logo,duration="",desc=desc))
        counter+=1
    debug("Counter :"+str(counter))
    try:
            anzahl=serienliste["total"]-counter
    except: 
            anzahl=0
    debug("Anzahl :### "+str(anzahl))
    seitennr=seitennr+1
     
  xbmcplugin.addDirectoryItems(addon_handle,menu)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    

def rubrik(name) :
  menu=[]
  freeonly=addon.getSetting("freeonly")
  kodi18=addon.getSetting("kodi18")
  debug("Rubrik New Menu")
  #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)   
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
  #http://api.tvnow.de/v3/formats/seo?fields=*,.*,formatTabs.*,formatTabs.headline&name=chicago-fire
  basurl="http://api.tvnow.de/v3/formats/seo?fields="
  div=urllib.quote_plus("*,.*,formatTabs.*,formatTabs.headline")
  endeurl="&name="+name
  url=basurl+div+endeurl
  debug(url)
  content = cache.cacheFunction(getUrl,url)      
  kapitelliste = json.loads(content, object_pairs_hook=OrderedDict)   
  try:
    serienanzahl=kapitelliste["formatTabs"]["total"]  
    debug("serienanzahl gefunden :"+ str(serienanzahl))
  except:
    serienanzahl=1
   
  if (serienanzahl==1):
    try:
      idd=kapitelliste["formatTabs"]["items"][0]["id"]   
    except:
      idd=kapitelliste["id"]
    uurl="http://api.tvnow.de/v3/formatlists/"+str(idd)+"?maxPerPage=500&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures"
    staffel(str(idd),uurl)
  else:
    for kapitel in kapitelliste["formatTabs"]["items"]:
      debug(kapitel)       
      idd=kapitel["id"]
      name=kapitel["headline"]      
      urlx="http://api.tvnow.de/v3/formatlists/"+str(idd)+"?maxPerPage=500&fields=formatTabPages.container.movies.free,formatTabPages.container.movies.isDrm"      
      content2 = cache.cacheFunction(getUrl,urlx)    
      if ('"free":true' in content2 or freeonly=="false") and ('"isDrm":false' in content2  or kodi18 == "true"):
      #      debug(staffelinfo)
          uurl="http://api.tvnow.de/v3/formatlists/"+str(idd)+"?maxPerPage=500&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures"
          menu.append(addDir(name , url=uurl,nummer=str(idd), mode="staffel", iconimage="",duration="",desc=""))        
  xbmcplugin.addDirectoryItems(addon_handle,menu)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)
def get_min(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s) /60
        
def staffel(idd,url) :    
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
  menu=[]
  xy=[]  
  global cache
  ret,token=login()
  debug("Lade staffel neu")
  #http://api.tvnow.de/v3/formatlists/41018?maxPerPage=5000&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1http://api.tvnow.de/v3/formatlists/41016?maxPerPage=9&fields=*,formatTabPages.*,formatTabPages.container.*,formatTabPages.container.movies.*,formatTabPages.container.movies.format.*,formatTabPages.container.movies.paymentPaytypes.*,formatTabPages.container.movies.pictures&page=1  
  debug("staffel :"+url)
  try:
     content = cache.cacheFunction(getUrl,url)
     folgen = json.loads(content, object_pairs_hook=OrderedDict)
     li=folgen["formatTabPages"]     
  except:  
    url='http://api.tvnow.de/v3/movies?filter={%22FormatId%22:'+idd+'}&fields=*,format,paymentPaytypes,pictures,trailers&maxPerPage=500&order=BroadcastStartDate%20desc2B'+idd+'}%26fields%3D*%2Cformat%2CpaymentPaytypes%2Cpictures%2Ctrailers%26maxPerPage%3D50%26order%3DBroadcastStartDate%2Bdesc'
    debug("NEWURL :"+url)
    content = cache.cacheFunction(getUrl,url) 
    li = json.loads(content, object_pairs_hook=OrderedDict)
  
  liste=li["items"]
  debug(liste)
  menu=[]
  menulist=""
  for element in liste:      
      debug("###")
      debug(element)      
      try:
        if element["container"]["movies"]==None:
          continue
        elemente2=element["container"]["movies"]["items"]
        debug("ELEMENT2")
      except:        
        elemente2=[element]
      for folge in elemente2:         
        debug("++")
        debug(folge)        
        freeonly=addon.getSetting("freeonly")        
        kodi18=addon.getSetting("kodi18")
        try:
          debug(folge["isDrm"])
          debug(folge["free"])
        except:
           continue
        if ( not folge["isDrm"]==True or kodi18=="true") and ( folge["free"]==True or freeonly=="false"):
          debug("--")
          name=folge["title"]         
          idd=folge["id"]
          bild="https://ais.tvnow.de/tvnow/movie/"+str(idd)+"/600x600/title.jpg"
          stream=folge["manifest"]["dashclear"].strip()
          if folge["isDrm"]==True:
            try:
                  streamcode=folge["manifest"]["dash"].strip()
            except:
                  streamcode="0"
          else:
              streamcode="0"
          laenge=get_sec(folge["duration"])          
          laengemin=get_min(folge["duration"])          
          sstaffel=str(folge["season"])
          folgenr=str(folge["episode"]) 
          plot=folge["articleLong"] 
          plotshort=folge["articleShort"]
          startdate=folge["broadcastStartDate"]    
          tagline=folge["teaserText"]           
          deeplink=folge["deeplinkUrl"] 
          try:          
            type=folge["format"]["categoryId"]
          except:
            type=""
          ftype="episode"
          if type=="serie":
            ftype="episode"
          if type=="film":
            ftype="movie"            
          zusatz=" ("+startdate+ " )"
          title=name+zusatz
          haswert=hashlib.md5(title.encode('utf-8')).hexdigest()
          zeile=haswert+"###"+stream+"###"+title+"###"+bild+"###"+str(laenge)+"###"+plot+"###"+plotshort+"###"+tagline+"###"+ftype+"###"+streamcode+"###"+str(token)+"###"+str(deeplink)+"###"
          menulist=menulist+zeile.replace("\n"," ").encode('utf-8')+"\n"             
          listitem = xbmcgui.ListItem(path="plugin://plugin.video.rtlnow/?nummer="+haswert+"&mode=hashplay",label=title,iconImage=bild,thumbnailImage=bild)
          listitem.setProperty('IsPlayable', 'true')
          listitem.addStreamInfo('video', {'duration': laenge,'plot' : plot,'plotoutline' : plotshort,'tagline':tagline,'mediatype':ftype })
          listitem.setInfo(type="Video", infoLabels={'duration': laenge,"Title": title, "Plot": plot,'plotoutline': plotshort,'tagline':tagline,'mediatype':ftype ,"episode": folgenr, "season":sstaffel,"sorttitle":"S"+sstaffel+"E"+folgenr+" "+title})                    
          #listitem.setInfo(type='video')          
          xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="plugin://plugin.video.rtlnow/?nummer="+haswert+"&mode=hashplay", listitem=listitem)
          #addLink(name, stream, "playvideo", bild)          
          xbmcplugin.addDirectoryItems(addon_handle,menu) 
  f = open( os.path.join(temp,"menu.txt"), 'w')  
  f.write(menulist)
  f.close()          
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

 
def hashplay(idd):
  debug("hashplay url :"+idd)
  f=xbmcvfs.File( os.path.join(temp,"menu.txt"),"r")   
  daten=f.read()
  zeilen=daten.split('\n')  
  for zeile in zeilen:    
    debug ("Read Zeile :"+zeile)
    felder=zeile.split("###")
    debug("Felder ")
    debug(felder)
    if felder[0]==idd:    
          debug("Gefunden")
          stream=felder[1]
          title=felder[2]          
          bild=felder[3]                      
          laenge=felder[4] 
          plot=felder[5] 
          plotshort=felder[6] 
          tagline=felder[7] 
          ftype=felder[8] 
          streamcode=felder[9] 
          token=felder[10] 
          deeplink=felder[11] 
          kodi18=addon.getSetting("kodi18")
          if kodi18=="true" :
             if not streamcode=="0":
               stream=streamcode
               debug("STREAM : #" +stream +"#")
          content = getUrl(deeplink)
          referer=re.compile("webLink = '(.+?)'", re.DOTALL).findall(content)[0]                
          headerfelder="user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36&Referer="+referer
          if kodi18=="true" :                
                listitem = xbmcgui.ListItem(path=stream+"|"+headerfelder,label=title,iconImage=bild,thumbnailImage=bild)
          else:
                listitem = xbmcgui.ListItem(path=stream,label=title,iconImage=bild,thumbnailImage=bild)
          listitem.setProperty('IsPlayable', 'true')
          listitem.addStreamInfo('video', {'duration': laenge,'plot' : plot,'plotoutline' : plotshort,'tagline':tagline,'mediatype':ftype })          
          listitem.setInfo(type="Video", infoLabels={'duration': laenge,"Title": title, "Plot": plot,'plotoutline': plotshort,'tagline':tagline,'mediatype':ftype})          
          listitem.setProperty(u'IsPlayable', u'true')
          listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
          listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
          if kodi18=="true" :
              if token=="0" and not streamcode=="0":
                    dialog = xbmcgui.Dialog()
                    dialog.notification("Login Notwendig", 'Es ist min. Ein Freier Watchbox account Notwendig', xbmcgui.NOTIFICATION_ERROR)
              else:               
                licstring='https://widevine.rtl.de/index/proxy|x-auth-token='+token+"&"+headerfelder+"&Content-Type=|R{SSM}|"
                debug(licstring)
                listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')                
                listitem.setProperty('inputstream.adaptive.license_key', licstring)                
                debug("LICENSE: " + licstring)      
          if kodi18=="true" :                
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=stream+"|"+headerfelder, listitem=listitem)
          else:
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=stream, listitem=listitem)
          xbmcplugin.setResolvedUrl(addon_handle,True, listitem)    
          #addLink(name, stream, "playvideo", bild)          
          
          
          
       
def  login():
  debug("Start login")
  username=addon.getSetting("user")
  password=addon.getSetting("pass")
  if username=="" and password=="":
     debug("Kein Password")
     addon.setSetting("freeonly", "true")
     return 0,"0"
  url="https://api.tvnow.de/v3/backend/login"
  values = {'password' : password,
        'email' : username,        
    }
  data = urllib.urlencode(values)
  debug("######LOGINDATA#####")
  debug(data)
  try:
    content = getUrl(url,data=data)         
    userdata = json.loads(content)
    try:
       token=userdata["token"]
    except:
     return 0,"0"
    debug(userdata)
    debug("### Subscriptioon ### "+ str(userdata["subscriptionState"]))
    if userdata["subscriptionState"]==5:      
      debug("Login ok")
      addon.setSetting("freeonly", "false")

      return 1,token
    else :      
      addon.setSetting("freeonly", "true")
      return 1,token
  except:
      debug("Wrong Login")
      addon.setSetting("freeonly", "true")
      return 0,"0"
  debug(content)
  
     
def genre(url):
    menu=[]
    #https://api.tvnow.de/v3/channels/station/rtl?fields=*&filter=%7B%22Active%22:true%7D&maxPerPage=500&page=1     
    urln="https://api.tvnow.de/v3/channels/station/"+url+"?fields=*&filter=%7B%22Active%22:true%7D&maxPerPage=500"
    content = cache.cacheFunction(getUrl,urln)      
    genres = json.loads(content, object_pairs_hook=OrderedDict)
    for genre in genres["items"]:
       id=genre["id"]
       name=genre["title"]
       image="https://ais.tvnow.de/tvnow/cms/"+genre["defaultImage"]+"/300x169/image2.jpg"
       menu.append(addDir(name , url=url, mode="listgenre", iconimage=image,duration="",desc="",nummer=id))   
    xbmcplugin.addDirectoryItems(addon_handle,menu)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    
    
def index():
    menu=[]
    ret,token=login()
    freeonly=addon.getSetting("freeonly")
    kodi18=addon.getSetting("kodi18")
    menu.append(addDir("Nach Sendern", "", 'sendermenu', ""))      
    menu.append(addDir("Themen" , url="rtl", mode="genre", iconimage="",duration="",desc=""))
    menu.append(addDir("Rubriken" , url="", mode="katalog", iconimage="",duration="",desc=""))
    menu.append(addDir("Genres" , url="", mode="genreliste", iconimage="",duration="",desc=""))
    if ret==1 and kodi18 == "true":
        menu.append(addDir("LiveTV",url="", mode="livetv", iconimage="",duration="",desc=""))    
    menu.append(addDir("Cache Loeschen", "", 'clearcache', ""))    
    menu.append(addDir("Settings", "", 'Settings', ""))    
    menu.append(addDir("Inputstream Einstellungen", "", 'inputsettings', ""))        
    xbmcplugin.addDirectoryItems(addon_handle,menu)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)        

    
def sendermenu():
    debug("START")    
    menu=[]
    debug("New MENU")
    ret,token=login()
    content = cache.cacheFunction(getUrl,"https://api.tvnow.de/v3/settings")      
    settings = json.loads(content, object_pairs_hook=OrderedDict)    
    aliases=settings["settings"]["nowtv"]["local"]["stations"]["aliases"]  
    for name,value in aliases.items():
      if not name=="toggoplus" :
          newimg=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),"logos",name +".png")
          menu.append(addDir(value , url=name, mode="serien", iconimage=newimg,duration="",desc=""))   
    xbmcplugin.addDirectoryItems(addon_handle,menu)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def genremenu(url):
     menu=[]     
     content = cache.cacheFunction(getUrl,url)      
     genres = json.loads(content)
     if genres["total"]>1:
       menu.append(addDir("Alle Serien" , url=url, mode="serien", iconimage="",duration="",desc=""))   
       menu.append(addDir("Genres" , url=url, mode="genre", iconimage="",duration="",desc=""))   
       xbmcplugin.addDirectoryItems(addon_handle,menu)
       xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    


       
def katalog():
  menu=[]
  url="https://api.tvnow.de/v3/pages/nowtv/tvnow?fields=teaserSets.headline,teaserSets.id"
  content = cache.cacheFunction(getUrl,url)     
  objekte = json.loads(content ,object_pairs_hook=OrderedDict)
  liste=objekte["teaserSets"]["items"]
  for serie in liste:
     name=serie["headline"]
     idd=str(serie["id"])
     if not idd=="2255" and not idd=="7619":
       menu.append(addDir(name , url=str(idd), mode="katalogliste", iconimage="",duration="",desc=""))
  xbmcplugin.addDirectoryItems(addon_handle,menu)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)        
def katalogliste(idd)   :    
   menu=[]
   url="https://api.tvnow.de/v3/teasersets/"+idd+"?fields=[%22teaserSetInformations%22,[%22format%22,[%22id%22,%22title%22,%22seoUrl%22,%22defaultDvdImage%22,%22infoText%22]]]"
   debug("katalogliste")
   debug("URL :"+url)
   content = cache.cacheFunction(getUrl,url)     
   objekte = json.loads(content, object_pairs_hook=OrderedDict)
   liste=objekte["teaserSetInformations"]["items"]
   for serie in liste:
     debug("---")
     debug(serie)
     id=serie["format"]["id"]
     seoUrl=serie["format"]["seoUrl"]
     title=serie["format"]["title"]
     logo=serie["format"]["defaultDvdImage"]
     desc=serie["format"]["infoText"]
     menu.append(addDir(title , url=str(seoUrl), mode="rubrik", iconimage=logo,duration="",desc=desc))
   xbmcplugin.addDirectoryItems(addon_handle,menu)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
       
def clearcache():
    debug("CLear Cache")
    cache.delete("%")
    
def genreliste():
 menu=[] 
 url="https://cdn.static-fra.de/tvnow/app/e81664b7.main.js"    
 content = cache.cacheFunction(getUrl,url)     
 liste=re.compile('return\[([^\]]+?)\]\}return', re.DOTALL).findall(content)[0]
 elemente=liste.replace('"',"").split(",")
 for element in elemente:
   uri="https://api.tvnow.de/v3/formats/genre/"+element+"?fields=*&filter=%7B%22station%22:%22none%22%7D&maxPerPage=500&order=NameLong+asc"
   menu.append(addDir(element , url=uri, mode="lsserie", iconimage="",duration="",desc=""))
 xbmcplugin.addDirectoryItems(addon_handle,menu)
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
    
def inputsettings()    :
  xbmcaddon.Addon(is_addon).openSettings()
  
def livetv():
    ret,token=login()    
    if token=="0":
        dialog = xbmcgui.Dialog()
        dialog.notification("Fuer Plus", 'Nur fuer Plusmitglieder', xbmcgui.NOTIFICATION_ERROR)
        return    
    url="https://api.tvnow.de/v3/epgs/movies/nownext?fields=*,nowNextEpgTeasers.*,nowNextEpgMovies.*"
    content = getUrl(url) 
    objekte = json.loads(content, object_pairs_hook=OrderedDict)
    for element in objekte["items"]:
       try:
        name = element["name"]       
        url  = element["nowNextEpgMovies"]["items"][0]["manifest"]["dash"]
        image=element["nowNextEpgMovies"]["items"][0]["image"]
       except:
         continue
       referer="https://www.tvnow.de/"+name+"/live-tv" 
       headerfelder="user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36&Referer="+referer         
       listitem = xbmcgui.ListItem(path=url+"||"+headerfelder,label=name,iconImage=image,thumbnailImage=image)
       listitem.setProperty('IsPlayable', 'true')          
       listitem.setInfo(type="Video", infoLabels={"Title": name })                 
       listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
       listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')                        
       licstring='https://widevine.rtl.de/index/proxy|x-auth-token='+token+"&"+headerfelder+"&Content-Type=|R{SSM}|"
       listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')                
       listitem.setProperty('inputstream.adaptive.license_key', licstring)                
       debug("LICENSE: " + licstring)                              
       xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url+"||"+headerfelder, listitem=listitem)
    xbmcplugin.setResolvedUrl(addon_handle,True, listitem)    

#OPTIONS https://api.tvnow.de/v3/formats/genre/Crime?fields=*&filter=%7B%22station%22:%22none%22%7D&maxPerPage=50&order=NameLong+asc&page=1
    
# Haupt Menu Anzeigen      
if mode is '':     
    index()    
else:  
  if mode == 'listgenre':
          urln="https://api.tvnow.de/v3/channels/"+nummer+"?fields=[%22*%22,%22movies%22,[%22id%22,%22title%22,%22episode%22,%22broadcastStartDate%22,%22blockadeText%22,%22free%22,%22replaceMovieInformation%22,%22seoUrl%22,%22pictures%22,[%22*%22],%22packages%22,[%22*%22],%22format%22,[%22*%22]]]"
          serien(urln)   
  if mode == 'serien':
          starturl='http://api.tvnow.de/v3/formats?filter='
          filter=urllib.quote_plus('{"Disabled": "0", "Station":"' + url +'"}')
          urln=starturl+filter+'&fields=title,id,seoUrl,defaultLogo,infoTextLong,hasFreeEpisodes,categoryId&maxPerPage=500'
          serien(urln)     
  if mode == 'lsserie':
           serien(url)
  if mode == 'rubrik':
          rubrik(url)             
  if mode == 'staffel':
          url="http://api.tvnow.de/v3/formatlists/"+nummer+"?maxPerPage=500&fields=[%22formatTabPages%22,[%22container%22,[%22movies%22,[%22free%22,%22isDrm%22,%22title%22,%22id%22,%22deeplinkUrl%22,%22manifest%22,[%22dashclear%22,%22dash%22],%22duration%22,%22season%22,%22episode%22,%22articleLong%22,%22articleShort%22,%22broadcastStartDate%22,%22teaserText%22,%22format%22,[%22categoryId%22]]]]]"
          staffel(nummer,url)             
  if mode == 'playvideo':
          playvideo(url) 
  if mode == 'clearcache':
          clearcache()           
  if mode == 'sendermenu':
          sendermenu()            
  if mode == 'genre':
          genre(url) 
  if mode == 'katalogliste':
          katalogliste(url)           
  if mode == 'katalog':
          katalog()             
  if mode == 'hashplay':
          hashplay(nummer)  
  if mode == 'genreliste':
             genreliste() 
  if mode == 'Settings':
          addon.openSettings()     
  if mode == 'inputsettings':
          inputsettings()                       
  if mode == 'livetv':
          livetv()

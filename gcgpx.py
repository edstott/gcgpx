import requests
import bs4
import re
import glob
import os
import time
import xml.dom.minidom as minidom
import random
import sys


defaultpath = 'H:\\gpx\\27-4-15'
filemask = 'GC*.GPX'
gpxage = 24*3600
maxdelay = 10.0

cipher = {}
for i in range(13):
	cipher[chr(i+65)] = chr(i+78)
	cipher[chr(i+78)] = chr(i+65)
	cipher[chr(i+97)] = chr(i+110)
	cipher[chr(i+110)] = chr(i+97)
cipherre = re.compile('|'.join(cipher.keys()))

if len(sys.argv)>1:
	path = sys.argv[1]
else:
	path = defaultpath

searchpath = os.path.join(path,filemask)	
print('Searching '+searchpath)

files = [filename for filename in glob.glob(searchpath) if time.time() - os.stat(filename).st_mtime < gpxage]

print('Found '+str(len(files))+' gpx files')

for filename in files:
	
	print('Processing '+filename)
	gpxdom = minidom.parse(filename)
	
	try:
		geocode = gpxdom.getElementsByTagName('wpt')[0].getElementsByTagName('name')[0].firstChild.data
	except AttributeError:
		print('Did not find reference code in '+filename)
		continue
		
	try:
		sdescnode = gpxdom.getElementsByTagName('groundspeak:short_description')[0].firstChild
	except:
		print('Did not find short description node in  '+filename)
		sdescnode = None
		
	try:
		ldescnode = gpxdom.getElementsByTagName('groundspeak:long_description')[0].firstChild
	except:
		print('Did not find long description node in  '+filename)
		ldescnode = None
		
	try:
		hintnode = gpxdom.getElementsByTagName('groundspeak:encoded_hints')[0].firstChild
	except:
		print('Did not find hint node in  '+filename)
		hintnode = None
	
	geopage = requests.get('http://www.geocaching.com/geocache/'+geocode)
	geohtml = bs4.BeautifulSoup(geopage.text, "html.parser")

	hintobj = geohtml.find("div",id="div_hint")
	if hintobj is None:
		print('Did not find hint for '+geocode)
		hint = ""
	elif hintnode is not None:
		hint = re.search("\s*(.*)",hintobj.text).group(1)
		hint = cipherre.sub(lambda x: cipher[x.group()], hint)
		hintnode.data = hint
		
	shortdescobj = geohtml.find("span",id="ctl00_ContentBody_ShortDescription")
	if shortdescobj is None:
		print('Did not find short description for '+geocode)
		shortdesc = ""
	elif sdescnode is not None:
		sdescnode.data = shortdescobj.text
		
	longdescobj = geohtml.find("span",id="ctl00_ContentBody_LongDescription")
	if longdescobj is None:
		print('Did not find long description for '+geocode)
		longdesc = ""
	elif ldescnode is not None:
		ldescnode.data = longdescobj.text
	
	gpxfile = open(os.path.join(path,geocode+'.gpx'),'wb')
	gpxfile.write(gpxdom.toxml('utf-8'))
	gpxfile.close()
	
	time.sleep(random.random()*maxdelay)
	

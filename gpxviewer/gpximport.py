#
#  gpximport.py - Used to import GPX XML files into applications
#
#  Copyright (C) 2009 Andrew Gee
#
#  GPX Viewer is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  GPX Viewer is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.

#
#  If you're having any problems, don't hesitate to contact: andrew@andrewgee.org
#   

try:
	from xml.etree import cElementTree as ET
except ImportError:
	from xml.etree import ElementTree as ET  # NOQA

from utils.iso8601 import parse_date as parse_xml_date

__all__ = ["import_gpx_trace"]


GPX_NS = '{http://www.topografix.com/GPX/1/1}'


class ParseError(Exception):
    """Raised when there is a problem parsing any part of the GPX XML"""
    pass


def match_node(node, tag):
	return node.tag == GPX_NS + tag


def fetch_metadata(node):
	metadata = {}
	for mnode in node.getchildren():
		if match_node(mnode, 'name'):
			metadata['name'] = mnode.text
			
		elif match_node(mnode, 'desc'):
			try:
				metadata['description'] = mnode.text
			except:
				metadata['description'] = "" #no description
			
		elif match_node(mnode, 'time'):
			metadata['time'] = mnode.tag
			
		elif match_node(mnode, 'author'):
			metadata['author'] = {}
			for anode in mnode.getchildren():
				if match_node(anode, 'name'):
					metadata['author']['name'] = anode.text
				elif match_node(anode, 'email'):
					metadata['author']['email'] = anode.text
				elif match_node(anode, 'link'):
					metadata['author']['link'] = anode.text
					
		elif match_node(mnode, 'copyright'):
			metadata['copyright'] = {}
			if mnode.get('author'):
				metadata['copyright']['author'] = mnode.get('author')
			for cnode in mnode.getchildren():
				if match_node(cnode, 'year'):
					metadata['copyright']['year'] = cnode.text
				elif match_node(cnode, 'license'):
					metadata['copyright']['license'] = cnode.text
					
		elif match_node(mnode, 'link'):
			metadata['link'] = {}
			if mnode.get('href'):
				metadata['link']['href'] = mnode.get('href')
			for lnode in mnode.getchildren():
				if match_node(lnode, 'text'):
					metadata['link']['text'] = lnode.text
				elif match_node(lnode, 'type'):
					metadata['link']['type'] = lnode.text
					
		elif match_node(mnode, 'time'):
			metadata['time'] = parse_xml_date(mnode.text)
					
		elif match_node(mnode, 'keywords'):
			metadata['keywords'] = mnode.text
		
	return metadata
	
def fetch_track_point(tsnode):
	point = {}
	if tsnode.get('lat') and tsnode.get('lon'):
		point['lat'] = float(tsnode.get('lat'))
		point['lon'] = float(tsnode.get('lon'))
	
	for tpnode in tsnode.getchildren():
		if match_node(tpnode, 'ele'):
			point['ele'] = float(tpnode.text)
		elif match_node(tpnode, 'desc'):
			point['description'] = tpnode.text
		elif match_node(tpnode, 'time'):
			point['time'] = parse_xml_date(tpnode.text)
		elif match_node(tpnode, 'name'):
			point['name'] = tpnode.text
		
	return point
	
def fetch_track_segment(tnode):
	trkseg = {}
	trkseg['points'] = []
	for tsnode in tnode.getchildren():
		if match_node(tsnode, 'trkpt'):
			trkseg['points'].append(fetch_track_point(tsnode))
	
	return trkseg
	
def fetch_track(node):
	track = {}
	track['segments'] = []
	for tnode in node.getchildren():
		if match_node(tnode, 'trkseg'):
		  track_segment = fetch_track_segment(tnode)
		  if len(track_segment['points']) > 0:
		    track['segments'].append(fetch_track_segment(tnode))
		
	return track
	
def import_gpx_trace(filename):
	doc = ET.parse(filename)

	doce = doc.getroot()

	if not match_node(doce, 'gpx'):
		raise Exception
		
	trace = {}
	trace['filename'] = filename
	trace['tracks'] = []
	
	try:
		e = doce.getchildren()
		for node in e:
			if match_node(node, 'metadata'):
				trace['metadata'] = fetch_metadata(node)
			elif match_node(node, 'trk'):
				trace['tracks'].append(fetch_track(node))
	except:
		raise Exception

	return trace


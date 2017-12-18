from HTMLParser import HTMLParser
import urllib2
import urllib
import requests
from urlparse import urlparse
import uuid 
import os

image_ext = (
	".jpg",
	".jpeg",
	".png"
)

class MyHTMLParser (HTMLParser):

	def __init__ (self):
		HTMLParser.__init__(self)
		self.hrefs = [];

	def extracturl(self, attr):
		return attr[1]

	def handle_starttag(self, tag, attrs):
		for attr in attrs:
			if "href" in attr or "src" in attr:
				self.hrefs.append (self.extracturl(attr))



class MyCrawler ():
	def __init__ (self, entries):
		self.visited = []
		self.links = [(link, 0) for link in entries]
		print self.links

	def start (self):
		while len(self.links) > 0:
			tlink = self.links.pop()
			self.crawl(tlink)

	def urlopen (self, url):
		# response = urllib2.urlopen(url)
		# return response.read().decode("utf8").strip()

		try:
			r = requests.get(url)
			r.raise_for_status()
		except requests.exceptions.RequestException as e:
			print e;
			return None

		return r.text

	def getlink(self, tlink):
		return tlink[0].strip()

	def getlevel(self, tlink):
		return tlink[1]

	def maketlink(self, link, cur_level):
		return (link, (int(cur_level) + 1))

	def isimage (self, link):
		return link.lower().endswith(image_ext)

	def saveimage (self, link):
		outdir = "downloads"
		out = "{}/{}".format(outdir, "-".join([uuid.uuid4().hex[:16].upper(), os.path.basename(link)]))
		urllib.urlretrieve(link, out)

	def crawl(self, t_link):
		link = self.getlink(t_link)
		level = self.getlevel(t_link)

		if level == 4:
			return
		if link in self.visited:
			return

		self.visited.append(link)
		if self.isimage(link):
			print "image in link:\t", link
			self.saveimage(link)
			return
		if not link.startswith("http://") and not link.startswith("https://"):
			print "Weird link:\t", link
			return 

		print "Visit:\t", link
		parser = MyHTMLParser()
		data = self.urlopen(link)
		if data is None:
			print "Error Opening Link:\t", link
			return

		parser.feed(data)
		url_component = urlparse(link)
		host = "{}://{}".format(url_component.scheme, url_component.netloc)

		self.links = self.links + ([self.maketlink(href, level) for href in ["".join([host, href]) if href.startswith("/") else href for href in parser.hrefs]])




def main ():
	# dummyhtml = "<html><head><title>Hello World</title></head><body><div><a href='http://www.google.com'>Google</a><div><a href='./local/file'>Local</a></div></div></body></html>"
	# parser = MyHTMLParser()
	# parser.feed(dummyhtml)

	url = "http://javfor.me"
	crawler = MyCrawler([url])
	crawler.start()

if __name__ == '__main__':
	main()